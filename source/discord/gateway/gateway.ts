// Import from native modules
import { URL } from "url"
import { setTimeout } from "timers/promises"
import { once } from "events"

// Import from my scripts
import { request } from "../api.js"
import { WebSocket } from "../../websocket/websocket.js"
import { APPLICATION_NAME, DISCORD_API_VERSION } from "../../config.js"
import { OperationCode as WSOperationCode, CloseCode } from "../../websocket/types.js"
import { Get, Payload, OperationCode, ActivityType, StatusType, DispatchEvent } from "./types.js"

// An implementation of the Discord Gateway.
// https://discord.com/developers/docs/topics/gateway

// The non-1000 WebSocket close code to use for resuming after not receiving a heartbeat acknowledgement
const RECONNECT_CLOSE_CODE = 4000

// Should compression be used? No it should not
const USE_COMPRESSION = false

export class Gateway extends WebSocket {

	// Holds the current payload sequence number, used when sending heartbeats
	private sequenceNumber: number | null = null

	// For periodic heartbeating in the background
	private heartbeatTask?: Promise<void>
	private heartbeatController = new AbortController()

	// Session identifier from the Ready event
	private sessionIdentifier?: string

	// Instansiate to connect to a provided gateway server
	constructor( baseUrl: string ) {

		// Parse the provided URL & add the required querystring to it
		// https://discord.com/developers/docs/topics/gateway#connecting-to-the-gateway
		const connectionUrl = new URL( baseUrl )
		connectionUrl.search = new URLSearchParams( {
			"encoding": "json",
			"compress": USE_COMPRESSION.toString(),
			"v": DISCORD_API_VERSION.toString()
		} ).toString()

		console.log( connectionUrl.toString() )

		// Initialise the base class with the URL above
		super( connectionUrl )

		// Register event handlers for the underlying websocket to methods on this class
		this.once( "open", this.onWebSocketOpen.bind( this ) )
		this.once( "close", this.onWebSocketClose.bind( this ) )
		this.on( "text", this.onWebSocketText.bind( this ) )

	}

	// Use this to instansiate, unless you want to provide your own gateway URL
	public static async create(): Promise<Gateway> {

		// Fetch the gateway metadata for bots
		const metadata: Get = await request( "gateway/bot" )

		// Return a new gateway object using the websocket URL from the metadata
		return new Gateway( metadata.url )

	}

	private send( code: OperationCode, data: any ) {
		this.sendFrame( WSOperationCode.Text, Buffer.from( JSON.stringify( {
			"op": code,
			"d": data
		} ) ) )
	}

	private async sendHeartbeat() {
		console.log( "Sending heartbeat with sequence number:", this.sequenceNumber )

		this.send( OperationCode.Heartbeat, this.sequenceNumber )

		const isAcknowledged = await Promise.race( [
			once( this, "heartbeatAcknowledge" ),
			setTimeout( 5000, false ) // { signal: this.heartbeatController.signal }
		] )

		console.log( "Heartbeat acknowledgement:", isAcknowledged )

		// If we never receive an acknowledgement, then the connection may be zombied.
		// We should disconnect with a non-1000 close code, reconnect and attempt to send Resume (Opcode 6)

		if ( !isAcknowledged ) {

			console.log( "Never received heartbeat acknowledgement, connection might be zombied!" )
			this.close( RECONNECT_CLOSE_CODE, "Never received heartbeat acknowledgement" )

			// Continues in onWebSocketClose...
		}
	}

	private async startHeartbeating( interval: number ) {
		console.log( "Starting to send heartbeats every:", interval, "ms" )

		let sentInitialBeat = false

		while ( this.isConnected() ) {
			console.log( "Waiting to send heartbeat..." )

			try {
				if ( sentInitialBeat === false ) {
					await setTimeout( interval * Math.random(), undefined, {
						signal: this.heartbeatController.signal
					} )
	
					sentInitialBeat = true
				} else {
					await setTimeout( interval, undefined, {
						signal: this.heartbeatController.signal
					} )
				}
			} catch ( exception ) {
				if ( exception instanceof Error ) {
					console.error( exception.message )
				}

				break
			}
			

			if ( this.heartbeatController.signal.aborted ) break

			await this.sendHeartbeat()
		}

		console.log( "Finished sending heartbeats" )
	}

	// Event that runs when the underlying websocket connection has opened
	private onWebSocketOpen() {
		
		// DEBUGGING
		console.log( "Opened!" )

	}

