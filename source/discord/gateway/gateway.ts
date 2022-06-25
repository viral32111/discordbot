// Import from native modules
import { URL } from "url"
import { setTimeout } from "timers/promises"
import { once } from "events"

// Import from my scripts
import { request } from "../api.js"
import { WebSocket } from "../../websocket/websocket.js"
import { DISCORD_API_VERSION } from "../../config.js"
import { OperationCode as WSOperationCode, CloseCode } from "../../websocket/types.js"
import { Get, Payload, OperationCode } from "./types.js"

// An implementation of the Discord Gateway.
// https://discord.com/developers/docs/topics/gateway

export class Gateway extends WebSocket {

	// Holds the current payload sequence number, used when sending heartbeats
	private sequenceNumber: number | null = null

	// Instansiate to connect to a provided gateway server
	constructor( baseUrl: string ) {

		// Parse the provided URL & add the required querystring to it
		// https://discord.com/developers/docs/topics/gateway#connecting-to-the-gateway
		const connectionUrl = new URL( baseUrl )
		connectionUrl.search = new URLSearchParams( {
			"encoding": "json",
			"v": DISCORD_API_VERSION
		} ).toString()

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

		// TODO: Disconnect and retry after a short time
		if ( !isAcknowledged ) this.emit( "error", Error( "Never received heartbeat acknowledgement" ) )
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

	// Event that runs when the underlying websocket connection opens
	private onWebSocketOpen() {
		
		// DEBUGGING
		console.log( "Opened!" )

	}

	// Event that runs when the underlying websocket connection closes
	private onWebSocketClose( code: CloseCode, reason?: string ) {
	
		// DEBUGGING
		console.log( "Closed:", code, reason )

	}

	// Event that runs when the underlying websocket receives a plaintext message
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
			this.startHeartbeating( payload.d[ "heartbeat_interval" ] ) // const heartbeatPromise =

		} else if ( payload.op == OperationCode.HeartbeatAcknowledgement ) {
			console.log( "Received heartbeat acknowledgement!" )
			this.emit( "heartbeatAcknowledge", true )
		
		} else if ( payload.op == OperationCode.Heartbeat ) {
			console.log( "Gateway requested a heartbeat" )
			await this.sendHeartbeat()

		} else {
			this.emit( "error", Error( "Unknown gateway operation code" ) )
		}

	}

}
