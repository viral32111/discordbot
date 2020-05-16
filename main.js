/*
ALL OF THIS CODE IS IN ALPHA!

This is only my first time
properly coding anything in
Node.js & my first time using
the Discord.js library, so
don't expect good code as
of now.

More changes will continue to
come in the future, hopefully
making the bot much more stable
and efficient.

Please ignore all of the randomly
commented out code in this file,
it's just where I was testing a
few features.
*/

// Import required packages
const discord = require( "discord.js" )
const axios = require( "axios" )
const crypto = require( "crypto" )
const fs = require( "fs" )
// const worker = require( "worker_threads" ) // i was gonna use this at some point

// Other files
const bitly = require( "./modules/bitly.js" )
const configDiscord = require( "./config/discord.js" )

require( "./extensions/array.js" )

// Configs & data
const existingAttachmentShortURLs = require( "./attachment-short-urls.json" )
const existingImageHistory = require( "./image-history.json" ) // yes i know this is a really shit way to do this, i'm still learning :/

// Create the client
console.log( "Loading..." )
const client = new discord.Client( {
	// Cache related
	messageCacheMaxSize: -1, // Store unlimited messages in the cache
	messageCacheLifetime: 0, // Never let anything in the cache expire
	messageSweepInterval: 0, // Never sweep/purge anything in the cache
	fetchAllMembers: true, // Cache all guild members on startup

	// Prevent any sort of mentions
	disableMentions: "all",

	// Set the rich presence status
	/*presence: {
		status: "online",
		id: "701769962125262878",
		activity: {
			name: "test",
			type: "PLAYING"
		} 
	},*/

	// Receive partial events for uncached objects
	partials: [
		"USER", // e.g. uncached user changes avatar
		"CHANNEL", // e.g. uncached channel is renamed
		"GUILD_MEMBER", // e.g. uncached member changes nick
		"MESSAGE", // e.g. uncached message is edited
		"REACTION", // e.g. uncached message is reacted to
	]

	// Force enable every intent
	/*ws: {
		intents: [
			discord.Intents.ALL
			OR?
			discord.Intents.GUILDS,
			discord.Intents.GUILD_MEMBERS,
			discord.Intents.GUILD_BANS,
			discord.Intents.GUILD_EMOJIS,
			discord.Intents.GUILD_INTEGRATIONS,
			discord.Intents.GUILD_WEBHOOKS,
			discord.Intents.GUILD_INVITES,
			discord.Intents.GUILD_VOICE_STATES,
			discord.Intents.GUILD_PRESENCES,
			discord.Intents.GUILD_MESSAGES,
			discord.Intents.GUILD_MESSAGE_REACTIONS,
			discord.Intents.GUILD_MESSAGE_TYPING,
			discord.Intents.DIRECT_MESSAGES,
			discord.Intents.DIRECT_MESSAGE_REACTIONS,
			discord.Intents.DIRECT_MESSAGE_TYPING
		]
	}*/
} )

// Safely shutdown bot on CTRL + C
process.on( "SIGINT", function() {
	// Friendly message
	console.log( "\nShutting down..." )

	// Loop through each connected voice channel 
	client.voice.connections.each( function( voiceConnection ) {
		// Friendly message
		console.log( `Disconnecting from ${ voiceConnection.channel.name }...` )

		// Leave the voice channels
		voiceConnection.disconnect()
	} )

	// Logs out, terminates connection & destroys the client
	client.destroy()

	// Stops the running process
	process.exit()
} )

