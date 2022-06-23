// Import from native modules
import { format } from "util"
import { EventEmitter, once } from "events"
import { connect, TLSSocket } from "tls"
import { URL } from "url"
import { randomBytes, createHash } from "crypto"

// Import from other scripts
import { OperationCode, CloseCode } from "./codes.js"
import { APPLICATION_NAME, APPLICATION_VERSION, CONTACT_WEBSITE, CONTACT_EMAIL } from "../config.js"

// The unique identifier to append to key checksums (see RFC 6455, section 1.3)
const KEY_SUFFIX = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

// This is a limited implementation of the WebSocket protocol.
// https://www.rfc-editor.org/rfc/rfc6455.html

export class WebSocket extends EventEmitter {

	// Full URL of the server
	private connectionUrl: URL
	
	// The underlying connection
	private socket: TLSSocket

	// Becomes true once the HTTP upgrade has completed
	private isUpgraded = false

	// Holds the currently received data in case of TCP fragmentation
	private incompleteData?: Buffer

	// Properties to be used in, or from, the closing handshake
	private closeCode?: CloseCode
	private closeReason?: string

	// Connects to a specified websocket URL
	constructor( url: string ) {

		// Initalise the base class
		super()

		// Parse the server URL
		this.connectionUrl = new URL( url )

		// Do not continue if this is not a secure server (as we are only using TLS below)
		if ( this.connectionUrl.protocol !== "wss" ) throw Error( "Only compatible with wss:// URLs" )

		// Connect to the server on the standard HTTPS port
		this.socket = connect( {
			host: this.connectionUrl.hostname,
			port: 443,
			servername: this.connectionUrl.hostname // Use SNI
		} )

		// Register event handlers to methods on this class
		this.socket.once( "secureConnect", this.onSecureConnect.bind( this ) )
		this.socket.on( "data", this.onData.bind( this ) )
		this.socket.on( "close", this.onClose.bind( this ) )

		// Register event handlers to forward errors
		this.socket.on( "timeout", () => this.emit( "error", Error( "Timed out attempting to connect" ) ) )
		this.socket.on( "error", ( error: Error ) => this.emit( "error", error ) )

	}

	// Disconnects the websocket with an optional code and reason
	public async close( code: CloseCode = CloseCode.Normal, reason?: string ) {

		// Has the HTTP upgrade happened?
		if ( this.isUpgraded === true ) {

			// Update properties so they can be checked in the handshake
			this.closeCode = code
			this.closeReason = reason

			// Create the close frame using the provided code and reason
			const data = Buffer.alloc( reason ? 2 + reason.length : 2 )
			data.writeUInt16BE( code, 0 )
			if ( reason ) data.write( reason, 2 )
	
			// Send the close frame
			await this.sendFrame( OperationCode.Close, data )

		// Close the underlying socket if the upgrade has not happened
		} else {
			this.socket.end()
		}

	}

	// Sends a specified type of websocket frame with data
	public async sendFrame( operationCode: OperationCode, data: Buffer ) {
		
		// Do not continue if the HTTP upgrade has not happened yet
		if ( this.isUpgraded !== true ) return this.emit( "error", Error( "Connection must be open to send a frame" ) )

		let byteOffset = 0

		const frame = Buffer.alloc( data.length <= 125 ? 6 + data.length : 8 + data.length )

		byteOffset = frame.writeUInt8( 0b10000000 + 0b00000000 + operationCode, byteOffset )

		if ( data.length <= 125 ) {
			byteOffset = frame.writeUInt8( 0b10000000 + data.length, byteOffset )
		} else if ( data.length <= 65535 ) {
			byteOffset = frame.writeUInt8( 0b10000000 + 126, byteOffset )
			byteOffset = frame.writeUInt16BE( data.length, byteOffset )
		} else {
			byteOffset = frame.writeUInt8( 0b10000000 + 127, byteOffset )
			byteOffset = frame.writeBigUInt64BE( BigInt( data.length ), byteOffset )
		}

		const key = randomBytes( 4 )
		byteOffset += key.copy( frame, byteOffset )

		for ( let i = 0; i < data.length; i++ ) byteOffset = frame.writeUInt8( data.readUInt8( i ) ^ key[ i % 4 ], byteOffset )

		this.socket.write( frame )
	}

