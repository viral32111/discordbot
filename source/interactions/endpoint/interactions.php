<?php

/********************************************************************************
Conspiracy AI - The official Discord bot for the Conspiracy Servers community.
Copyright (C) 2016 - 2021 viral32111 (https://viral32111.com)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see http://www.gnu.org/licenses/.
********************************************************************************/

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
