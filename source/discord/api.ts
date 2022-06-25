// Import from native modules
import { format } from "util";
import { request as createHttpsRequest } from "https";

// Import from my scripts
import { APPLICATION_NAME, APPLICATION_VERSION, CONTACT_WEBSITE, CONTACT_EMAIL, DISCORD_API_URL, DISCORD_API_VERSION } from "../config.js";

// Sends a request to the Discord API and returns a JSON object
export function request( endpoint: string, method: string = "GET" ): Promise<any> {

	// Create a HTTP request to the specified endpoint using the specified method
	const request = createHttpsRequest( format( "https://%s/v%s/%s", DISCORD_API_URL, DISCORD_API_VERSION, endpoint ), {
		method: method,
		headers: {
			"Accept": "application/json", // Expect a JSON response
			"Authorization": format( "Bot %s", process.env[ "BOT_TOKEN" ] ), // Authenticate as the bot
			"User-Agent": format( "%s/%s (%s; %s)", APPLICATION_NAME, APPLICATION_VERSION, CONTACT_WEBSITE, CONTACT_EMAIL )
		}
	} )

	// Return a promise that resolves when a valid response is received
	return new Promise( ( resolve, reject ) => {
		
		// When a response is received...
		request.once( "response", ( response ) => {

			// Set the encoding so text is provided in the data event
			response.setEncoding( "utf8" )

			// Create and populate an array of strings containing the response body
			const chunks: string[] = []
			response.on( "data", ( chunk ) => chunks.push( chunk ) )

			// When all of the response body has been received...
			response.once( "end", () => {

				// Reject the promise if the response content is not JSON
				if ( !response.headers[ "content-type" ]?.startsWith( "application/json" ) ) reject( Error( "Did not receive a JSON response" ) )

				// Resolve the promise with the parsed JSON object
				resolve( JSON.parse( chunks.join( "" ) ) )

			} )

		} )

		// Reject the promise if an error occurs
		request.once( "error", reject )
	
		// Send the HTTP request
		request.end()

	} )
}
