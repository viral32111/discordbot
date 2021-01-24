<?php

/****************** Globals ******************/

// Handlers for each slash command
$commands = [

	// Ping
	'ping' => function( $data ) {
		$memberID = $data[ 'member' ][ 'user' ][ 'id' ];
		$memberName = $data[ 'member' ][ 'user' ][ 'username' ];
		$memberTag = $data[ 'member' ][ 'user' ][ 'discriminator' ];

		$commandID = $data[ 'id' ];
		$guildID = $data[ 'guild_id' ];
		$channelID = $data[ 'channel_id' ];

		$optionalMessage = ( isset( $data[ 'data' ][ 'options' ][ 0 ] ) : $data[ 'data' ][ 'options' ][ 0 ][ 'value' ] : 'No message provided.' );

		return "Pong!\n\nMember: $memberName#$memberTag (ID: `$memberID`).\nInteraction ID: `$commandID`.\nGuild ID: `$guildID`.\nChannel ID: `$channelID`.\nMessage: `$optionalMessage`.";
	}

];

// All the request headers
$requestHeaders = apache_request_headers();

// Public key for the application
$publicKey = sodium_hex2bin( '4222308ac7e60d88d5e3769ba88f9b6a939ae388fca46bfc2d19197be07eaf4d' );

/****************** Verification ******************/

// Signature, timestamp and body from the request
$signature = sodium_hex2bin( $requestHeaders[ 'x-signature-ed25519' ] );
$timestamp = $requestHeaders[ 'x-signature-timestamp' ];
$body = file_get_contents( 'php://input' );

// Stop processing with unauthorised status code if the signature is invalid
if ( !sodium_crypto_sign_verify_detached( $signature, $timestamp . $body, $publicKey ) ) {
	http_response_code( 401 );
	exit();
}

/****************** Processing ******************/

// Decode the request body and create empty array for the response
$payload = json_decode( $body, true );
$response = [];

// We've been pinged by Discord
if ( $payload[ 'type' ] == 1 ) {
	$response[ 'type' ] = 1; // Ack

// It's time to respond to a command
} elseif ( $payload[ 'type' ] == 2 ) {

	// Get the name of the command
	$command = $payload[ 'data' ][ 'name' ];

	// Is there no handler for this command?
	if ( array_key_exists( $command, $commands ) !== true ) {

		// Ack, show command, we have message
		$response[ 'type' ] = 4;

		// Send an error message
		$response[ 'data' ] = [
			'content' => 'There is no handler registered for that command on the endpoint.'
		];

		// Stop processing
		exit();

	}

	// Execute the command handler and store the result
	$result = $commands[ $command ]( $payload );

	// If the result is valid...
	if ( is_string( $result ) ) {

		// Ack, show command, we have message
		$response[ 'type' ] = 4;

		// Set the message as the result of the handler
		$response[ 'data' ] = [
			'content' => $result
		];
	
	// Result is not valid
	} else {

		// Ack, show command, we have no message
		$response[ 'type' ] = 5;

	}

}

/****************** Response ******************/

// Output the response as JSON
echo( json_encode( $response ) );

?>
