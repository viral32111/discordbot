import { setTimeout } from "timers/promises"

import { request } from "./discord/api.js"
import { WebSocket } from "./websocket/client.js"
import { OperationCode } from "./websocket/codes.js"

try {
	await import( "dotenv/config" )
} catch ( error ) {
	console.log( "Failed to import environment variables for development." )
}

if ( !process.env[ "BOT_TOKEN" ] ) throw Error( "No bot token present in environment variables" )

const gatewayConnectionData = await request( "gateway/bot" )
console.log( gatewayConnectionData[ "url" ] )

const wsClient = new WebSocket( "wss://echo.websocket.events" ) // gatewayConnectionData[ "url" ]

wsClient.once( "open", async () => {
	console.log( "Connection opened" )

	await wsClient.sendFrame( OperationCode.Text, Buffer.from( "Hello World :)" ) )
} )

wsClient.once( "close", () => {
	console.log( "Connection closed" )
} )

wsClient.once( "error", ( error: Error ) => {
	console.error( "Error: ", error.message )
} )

wsClient.on( "text", async ( message: string ) => {
	console.log( "Received: ", message )

	await setTimeout( 1000 )

	await wsClient.sendFrame( OperationCode.Text, Buffer.from( "Thank you" ) )
} )
