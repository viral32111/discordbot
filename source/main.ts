// Import from native modules
import { readFile } from "fs/promises"

// Import from my scripts
import { Gateway } from "./discord/gateway/gateway.js"

// Attempt to add variables from the .env file to the environment
try {
	const fileContent = await readFile( ".env", "utf8" )

	const fileLines = fileContent.split( /\r?\n/ )

	fileLines.forEach( ( line ) => {
		const [ key, value ] = line.split( "=", 2 )

		if ( key ) process.env[ key ] = value
	} )
} catch ( error ) {
	console.log( "Failed to add development variables into the environment." )
}

// Do not continue if no bot token is present
if ( !process.env[ "BOT_TOKEN" ] ) throw Error( "No bot token present in environment variables" )

// DEBUGGING
const bot = await Gateway.create()

bot.on( "error", ( error: Error ) => {
	console.error( "oh no", error.message )
	// TODO: Graceful disconnect
	// this.close( CloseCode.Normal, "Internal error occured" )
	process.exit( 1 )
} )
