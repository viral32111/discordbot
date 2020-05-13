// Import modules
const axios = require( "axios" )
const tmp = require( "tmp" )
const fs = require( "fs" )

// Download a file from the Internet
// i dont even need this anymore :c
async function downloadWebFile( webURL, localPath = null ) {
	// Check if no local path was provided
	if ( localPath === null ) {
		// Create a new temporary file path
		const tempFilePath = tmp.tmpNameSync( {
			prefix: "dl_",
			postfix: ".bin"
		} )

		// Update the local path with the temporary path
		localPath = tempFilePath
	}

	// Make the request to download the file
	const response = await axios.get( webURL )

	// Write the file to the local path
	fs.writeFile( localPath, response.data, {
		encoding: null, // Disable UTF-8 encoding since its raw bytes
		mode: 0o644 // Set proper file permissions
	}, function( err ) {
		if ( err ) throw err
	} )

	// Return the local path
	return localPath
}

// Expose functions
module.exports.downloadWebFile = downloadWebFile