	private async handleFrame( operationCode: OperationCode, data: Buffer ) {
		if ( operationCode === OperationCode.Text ) {
			this.emit( "text", data.toString() )

		} else if ( operationCode === OperationCode.Binary ) {
			this.emit( "binary", data )

		} else if ( operationCode === OperationCode.Close ) {
			const closeCode = data.readUInt16BE( 0 )
			const closeReason = ( data.length > 2 ? data.subarray( 2, data.length ).toString() : null )

			if ( !this.closeCode ) return this.sendFrame( OperationCode.Close, data.subarray( 0, 2 ) )

			if ( closeCode !== this.closeCode ) return this.emit( "error", Error( "Mismatching close code in close frame" ) )

			this.closeCode = closeCode
			this.closeReason = closeReason ?? this.closeReason

			this.socket.end()

		} else {
			return this.emit( "error", Error( "Unknown operation code" ) )
		}
	}

	private async onSecureConnect() {
		const key = randomBytes( 16 ).toString( "base64" )
		const keyHash = createHash( "sha1" ).update( key.concat( KEY_SUFFIX ), "binary" ).digest( "base64" )

		const request = [ format( "GET %s HTTP/1.1", this.connectionUrl.pathname ) ]

		for ( const [ name, value ] of Object.entries( {
			"Accept": "*/*",
			"Host": this.connectionUrl.host,
			"Origin": format( "%s://%s", this.connectionUrl.protocol, this.connectionUrl.host ),
			"Connection": "Upgrade",
			"Upgrade": "websocket",
			"Sec-WebSocket-Key": key,
			"Sec-WebSocket-Version": 13,
			"From": CONTACT_EMAIL,
			"User-Agent": format( "%s/%s (%s; %s)", APPLICATION_NAME, APPLICATION_VERSION, CONTACT_WEBSITE, CONTACT_EMAIL )
		} ) ) request.push( format( "%s: %s", name, value ) )

		this.socket.write( request.join( "\r\n" ).concat( "\r\n\r\n" ) )

		const [ response ] = await once( this, "upgrade" )

		const lines = response.split( "\r\n" )

		if ( lines[ 0 ].startsWith( "HTTP/1.1 101 Switching Protocols" ) !== true ) return this.emit( "error", Error( "Upgrade request not satisfied" ) )

		for ( const line in lines.slice( 1 ) ) {
			const [ key, value ] = line.split( ": ", 2 )

			if ( !key || !value ) continue

			switch ( key.toLowerCase() ) {
				case "sec-websocket-accept": {
					if ( value !== keyHash ) return this.emit( "error", Error( "Invalid websocket key confirmation" ) )
				}

				case "connection": {
					if ( value.toLowerCase() !== "upgrade" ) return this.emit( "error", Error( "Upgrade request denied" ) )
				}

				case "upgrade": {
					if ( value.toLowerCase() !== "websocket" ) return this.emit( "error", Error( "Upgrade request denied" ) )
				}
			}
		}

		this.isUpgraded = true

		this.emit( "open" )
	}


	private onData( data: Buffer ) {
		if ( data.includes( "HTTP/1.1" ) === true && this.isUpgraded === false ) return this.emit( "upgrade", data.toString() )

		if ( this.incompleteData ) {
			data = Buffer.concat( [ this.incompleteData, data ] )
			this.incompleteData = undefined
		}

		do {
			let byteOffset = 0

			const header = data.readUInt8( byteOffset )
			const isFinalFrame = ( header >>> 7 ) & 0x01
			const operationCode: OperationCode = header & 0x0F
			byteOffset += 1

			let payloadLength = data.readUInt8( byteOffset ) & 0x7F
			byteOffset += 1

			if ( payloadLength === 126 ) {
				payloadLength = data.readUInt16BE( byteOffset )
				byteOffset += 2
			} else if ( payloadLength === 127 ) {
				payloadLength = Number( data.readBigUInt64BE( byteOffset ) )
				byteOffset += 8
			}

			// This packet doesn't contain everything (yet)
			if ( ( byteOffset + payloadLength ) > data.length ) {
				this.incompleteData = data
				break
			}

			const payload = Buffer.alloc( payloadLength )
			data.copy( payload, 0, byteOffset, byteOffset + payloadLength )
			byteOffset += payloadLength

			if ( isFinalFrame === 0 ) return this.emit( "error", Error( "Message fragmentation is not supported" ) )

			this.handleFrame( operationCode, payload )

			// Split packet because it may contain more than one frame
			data = data.subarray( byteOffset, data.length )
		} while ( data.length > 0 )
	}

	private async onClose() {
		this.emit( "close", this.closeCode, this.closeReason )
	}
}
