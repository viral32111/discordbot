// Import from native modules
import { format } from "util"
import { EventEmitter, once } from "events"
import { connect, TLSSocket } from "tls"
import { URL } from "url"
import { randomBytes, createHash } from "crypto"

// Import from my scripts
import { OperationCode, CloseCode } from "./types.js"
import { APPLICATION_NAME, APPLICATION_VERSION, CONTACT_WEBSITE, CONTACT_EMAIL } from "../config.js"

// This is a limited implementation of the WebSocket protocol.
// https://www.rfc-editor.org/rfc/rfc6455.html

// The unique identifier to append to key checksums
// https://www.rfc-editor.org/rfc/rfc6455.html#section-1.3
const KEY_SUFFIX = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

// Class to encapsulate everything
export class WebSocket extends EventEmitter {

	// Full URL to the remote server
	private connectionUrl: URL

	// The underlying secure connection
	private socket?: TLSSocket

	// Becomes true once the HTTP upgrade has completed
	private isUpgraded = false

	// Holds the currently received data in case of TCP fragmentation
	private incompleteData?: Buffer

	// Properties to be used in, or from, the closing handshake
	private closeCode?: CloseCode | number
	private closeReason?: string

	// Instansiate to connect to a WebSocket server
	constructor( url: URL ) {

		// Initialise the base class
		super()

		// Do not continue if this is not a secure server (as we are only using TLS)
		if ( url.protocol !== "wss:" ) throw Error( "Only compatible with wss:// URLs" )

		// Update the class property
		this.connectionUrl = url

		// Start the connection
		this.open()

	}

	public open() {

		// Connect to the server on the standard HTTPS port
		this.socket = connect( {
			host: this.connectionUrl.hostname,
			port: 443,
			servername: this.connectionUrl.hostname // Use SNI
		} )

		// Register event handlers for the underlying TLS socket to methods on this class
		this.socket.once( "secureConnect", this.onSocketSecureConnect.bind( this ) )
		this.socket.once( "close", this.onSocketClose.bind( this ) )
		this.socket.on( "data", this.onSocketData.bind( this ) )

		// Register event handlers to forward errors
		this.socket.on( "timeout", () => this.emit( "error", Error( "Timed out attempting to connect" ) ) )
		this.socket.on( "error", ( error: Error ) => this.emit( "error", error ) )

	}

	// Disconnects the websocket with an optional code and reason
	public close( code: CloseCode = CloseCode.Normal, reason?: string ) {

		// Do not continue if the underlying socket has not established a connection yet
		if ( !this.socket || this.socket.readyState !== "open" ) throw Error( "Cannot close a connection that is not open" )

		// Has the HTTP upgrade happened?
		if ( this.isUpgraded === true ) {

			// Update properties so they can be checked in the handshake
			this.closeCode = code
			this.closeReason = reason

			// Create the close payload using the provided code and reason
			const payload = Buffer.alloc( reason ? 2 + reason.length : 2 )
			payload.writeUInt16BE( code, 0 )
			if ( reason ) payload.write( reason, 2 )
	
			// Send the close frame
			this.sendFrame( OperationCode.Close, payload )

		// Close the underlying socket if the upgrade has not happened
		} else {
			this.socket.end()
		}

	}

	// Checks if the underlying socket is connected and we are upgraded to websocket
	public isConnected(): boolean {
		return ( this.socket !== undefined && this.socket.readyState === "open" && this.isUpgraded )
	}