// List of activities to show on the bot
const activityList = [
	/*
	PLAYING: Playing <whatever>
	WATCHING: Watching <whatever>
	LISTENING: Listening to <whatever>
	STREAMING: Streaming <whatever> (Only works when Stream URL is set!)
	*/

	[ "PLAYING", "Garry's Mod" ],
	[ "PLAYING", "Half-Life" ],
	[ "PLAYING", "Half-Life 2" ],
	[ "PLAYING", "Half-Life 2: Episode 1" ],
	[ "PLAYING", "Half-Life 2: Episode 2" ],
	[ "PLAYING", "Half-Life: Alyx" ],
	[ "PLAYING", "Half-Life 3" ],
	[ "PLAYING", "Sandbox" ],
	[ "PLAYING", "Spacebuild" ],
	[ "PLAYING", "DarkRP" ],
	[ "PLAYING", "with broken addons." ],
	[ "PLAYING", "with my code." ],
	[ "PLAYING", "with the Physics Gun." ],
	[ "PLAYING", "with the Tool Gun." ],
	[ "PLAYING", "S&box" ],
	[ "PLAYING", "Source 2" ],
	[ "PLAYING", "GMod 2" ],
	[ "PLAYING", "Garry's Mod 9 Beta" ],
	[ "PLAYING", "Garry's Mod (Source 2 Beta)" ],
	[ "PLAYING", "Half-Life: Alyx - Workshop Tools" ],
	[ "PLAYING", "Hammer World Editor" ],
	[ "PLAYING", "Hammer 2" ],
	[ "PLAYING", "F-STOP" ],
	[ "PLAYING", "Half-Life: Blue Shift" ],
	[ "PLAYING", "Half-Life: Opposing Force" ],
	[ "PLAYING", "Half-Life: Source" ],
	[ "PLAYING", "Half-Life 2: Deathmatch" ],
	[ "PLAYING", "Source SDK 2006" ],
	[ "PLAYING", "Source SDK 2007" ],
	[ "PLAYING", "Source SDK 2013" ],
	[ "PLAYING", "Source 2 SDK" ],
	[ "PLAYING", "Half-Life 2: Episode 3" ],
	[ "PLAYING", "with fire." ],
	[ "PLAYING", "with burning servers." ],
	[ "PLAYING", "with Sandbox's code." ],
	[ "PLAYING", "with myself." ],
	[ "PLAYING", "alone on the server." ],
	[ "PLAYING", "dead." ],

	[ "WATCHING", "you read this." ],
	[ "WATCHING", "you get banned." ],
	[ "WATCHING", "over the community." ],
	[ "WATCHING", "people break rules." ],
	[ "WATCHING", "YouTube videos." ],
	[ "WATCHING", "@Conspiracy AI v1." ],
	[ "WATCHING", "all of your messages." ],
	[ "WATCHING", "you watch me watch you watch me watch you watch me watch you -and so on, for a long time." ],
	[ "WATCHING", "players on the server." ],
	[ "WATCHING", "the server crash." ],
	[ "WATCHING", "the server lag." ],
	[ "WATCHING", "you sleep." ],

	[ "LISTENING", "minges cry." ],
	[ "LISTENING", "your voice chat." ],
	[ "LISTENING", "Spotif- iTune- YouTube Music..." ],
	[ "LISTENING", "in-game voice chat." ],
	[ "LISTENING", "dubstep DarkRP loading screens." ],
	[ "LISTENING", "\"RDM!, RDM! @ADMIN TP\"" ]
]

// The current/last randomly picked activity
let currentRandomActivity = null

// Shuffle to random activity function
function setRandomActivity() {
	// Hold the new randomly picked activity
	let newRandomActivity = null

	// Is this not the first run?
	if ( currentRandomActivity !== null ) {
		// Repeat until we don't have the same activity
		do {
			// Choose a random activity
			newRandomActivity = activityList.random()
		} while ( newRandomActivity[ 1 ] === currentRandomActivity[ 1 ] )

	// It is the first run
	} else {
		// Choose a random activity
		newRandomActivity = activityList.random()
	}

	// Update the client's activity
	client.user.setActivity( newRandomActivity[ 1 ], {
		type: newRandomActivity[ 0 ]
	} )

	// Update the current activity variable
	currentRandomActivity = newRandomActivity

	// Repeat every 5 minutes
	setTimeout( setRandomActivity, 300000 )
}

