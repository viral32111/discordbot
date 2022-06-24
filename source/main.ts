// Import from my scripts
import { request } from "./discord/api.js"
import { WebSocket } from "./websocket/client.js"

// Try to import environment variables from the .env file
try {
	await import( "dotenv/config" )
} catch ( error ) {
	console.log( "Failed to import environment variables for development." )
}

// Do not continue if no bot token is present
if ( !process.env[ "BOT_TOKEN" ] ) throw Error( "No bot token present in environment variables" )

// v v v DEBUGGING v v v

const gatewayConnectionData = await request( "gateway/bot" )
console.log( gatewayConnectionData[ "url" ] )

const wsClient = new WebSocket( gatewayConnectionData[ "url" ] )

wsClient.once( "open", async () => {
	console.log( "Connection opened" )

	//wsClient.sendFrame( OperationCode.Text, Buffer.from( "Hello World :)" ) )
} )

wsClient.once( "close", () => {
	console.log( "Connection closed" )
} )

wsClient.once( "error", ( error: Error ) => {
	console.error( "Error:", error.message )
} )

wsClient.on( "text", async ( message: string ) => {
	console.log( "Received:", message )

	//await setTimeout( 1000 )

	//wsClient.sendFrame( OperationCode.Text, Buffer.from( "Thank you" ) )
} )
