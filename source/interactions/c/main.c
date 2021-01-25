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

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <arpa/inet.h>
#include <ctype.h>

#define READ_SIZE 1024

struct handle_args {
	int sock;
	struct sockaddr_in addr;
};

void parse_request( char *buffer, int buffer_length ) {
	char request[ READ_SIZE ];
	memset( request, '\0', sizeof( request ) );
	strcpy( request, buffer );

	char *occurence = strstr( request, "\r\n\r\n" );
	*occurence = '\0';
	char *body = occurence + 4;

	char *method;
	char *path;
	char *signature;
	char *timestamp;

	int line_number = 1;
	char *line_content = strtok( request, "\r\n" );
	while ( line_content != NULL ) {
		if ( line_number == 1 ) {
			char *context;
			method = strtok_r( line_content, " ", &context );
			path = strtok_r( NULL, " ", &context );

			//printf( "REQUEST: '%s' -> '%s'\n", method, path );
		} else {
			char *first_occurence = strchr( line_content, ':' );
			*first_occurence = '\0';
			char *value = first_occurence + 2;

			for ( int i = 0; line_content[ i ]; i++ ){
				line_content[ i ] = tolower( line_content[ i ] );
			}

			if ( strcmp( line_content, "x-signature-ed25519" ) == 0 ) {
				signature = value;
			} else if ( strcmp( line_content, "x-signature-timestamp" ) == 0 ) {
				timestamp = value;
			}

			// printf( "HEADER: '%s' = '%s'\n", line_content, value );
		}

		line_content = strtok( NULL, "\r\n" );
		line_number++;
	}

	//printf( "BODY: '%s'\n", body );

	printf( "Method: %s\nPath: %s\nSignature: %s\nTimestamp: %s\nContent: %s\n", method, path, signature, timestamp, body );
}

void handle_connection( void *args ) {
	struct handle_args *argz = ( struct handle_args * ) args;;

	char *ip_address = inet_ntoa( argz->addr.sin_addr );
	unsigned short port = argz->addr.sin_port;
	printf( "%s:%d connected!\n", ip_address, port );

	int read_bytes;
	char read_buffer[ READ_SIZE ];
	bzero( read_buffer, READ_SIZE );

	while ( ( read_bytes = read( argz->sock, read_buffer, READ_SIZE - 1 ) ) > 0 ) {
		printf( "%s:%d sent us %d bytes.\n", ip_address, port, read_bytes );
		parse_request( read_buffer, read_bytes );
		bzero( read_buffer, READ_SIZE );

		write( argz->sock, "thank u", 7 );
		printf( "responded to %s:%d in 7 bytes.\n", ip_address, port );
	}

	close( argz->sock );
	printf( "%s:%d disconnected.\n", ip_address, port );

	pthread_exit( NULL );
}

int main() {
	printf( "Initalising...\n" );

	int sock_server = socket( AF_INET, SOCK_STREAM, 0 );

	struct sockaddr_in addr_server;
	bzero( ( char * ) &addr_server, sizeof( addr_server ) );

	addr_server.sin_family = AF_INET;
	addr_server.sin_addr.s_addr = INADDR_ANY;
	addr_server.sin_port = htons( 8080 );

	bind( sock_server, ( struct sockaddr * ) &addr_server, sizeof( addr_server ) );
	listen( sock_server, 5 );

	while ( 1 ) {
		struct sockaddr_in addr_client;
		socklen_t addr_client_length = sizeof( addr_client );

		int sock_client = accept( sock_server, ( struct sockaddr * ) &addr_client, &addr_client_length );

		struct handle_args *args_to_pass;
		args_to_pass->sock = sock_client;
		args_to_pass->addr = addr_client;

		pthread_t my_thread;
		pthread_create( &my_thread, NULL, ( void * ) handle_connection, args_to_pass );
	}

	close( sock_server );

	pthread_exit( NULL );

	return 0;
}
