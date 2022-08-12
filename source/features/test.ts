import { bot } from "../main.js"
import { Guild, Message, User } from "../discord/types.js"

// Runs when the bot finishes loading
bot.once( "ready", ( user: User, guilds: Guild[] ) => {
	console.log( "Ready as user '%s#%d' (%s) in %d server(s).", user.Name, user.Discriminator, user.Identifier, guilds.length )

	console.log( user.Avatar, user.AvatarUrl() )
} )

// Runs when the bot joins a server
bot.on( "guildCreate", ( guild: Guild ) => {
	console.log( "Joined server '%s' (%s).", guild.name, guild.id )
} )

bot.on( "messageCreate", async ( message: Message ) => {
	console.log( "Message '%s' (%s).", message.content, message.identifier )

	await message.reply( "hi!" )
} )