	// Sends a specified type of websocket frame with a payload
	public sendFrame( operationCode: OperationCode, payload: Buffer ) {

		// Do not continue if the underlying socket has not established a connection yet
		if ( !this.socket || this.socket.readyState !== "open" ) throw Error( "Cannot send a frame on a connection that is not open" )

		// Do not continue if the HTTP upgrade has not happened yet
		if ( this.isUpgraded !== true ) throw Error( "Connection must be open to send a frame" )

		// Holds the current byte position within the payload
		let byteOffset = 0

		// Allocate a buffer for the new frame (extra two bytes are for >8-bit integers)
		const frame = Buffer.alloc( payload.length <= 125 ? 6 + payload.length : 8 + payload.length )

		// Add the header
		// 1 bit for final message flag, 3 bits for reserved, 4 bits for opcode
		byteOffset = frame.writeUInt8( 0b10000000 + 0b00000000 + operationCode, byteOffset )

		// Add the mask flag (1 bit), and payload length (7 bits) as either a 8-bit, 16-bit, or 64-bit integer
		if ( payload.length <= 125 ) {
			byteOffset = frame.writeUInt8( 0b10000000 + payload.length, byteOffset )
		} else if ( payload.length <= 65535 ) {
			byteOffset = frame.writeUInt8( 0b10000000 + 126, byteOffset ) // Payload length as 126 to indicate 16-bit length follows
			byteOffset = frame.writeUInt16BE( payload.length, byteOffset )
		} else {
			byteOffset = frame.writeUInt8( 0b10000000 + 127, byteOffset ) // Payload length as 127 to indicate 64-bit length follows
			byteOffset = frame.writeBigUInt64BE( BigInt( payload.length ), byteOffset )
		}

		// NOTE: Masking of client messages is needed to prevent the server from mistaking frames as HTTP messages.
		// https://security.stackexchange.com/a/113306

		// Add a random key for XOR masking
		const key = randomBytes( 4 )
		byteOffset += key.copy( frame, byteOffset )

		// Mask and add the data to send using the key
		for ( let position = 0; position < payload.length; position++ ) byteOffset = frame.writeUInt8( payload.readUInt8( position ) ^ key[ position % 4 ], byteOffset )

		// Send the frame
		this.socket.write( frame )

	}

	// Runs our events based on type of frame received
	private handleFrame( operationCode: OperationCode, payload: Buffer ) {

		// Do not continue if the underlying socket has not established a connection yet
		// NOTE: This is just to stop TypeScript complaining, obviously by the time this event is called the socket would be open!
		if ( !this.socket || this.socket.readyState !== "open" ) return this.emit( "error", Error( "Cannot handle a frame on a connection that is not open" ) )

		// Run the text event for plaintext messages
		if ( operationCode === OperationCode.Text ) {
			this.emit( "text", payload.toString() )

		// Run the binary event for raw messages
		} else if ( operationCode === OperationCode.Binary ) {
			this.emit( "binary", payload )

		// If the frame is connection close...
		} else if ( operationCode === OperationCode.Close ) {

			// Store the included close code and optional reason
			const closeCode = payload.readUInt16BE( 0 )
			const closeReason = ( payload.length > 2 ? payload.subarray( 2, payload.length ).toString() : null )

			// If we did not request this close...
			if ( !this.closeCode ) {

				// Update the close handshake properties for use in the underlying socket close event
				this.closeCode = closeCode
				this.closeReason = closeReason ?? this.closeReason

				// Reply with the same close code to acknowledge
				this.sendFrame( OperationCode.Close, payload.subarray( 0, 2 ) )

			// If we did request this close...
			} else {

				// Error if the code in the acknowledgement response is not the same as what we requested
				if ( closeCode !== this.closeCode ) return this.emit( "error", Error( "Mismatching close code in close frame" ) )

				// Update the close handshake properties for use in the underlying socket close event
				this.closeCode = closeCode
				this.closeReason = closeReason ?? this.closeReason

			}

			// Disconnect the underlying socket
			this.socket.end()

		// Error if it is any other operation code
		} else {
			return this.emit( "error", Error( "Unknown operation code" ) )
		}

	}

