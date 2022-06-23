import { format } from "util";
import { request as sendHttpsRequest } from "https";

import { APPLICATION_NAME, APPLICATION_VERSION, CONTACT_WEBSITE, CONTACT_EMAIL, DISCORD_API_URL } from "../config.js";

export function request( endpoint: string, method: string = "GET" ): Promise<any> {
	const request = sendHttpsRequest( format( "https://%s/%s", DISCORD_API_URL, endpoint ), {
		method: method,
		headers: {
			"Accept": "application/json",
			"Authorization": format( "Bot %s", process.env[ "BOT_TOKEN" ] ),
			"User-Agent": format( "%s/%s (%s; %s)", APPLICATION_NAME, APPLICATION_VERSION, CONTACT_WEBSITE, CONTACT_EMAIL )
		}
	} )

	console.debug( request.method, request.protocol, request.host, request.path )

	return new Promise( ( resolve, reject ) => {
		request.once( "response", ( response ) => {
			response.setEncoding( "utf8" )

			console.debug( response.statusCode, response.statusMessage, response.headers )
	
			const chunks: string[] = []
			response.on( "data", chunk => chunks.push( chunk ) )

			response.once( "end", () => {
				if ( !response.headers[ "content-type" ]?.startsWith( "application/json" ) ) reject( Error( "Did not receive a JSON response" ) )

				resolve( JSON.parse( chunks.join( "" ) ) )
			} )
		} )

		request.once( "error", reject )
	
		request.end()
	} )
}
