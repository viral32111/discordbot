##############################################
# Setup this script
##############################################

# Import the chat command object from the main script
from __main__ import chatCommand

# Import required modules
import discord

##############################################
# Define chat commands
##############################################

# Example
@chatCommand( aliases = [ "hello", "hw" ], wip = True )
async def helloworld( message, arguments ):
	return { "content": "hello discord!\n" + ", ".join( arguments ) }

@chatCommand( subaliases = [ "foo", "bar" ], aliases = [ "hwfoo" ], parent = "helloworld" )
async def foobar( message, arguments ):
	return { "content": "fooooooooooo\n" + ", ".join( arguments ) }

@chatCommand( subaliases = [ "fun", "funny" ], parent = "foobar" )
async def funni( message, arguments ):
	return { "content": "funni word\n" + ", ".join( arguments ) }