// Called when the client is ready
client.on( "ready", async function() {
	// Friendly message
	console.log( `Logged in as ${client.user.tag}!` )

	// Shuffle activity status
	setRandomActivity()

	// Cache ~100 past messages in every channel incase the bot abruptly shutdown & we don't want to miss any message events!
	// this doesn't actually work, i was expecting it to reduce the amount of partials :/
	/*for ( const channel of client.channels.cache.array() ) {
		// Skip non-text channels
		if ( channel.type !== "text" ) continue

		const previousCachedAmount = channel.messages.cache.size

		const collection = await channel.messages.fetch( {
			limit: 100
		} )

		for ( const message of collection.array() ) {
			await message.fetch()
		}

		console.log( "Cached", collection.size, "past messages from #", channel.name, "before was", previousCachedAmount)

		/*channel.messages.fetch( {
			limit: 100
		} ).then( async function( collection ) {
			for ( const message of collection.array() ) {
				await message.fetch()
			}

			console.log( "Cached", collection.size, "past messages from #", channel.name, "before was", previousCachedAmount)
		} )*

		

		/*channel.awaitMessages( function( message ) {
			console.log("filter",message.cleanContent)
			return true
		}, {
			max: 100,
			maxProcessed: 100
		} ).then( function( collected ) {
			console.log( collected.size )
		} ).catch( console.error )*/

		// break
	/*}

	for ( const channel of client.channels.cache.array() ) {
		console.log("cache for",channel.name,"is now", channel.messages.cache.size)
	}
	// Connect to my office
	/*const myOffice = await client.channels.fetch( '709435485398892635' )
	const voiceConnection = await myOffice.join()

	// For debugging
	voiceConnection.on( "authenticated", () => console.debug( "voiceConnection", "AUTHENTICATED" ) )
	voiceConnection.on( "disconnect", () => console.debug( "voiceConnection", "DISCONNECT" ) )
	voiceConnection.on( "newSession", () => console.debug( "voiceConnection","NEWSESSION" ) )
	voiceConnection.on( "ready", () => console.debug( "voiceConnection", "READY" ) )
	voiceConnection.on( "reconnecting", () => console.debug( "voiceConnection", "RECONNECTING" ) )
	voiceConnection.on( "debug", ( msg ) => console.debug( "voiceConnection", "DEBUG", msg ) )
	voiceConnection.on( "warn", ( wrn ) => console.warn( "voiceConnection", "WARN", wrn ) )
	voiceConnection.on( "error", ( err ) => console.error( "voiceConnection", "ERROR", err ) )
	voiceConnection.on( "failed", ( err ) => console.error( "voiceConnection", "FAILED", err ) )

	// Create the stream for writing to a file
	//const writeSockStream = fs.createWriteStream( `/tmp/discord_to_garrysmod.sock` )
	//const readSockStream = fs.createReadStream( `/tmp/discord_to_garrysmod.sock` )

	const server = net.createServer()
	server.listen( "/tmp/discord_to_garrysmod.sock", () => {
		console.log("bound")
	} )

	// When a user starts speaking
	voiceConnection.on( "speaking", function( user, state ) {
		if ( state.bitfield == 1 ) { // Speaking
			console.log( `${ user.tag } is speaking` )

			

			// For debugging
			/*
			writeFileStream.on( "close", () => console.debug( "writeFileStream", "CLOSE" ) )
			writeFileStream.on( "drain", () => console.debug( "writeFileStream", "DRAIN" ) )
			writeFileStream.on( "finish", () => console.debug( "writeFileStream", "FINISH" ) )
			writeFileStream.on( "pipe", ( src ) => console.debug( "writeFileStream", "PIPE", src ) )
			writeFileStream.on( "unpipe", ( src ) => console.debug( "writeFileStream", "UNPIPE", src ) )
			writeFileStream.on( "error", ( err ) => console.error( "writeFileStream", "ERROR", err ) )
			*/

			// For receiver debugging
			/*voiceConnection.receiver.on( "debug", ( err ) => console.error( "voiceConnection.receiver", "DEBUG", err ) )

			// Create receiving voice stream (PCM - signed 16-bit, little-endian, 2-channel, 48KHz sample-rate)
			const readVoiceStream = voiceConnection.receiver.createStream( user.id, {
				mode: "pcm",
				//end: "manual"
			} )

			// For debugging
			readVoiceStream.on( "end", () => {
				console.debug( "readVoiceStream", "END", `No longer listening to ${ user.tag }` )
				// writeFileStream.end()
				server.close()
			} )

			// Start piping recieved audio stream to the write file stream
			readVoiceStream.pipe( server )
			console.debug( "readVoiceStream", `Now listening to ${ user.tag }` )



		} else if ( state.bitfield == 0 ) { // Not speaking
			console.log( `${ user.tag } is no longer speaking` )
		}
	} )

	// Create a ReadableStream of s16le PCM audio
	/*const stream = voiceConnection.receiver.createStream( '480764191465144331', {
		mode: 'pcm'
	} )

	stream.pipe(  )*/
} )

