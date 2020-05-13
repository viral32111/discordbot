// TODO: move this to a wrappers folder because it's just a wrapper func around an API endpoint

// Import Axios for HTTP API interaction
const axios = require( "axios" )

// we're gonna need that api key
const configBitly = require( "../config/bitly.js" )

// Create an axios instance for later reuse
const bitlyShortenAPI = axios.create( {
	url: "https://api-ssl.bitly.com/v4/shorten",
	method: "POST",
	headers: {
		"Content-Type": "application/json",
		"Authorization": "Bearer " + configBitly.apiKey,
		"Connection": "close"
	}/*, // apparently not needed since axios auto converts to json, but it doesn't set the content-type header automatically???
	transformRequest: [
		function( data, headers ) {
			return JSON.stringify( data )
		}
	]*/
} )

// Function to shorten a long URL and return the short URL
async function shortenURL( longURL, customTags = [] ) {
	// Send the API request
	const response = await bitlyShortenAPI.request( {
		data: {
			long_url: longURL,
			tags: customTags
		}
	} )

	// Return the new short URL
	return response.data.link
}

// Expose function
module.exports.shortenURL = shortenURL