	// Event that runs when the underlying socket has established a TLS connection to the remote server
	private async onSocketSecureConnect() {

		// Do not continue if the underlying socket has not established a connection yet
		// NOTE: This is just to stop TypeScript complaining, obviously by the time this event is called the socket would be open!
		if ( !this.socket || this.socket.readyState !== "open" ) return this.emit( "error", Error( "Cannot continue on a connection that is not open" ) )

		// Generate a random key, and hash it with the key suffix
		const key = randomBytes( 16 ).toString( "base64" )
		const keyHash = createHash( "sha1" ).update( key.concat( KEY_SUFFIX ), "binary" ).digest( "base64" )

		// Create an array to hold the lines of our HTTP upgrade request, starting with a GET request
		const request = [ format( "GET %s HTTP/1.1", this.connectionUrl.pathname ) ]

		// Add custom headers to the upgrade request
		for ( const [ name, value ] of Object.entries( {
			"Accept": "*/*", // What content type does an upgrade return, if any?
			"Host": this.connectionUrl.host,
			"Origin": format( "%s//%s", this.connectionUrl.protocol, this.connectionUrl.host ),
			"Connection": "Upgrade",
			"Upgrade": "websocket",
			"Sec-WebSocket-Key": key,
			"Sec-WebSocket-Version": 13,
			"From": CONTACT_EMAIL,
			"User-Agent": format( "%s/%s (%s; %s)", APPLICATION_NAME, APPLICATION_VERSION, CONTACT_WEBSITE, CONTACT_EMAIL )
		} ) ) request.push( format( "%s: %s", name, value ) )

		// Join the HTTP upgrade request lines and send it to the server
		this.socket.write( request.join( "\r\n" ).concat( "\r\n\r\n" ) )

		// Wait for a response...
		const [ response ] = await once( this, "upgrade" )

		// Split up the response into seperate lines
		const lines = response.split( "\r\n" )

		// Error if the first line is not HTTP 101
		if ( lines[ 0 ].startsWith( "HTTP/1.1 101 Switching Protocols" ) !== true ) return this.emit( "error", Error( "Upgrade request not satisfied" ) )

		// Loop through the rest of the lines (should be headers)...
		for ( const line in lines.slice( 1 ) ) {

			// Split the header up into name and value
			const [ key, value ] = line.split( ": ", 2 )
			if ( !key || !value ) continue // Skip if header is invalid

			// Match each header name...
			switch ( key.toLowerCase() ) {

				// Error if the returned key hash does not match our one
				case "sec-websocket-accept": {
					if ( value !== keyHash ) return this.emit( "error", Error( "Invalid websocket key confirmation" ) )
				}

				// Error if the returned upgrade headers do not match those for a websocket upgrade
				case "connection": {
					if ( value.toLowerCase() !== "upgrade" ) return this.emit( "error", Error( "Upgrade request denied" ) )
				}
				case "upgrade": {
					if ( value.toLowerCase() !== "websocket" ) return this.emit( "error", Error( "Upgrade request denied" ) )
				}

			}

		}

		// At this point we have successfully upgraded and started a websocket connection
		this.isUpgraded = true
		this.emit( "open" )

	}

	// Event that runs when the underlying socket has disconnected
	private onSocketClose() {

		// Run our close event using the close code and reason we requested or received
		this.emit( "close", this.closeCode, this.closeReason )

	}

	// Event that runs when the underlying socket has received a packet
	private onSocketData( data: Buffer ) {

		// Run our upgrade event if the data starts with a HTTP message identifier and the upgrade has not happened yet
		if ( data.includes( "HTTP/1.1" ) === true && this.isUpgraded === false ) return this.emit( "upgrade", data.toString() )

		// If there was data left over from last time then prepend it onto this data and clear it
		if ( this.incompleteData ) {
			data = Buffer.concat( [ this.incompleteData, data ] )
			this.incompleteData = undefined
		}

		// Loop until no bytes are left (packet split happens at the end)
		do {

			// Holds the current byte position in the data
			let byteOffset = 0

			// Read the header's final frame flag (1 bit) and operation code (4 bits)
			const header = data.readUInt8( byteOffset )
			const isFinalFrame = ( header >>> 7 ) & 0x01
			const operationCode: OperationCode = header & 0x0F
			byteOffset += 1

			// Error if the final frame flag is not set
			if ( isFinalFrame === 0 ) return this.emit( "error", Error( "Message fragmentation is not supported" ) )

			// Read the payload length (7 bits)
			// NOTE: This ignores the mask flag (1 bit) as it is not used for server to client messages
			let payloadLength = data.readUInt8( byteOffset ) & 0x7F
			byteOffset += 1

			// If the payload length is 16-bit or 64-bit then read the bytes that follow
			if ( payloadLength === 126 ) {
				payloadLength = data.readUInt16BE( byteOffset )
				byteOffset += 2
			} else if ( payloadLength === 127 ) {
				payloadLength = Number( data.readBigUInt64BE( byteOffset ) )
				byteOffset += 8
			}

			// Stop & store the current packet for the next event call if the payload length is greater than the amount of bytes remaining
			if ( ( byteOffset + payloadLength ) > data.length ) {
				this.incompleteData = data
				break
			}

			// Extract the frame payload
			const payload = data.subarray( byteOffset, byteOffset + payloadLength )
			byteOffset += payloadLength

			// Run the frame handler method
			this.handleFrame( operationCode, payload )

			// Split the remainder of the packet as it may contain additional frames
			data = data.subarray( byteOffset, data.length )

		} while ( data.length > 0 )

	}

}
