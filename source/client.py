import os
import discord

bot = discord.Client( intents = discord.Intents.all() )

async def on_ready():
	print( "Ready!" )
	await bot.change_presence( activity = discord.Activity( name = "Hello World!", type = discord.ActivityType.competing ) )

bot.event( on_ready )

try:
	print( "Connecting..." )
	bot.loop.run_until_complete( bot.start( os.environ[ "BOT_TOKEN" ] ) )
except KeyboardInterrupt:
	print( "Stopping..." )
	bot.loop.run_until_complete( bot.change_presence( status = discord.Status.offline ) )
	bot.loop.run_until_complete( bot.close() )
finally:
	bot.loop.close()
