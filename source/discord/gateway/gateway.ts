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

	// Background periodic heartbeating
	private heartbeatTask?: Promise<void>

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
			setTimeout( 5000, false )
		] )

		console.log( "Heartbeat acknowledgement:", isAcknowledged )

		// If we never receive an acknowledgement, then the connection may be zombied.
		// We should disconnect with a non-1000 close code, reconnect and attempt to send Resume (Opcode 6)

		if ( !isAcknowledged ) {

			this.close( RECONNECT_CLOSE_CODE )



		}
	}

	private async startHeartbeating( interval: number ) {
		console.log( "Starting to send heartbeats every:", interval, "ms" )

		let sentInitialBeat = false

		while ( this.isConnected() ) {
			if ( sentInitialBeat === false ) {
				const random = interval * Math.random()
				console.log( "Waiting", random, "ms to send initial heartbeat..." )
				await setTimeout( random )
				sentInitialBeat = true
			} else {
				console.log( "Waiting", interval, "ms to send heartbeat..." )
				await setTimeout( interval )
			}

			await this.sendHeartbeat()
		}
	}

	// Event that runs when the underlying websocket connection has opened
	private onWebSocketOpen() {
		
		// DEBUGGING
		console.log( "Opened!" )

	}

	// Event that runs when the underlying websocket connection has closed
	private onWebSocketClose( code: CloseCode | number, reason?: string ) {
	
		// DEBUGGING
		console.log( "Closed:", code, reason )

		// TODO: Stop heartbeating
		// this.heartbeatTask...

		if ( code == RECONNECT_CLOSE_CODE ) {

			// Wait a bit...
			// await setTimeout( 1000 to 5000 )...

			// TODO: Reconnect
			console.log( "Reconnecting" )
			// this.open()

			// TODO: Wait for connection to open...
			// Maybe do this in onWebSocketText() ???

			if ( this.sessionIdentifier ) {

				// TODO: Send Resume

			} else {

				console.log( "Reconnected, but cannot Resume as I do not have a session identifier" )

			}

		}

	}

	// Event that runs when the underlying websocket has received a plaintext message
	private async onWebSocketText( message: string ) {

		// Parse the message as a standard gateway payload
		const payload: Payload = JSON.parse( message )

		// Update the sequence number
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

			// Identify
			console.log( "identifying..." )
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

		} else if ( payload.op == OperationCode.HeartbeatAcknowledgement ) {
			console.log( "Received heartbeat acknowledgement!" )
			this.emit( "heartbeatAcknowledge", true )
		
		} else if ( payload.op == OperationCode.Heartbeat ) {
			console.log( "Gateway requested a heartbeat" )
			await this.sendHeartbeat()

		} else if ( payload.op == OperationCode.Dispatch ) {

			if ( payload.t === DispatchEvent.Ready ) {

				console.log( "we're ready!!" )

				this.sessionIdentifier = payload.d[ "session_id" ]

				// .v is ALWAYS 6????

				// .user
				// .guilds
				// .application

			}

		} else {
			this.emit( "error", Error( "Unknown gateway operation code" ) )
		}

	}

}
