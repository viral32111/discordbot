##############################################
# Setup this script
##############################################

# Import variables from the main script
from __main__ import chatCommand

# Import required modules
import discord, asyncio, time

##############################################
# Define chat commands
##############################################

# Sleep
@chatCommand( category = "Dev", wip = True )
async def sleep( message, arguments ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must specify the duration to sleep for in seconds." }

	# Convert the duration argument to an integer
	duration = int( arguments[ 0 ] )

	# Friendly message
	await message.channel.send( "Sleeping for `" + "{:,}".format( duration ) + "` seconds..." )

	# Store high resolution time in seconds of when the sleeping started
	started = time.perf_counter()

	# Sleep
	await asyncio.sleep( duration )

	# Store high resolution time in seconds of when the sleeping finished
	finished = time.perf_counter() - started

	# Friendly message
	await message.channel.send( "Finished sleeping, took `" + "{:,}".format( finished ) + "` seconds." )
