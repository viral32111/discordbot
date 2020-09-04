##############################################
# Setup this script
##############################################

# Import variables from the main script
from __main__ import chatCommand, settings

# Import required modules
import discord

##############################################
# Define chat commands
##############################################

# Help
@chatCommand( category = "General" )
async def help( message, arguments ):

	# Create a blank embed
	embed = discord.Embed( title = "", description = "", color = settings.color )

	# Add the about field to the embed
	embed.add_field(

		# The title of the field
		name = "About Us",

		# The description of the field
		value = "Conspiracy Servers is a Garry's Mod community founded by <@" + str( settings.owner ) + "> and <@213413722943651841> in early 2016. We've been going for nearly 5 years now and have always kept our non-serious, relaxed and casual approach towards our community and the servers which we run."

	)

	# Add the guidelines & rules field to the embed
	embed.add_field(

		# The title of the field
		name = "Guidelines & Rules",

		# The description of the field
		value = "If you're new here or need a refresher on our rules & guidelines then read <#410507397166006274>.",

		# Don't place this field inline with the other fields
		inline = False

	)

	# Add the chat commands field to the embed
	embed.add_field(

		# The title of the field
		name = "Chat Commands",

		# The description of the field
		value = "Type `" + settings.prefix + "commands` for a list of chat commands. Keep command usage in <#241602380569772044> to avoid cluttering the discussion channels.",

		# Don't place this field inline with the other fields
		inline = False

	)

	# Add the contacting staff field to the embed
	embed.add_field(

		# The title of the field
		name = "Contacting Staff",

		# The description of the field
		value = "You can reach out to our staff by direct messaging anyone with the <@&507323152737763352>, <@&613124236101419019>, <@&748809314290106389> or <@&519273212807348245> role.",

		# Don't place this field inline with the other fields
		inline = False

	)

	# Respond with this embed
	return { "embed": embed }
