import { request } from "./discord/api.js"

try {
	await import( "dotenv/config" )
} catch ( error ) {
	console.log( "Failed to import environment variables for development." )
}

console.debug = ( ...args ) => {
	if ( process.env[ "DEBUG" ] === "true" ) console.log( ...args )
}

if ( !process.env[ "BOT_TOKEN" ] ) throw Error( "No bot token present in environment variables" )

const gatewayConnectionData = await request( "gateway/bot" )

console.log( gatewayConnectionData[ "url" ] )
