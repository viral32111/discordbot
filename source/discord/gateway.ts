// Import from native modules
import { URL } from "url"

// Import from my scripts
import { request } from "./api.js"
import { WebSocket } from "../websocket/client.js"
import { DISCORD_API_VERSION } from "../config.js"
import { CloseCode } from "../websocket/codes.js"

// An implementation of the Discord Gateway.
// https://discord.com/developers/docs/topics/gateway

export class Gateway extends WebSocket {

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
		const connectionMetadata = await request( "gateway/bot" )

		// Return a new gateway object using the websocket URL from the metadata
		return new Gateway( connectionMetadata[ "url" ] )

	}

	private onWebSocketOpen() {
		console.log( "Opened!" )
	}

	private onWebSocketClose( code: CloseCode, reason?: string ) {
		console.log( "Closed:", code, reason )
	}

	private onWebSocketText( message: string ) {
		console.log( "Message:", message )
	}

}