	// Event that runs when the underlying websocket connection has closed
	private async onWebSocketClose( code: CloseCode | number, reason?: string ) {

		// DEBUGGING
		console.log( "Closed:", code, reason )

		// Stop heartbeating in the background
		console.log( "Stopping heartbeats..." )
		this.heartbeatController.abort()
		
		// Wait for background heartbeats to resolve...
		console.log( "Waiting for heartbeating to stop..." )
		await this.heartbeatTask
		console.log( "Done~" )

		// Cleanup so we are ready for another run
		this.heartbeatTask = undefined
		this.heartbeatController = new AbortController()

		if ( code == RECONNECT_CLOSE_CODE ) {
			console.log( "We need to reconnect!" )

			const duration = Math.floor( Math.random() * 4000 ) + 1000 // Between 1 and 5 seconds
			console.log( "Waiting", duration, "ms..." )
			await setTimeout( duration )

			console.log( "Reopening..." )
			this.open()

			// Continues in onWebSocketText...
		} else {

			// Cleanup - this should not be needed as the process will just end if there is no automatic reconnect
			this.sessionIdentifier = undefined
			this.sessionIdentifier = undefined
			this.sequenceNumber = null

		}

	}

	// Event that runs when the underlying websocket has received a plaintext message
	private async onWebSocketText( message: string ) {

		// Parse the message as a standard gateway payload
		const payload: Payload = JSON.parse( message )

		// Update the sequence number if it is valid
		if ( payload.s ) this.sequenceNumber = payload.s

		// DEBUGGING
		console.log( "\nOperation Code:", payload.op )
		console.log( "Event Data:", payload.d )
		console.log( "Sequence Number:", payload.s )
		console.log( "Event Name:", payload.t )

		if ( payload.op === OperationCode.Hello ) {
			if ( this.heartbeatTask ) return this.emit( "error", Error( "Already heartbeating?" ) )

			// Start heartbeating in the background with the interval given to us
			this.heartbeatTask = this.startHeartbeating( payload.d[ "heartbeat_interval" ] )

			// If we have a session identifier, then we should try to RESUME instead of IDENTIFY
			if ( this.sessionIdentifier !== undefined ) {
				console.log( "Resuming with session identifier:", this.sessionIdentifier, "and sequence number:", this.sequenceNumber )
				this.send( OperationCode.Resume, {
					"token": process.env[ "BOT_TOKEN" ],
					"session_id": this.sessionIdentifier,
					"seq": this.sequenceNumber
				} )

			// Identify
			} else {
				console.log( "Identifying..." )
				this.send( OperationCode.Identify, {
					"token": process.env[ "BOT_TOKEN" ],
					"intents": 32767, // Everything
					"compress": USE_COMPRESSION,
					"large_threshold": 250, // This is the max
					"presence": {
						"afk": false,
						"since": null,
						"status": StatusType.Online,
						"activities": [ {
							"name": "Hello World!",
							"type": ActivityType.Playing
						} ]
					},
					"properties": {
						"os": process.platform,
						"browser": APPLICATION_NAME,
						"device": APPLICATION_NAME,
					}
				} )
			}

		} else if ( payload.op === OperationCode.HeartbeatAcknowledgement ) {
			//console.log( "Received heartbeat acknowledgement!" )
			//this.emit( "heartbeatAcknowledge", true )

		} else if ( payload.op === OperationCode.Heartbeat ) {
			console.log( "Gateway requested a heartbeat" )
			await this.sendHeartbeat()

		} else if ( payload.op === OperationCode.Reconnect ) {
			console.log( "We need to reconnect!" )
			
			if ( this.sessionIdentifier !== undefined ) {
				this.close( RECONNECT_CLOSE_CODE, "Client reconnect requested (attempt resume on reconnect)" )
			} else {
				this.close( CloseCode.GoingAway, "Client reconnect requested" )
			}

			// Continues in onWebSocketClose...
		
		} else if ( payload.op === OperationCode.InvalidSession ) {
			console.log( "Our session is invalid? Can resume:", payload.d )

			// Can we resume?...
			if ( payload.d === true ) {
				this.close( RECONNECT_CLOSE_CODE, "Session reported as invalid (attempt resume on reconnect)" )
			} else {
				this.close( CloseCode.GoingAway, "Session reported as invalid" )
			}

			// Continues in onWebSocketClose...

		} else if ( payload.op === OperationCode.Dispatch ) {

			if ( payload.t === DispatchEvent.Ready ) {

				console.log( "we're ready!!" )

				this.sessionIdentifier = payload.d[ "session_id" ]

				// .v is ALWAYS 6????

				// .user
				// .guilds
				// .application

			} else if ( payload.t === DispatchEvent.Resumed ) {
				console.log( "We have resumed!" )

			}

		} else {
			this.emit( "error", Error( "Unknown gateway operation code" ) )
		}

	}

}
