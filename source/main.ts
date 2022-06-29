// Import from native modules
import { readFile } from "fs/promises"

// Import from my scripts
import { Gateway } from "./discord/gateway/gateway.js"
import { ActivityType, StatusType } from "./discord/gateway/types.js"
import { CloseCode } from "./websocket/types.js"

// Attempt to add variables from the .env file to the environment
try {

	// Read the file
	const fileContent = await readFile( ".env", "utf8" )

	// Split the file by each line
	const fileLines = fileContent.split( /\r?\n/ )

	// Loop over each line, split into key-value pairs, then add them to the environment if they are valid
	fileLines.forEach( ( line ) => {
		const [ key, value ] = line.split( "=", 2 )

		if ( key ) process.env[ key ] = value
	} )

// Display a message and continue if we fail to read the file
// NOTE: This is for when running in a Docker container as the variables should already be in the environment
} catch ( error ) {
	console.log( "Failed to add development variables into the environment." )
}

// Do not continue if no bot token is present
if ( !process.env[ "BOT_TOKEN" ] ) throw Error( "No bot token present in environment variables" )

// Create a new Discord gateway instance
const bot = await Gateway.create( StatusType.Online, {
	name: "Hello World!",
	type: ActivityType.Playing
} )
console.log( "Connecting..." )

// When the websocket connection has opened
bot.once( "open", () => {
	console.log( "Open!" )
} )

// When an error occured
bot.once( "error", ( error: Error ) => {

	// Display the error message
	console.error( error.message )

	// Gracefully close the connection
	bot.close( CloseCode.Normal, "Internal error" )

} )

// Called whenever a keyboard interrupt/exit signal happens
function onRequestExit() {

	// Display a message and gracefully close the connection
	console.log( "Closing..." )
	bot.close( CloseCode.Normal, "Application exit" )

}

// Call the above function for these exit signals
process.once( "SIGTERM", onRequestExit ) // Docker
process.once( "SIGINT", onRequestExit ) // Windows & Linux Terminals
