##############################################
# Setup this script
##############################################

# Import variables from the main script
from __main__ import chatCommands

# Import required modules
import discord, asyncio, time

##############################################
# Define chat commands
##############################################

# Sleep
@chatCommands( category = "Dev", wip = True )
async def sleep( message, arguments ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must specify the duration to sleep for in seconds." }

	# Convert the duration argument to a float
	duration = float( arguments[ 0 ] )

	# Friendly message
	await message.channel.send( "Sleeping for `" + "{0:.16f}".format( duration ) + "` seconds..." )

	# Store high resolution time in seconds of when the sleeping started
	started = time.perf_counter()

	# Sleep
	await asyncio.sleep( duration )

	# Store high resolution time in seconds of when the sleeping finished
	finished = time.perf_counter() - started

	# Friendly message
	await message.channel.send( "Finished sleeping, sleep lasted exactly `" + "{0:.16f}".format( finished ) + "` seconds." )
