##############################################
# Setup this script
##############################################

# Import the chat command object from the main script
from __main__ import chatCommand

# Import any required modules
import discord

##############################################
# Define chat commands
##############################################

# Example
@chatCommand()
async def example( message, arguments ):
	return "example"

# ABC
@chatCommand()
async def abc( message, arguments ):
	return "abc"

# Foo
@chatCommand( bar = 123 )
async def foo( message, arguments ):
	return "foo"
