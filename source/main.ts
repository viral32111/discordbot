// Import from my scripts
import { Gateway } from "./discord/gateway/gateway.js"

// Try to import environment variables from the .env file
try {
	await import( "dotenv/config" )
} catch ( error ) {
	console.log( "Failed to import environment variables for development." )
}

// Do not continue if no bot token is present
if ( !process.env[ "BOT_TOKEN" ] ) throw Error( "No bot token present in environment variables" )

// DEBUGGING
const bot = await Gateway.create()

bot.once( "error", ( error: Error ) => {
	console.error( "oh no", error.message )
	process.exit( 1 )
} )