client.on( "message", async function( message ) {
	// Repost detector
	
	// Loop through each attachment
	for ( const attachment of message.attachments.array() ) {
		// Skip attachments that aren't images or videos
		if ( attachment.width === undefined ) continue

		// Request the attachment
		const response = await axios.get( attachment.url ).catch( console.error )

		// Hash the bytes of the attachment
		const hash = crypto.createHash( "sha1" ).update( response.data ).digest( "hex" )

		// Check if it exists in the image history data
		if ( existingImageHistory[ hash ] !== undefined ) {
			// Add the author to the repost author if they aren't the original author or already in repost authors
			if ( existingImageHistory[ hash ].author !== message.author.id && existingImageHistory[ hash ].reposters[ message.author.id ] === undefined ) {
				existingImageHistory[ hash ].reposters.push( message.author.id )
			}

			// Fetch original poster
			const originalAuthor = client.users.fetch( existingImageHistory[ hash ].author )
			
			// Send a message i suppose
			/* await message.reply( `I've seen that image/video ${ existingImageHistory[ hash ].count } time(s) before!\n\nI first saw this posted by ${ originalAuthor.tag } (\`${ existingImageHistory[ hash ] }\`), here's a link: <${ existingImageHistory[ hash ].link }>.`, {
				disableMentions: false
			} ) */
			await message.reply( `I've seen that image/video ${ existingImageHistory[ hash ].count } time(s) before! (<${ existingImageHistory[ hash ].link }>)` )

			// Increment the counter
			existingImageHistory[ hash ].count += 1
		} else {
			// Add the new short URL to the image history data
			existingImageHistory[ hash ] = {
				author: message.author.id,
				link: message.url,
				timestamp: message.createdTimestamp,
				reposters: [],
				count: 1
			}
		}
	}

	// Check if there were any attachments
	if ( message.attachments.size > 0 ) {
		// Resave image history
		fs.writeFile( "image-history.json", JSON.stringify( existingImageHistory ), function( err ) {
			if ( err ) throw err
		} )
	}

	/* Relay changes:
	1) https://discordapp.com/channels/240167618575728644/509871330104049684/709807239837253642
	2) https://discordapp.com/channels/240167618575728644/509871330104049684/709846833865818275
	3) https://discordapp.com/channels/240167618575728644/509871330104049684/709913214732730369
	*/

	// Is the message in the Sandbox server relay channel?
	// (Is actually my private development channel for now, so I don't clog up the main relay channel)
	/*if ( message.channel.id == "420369246363844613" ) {
		// Variable for the final message after we've made all our changes
		let finalMessage = ""

		// Create an array for holding attachment short URLs
		const attachmentShortURLs = []

		// Loop through each attachment
		for ( const attachment of message.attachments.array() ) {
			// Request the attachment
			const response = await axios.get( attachment.url )

			// Hash the bytes of the attachment
			const hash = crypto.createHash( "sha1" ).update( response.data ).digest( "hex" )

			// Holder for the short URL
			let shortURL = null

			// Check if hash exists in existing attachment short URLs
			if ( existingAttachmentShortURLs[ hash ] !== undefined ) {
				// Construct short URL
				shortURL = "https://bit.ly/" + existingAttachmentShortURLs[ hash ]

			// It doesn't exist in the existing attachment short URLs
			} else {
				// Create a new short URL for the attachment
				shortURL = await bitly.shortenURL( attachment.url, [
					"Reason: Discord Relay",
					"Server: Sandbox",
					`Member: ${ message.author.id }`
				] )

				// Extract the short URL identifier without the host or protocol
				const id = /bit\.ly\/(\w+)/g.exec( shortURL )[ 1 ]

				// Add the new short URL to the existing attachment short URLs array
				existingAttachmentShortURLs[ hash ] = id
			}

			// Strip the protocol, if we've got more than 3 attachments or more than 20 characters of text
			if ( message.attachments.size > 3 || message.cleanContent.length > 20 ) {
				shortURL = shortURL.replace( /https?:\/\//, "" )
			}

			// Add the short URL to the array
			attachmentShortURLs.push( shortURL )
		}

		// Convert custom emojis to just the text representation
		finalMessage = message.cleanContent.replace( /<(a?):([A-Za-z0-9_-]+):(\d+)>/g, ":$2:" )

		// Append the attachment short URLs to the end of the original message content (if it exists)
		finalMessage = ( finalMessage.length > 0 ? finalMessage + " " : "" ) + attachmentShortURLs.join( " " )

		// Check if the length of the final message is greater than the Garry's Mod max chat message length?
		if ( message.cleanContent.length >= 127 ) {
			// Tell them their message is too long
			// const replyMessage = await message.reply( "your message is too long to be relayed! (try to keep it below 127 characters, this includes emojis & URLs of attachments)" )
			const replyMessage = await message.channel.send( `> ${ message.author.content }\n${ message.author.tag }, your message is too long to be relayed! (try to keep it below 127 characters, this includes emojis & URLs of attachments.)` )

			// Delete the message after 10 seconds
			await replyMessage.delete( { timeout: 10000 } )

			// Stop execution
			return
		}

		// Construct the request payload
		const payload = {
			message: finalMessage,
			author: message.member.displayName,
			role: {
				name: message.member.roles.highest.name,
				color: [
					( message.member.displayColor & 0xFF0000 ) >> 16, // Red
					( message.member.displayColor & 0x00FF00 ) >> 8, // Green
					( message.member.displayColor & 0x0000FF ) // Blue
				]
			}
		}

		// Relay the message to the Garry's Mod server
		// Protip: Dear reader, don't bother trying to make a request to this API endpoint because it's heavily whitelisted.
		// TODO: bloody stop using a Rest API & develop my own protocol for internal communication
		const response = await axios.post( "http://sandbox.conspiracyservers.com:27190/discord", payload )

		// Check if there were any attachments sent to see if we need to write any changes
		if ( message.attachments.size > 0 ) {
			// Write new existing attachment short URLs array to the JSON file
			fs.writeFile( "attachment-short-urls.json", JSON.stringify( existingAttachmentShortURLs ), function( err ) {
				if ( err ) throw err
			} )
		}
	}*/
} )

// Message edited
client.on( "messageUpdate", async function( oldMessage, newMessage ) {
	// Check if we're receiving an uncached message edit
	if ( oldMessage.partial === true ) {
		// We can't see what the content was before :c


	// The old message is in the cache
	} else {
		// We can see everything! :D
	}

	const fetchedOldMessage = await oldMessage.fetch()
	console.log( "#", oldMessage.channel.name, ":", oldMessage.cleanContent, "[", oldMessage.id, "]", "-->", "#", newMessage.channel.name, ":", newMessage.cleanContent, "[", newMessage.id, "]" )
	console.log( "#", fetchedOldMessage.channel.name, ":", fetchedOldMessage.cleanContent, "[", fetchedOldMessage.id, "]", "-->", "#", newMessage.channel.name, ":", newMessage.cleanContent, "[", newMessage.id, "]" )
	console.log( oldMessage.partial, fetchedOldMessage.partial, newMessage.partial )
} )

// Login
client.login( configDiscord.token )