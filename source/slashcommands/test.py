###################################################################################
# Conspiracy AI - The official Discord bot for the Conspiracy Servers community.
# Copyright (C) 2016 - 2021 viral32111 (https://viral32111.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see http://www.gnu.org/licenses/.
###################################################################################

##############################################
# Setup this script
##############################################

# Import variables from the main script
from __main__ import slashCommands, ApplicationCommandOption, ApplicationCommandOptionType, ApplicationCommandOptionChoice, InteractionResponse, InteractionResponseType, InteractionApplicationCommandCallbackData

# Import required modules
import discord

##############################################
# Define slash commands
##############################################

# Test
@slashCommands( description = "A test command to check if the bot can respond to interactions over the gateway." )
async def test( guild, channel, member, options ):
	return InteractionResponse(
		InteractionResponseType.ChannelMessageWithSource,
		InteractionApplicationCommandCallbackData(
			"Haha this was a test!"
		)
	)

# Hello World
@slashCommands( description = "Another testing command, do arguments work?", options = [
	ApplicationCommandOption(
		name = "message",
		description = "This is where the message goes.",
		type = ApplicationCommandOptionType.String,
		required = True
	)
] )
async def hello( guild, channel, member, options ):
	print( "Hello World!" )

# Foo Bar
@slashCommands( description = "A third testing command, do multiple arguments with choices work?", options = [
	ApplicationCommandOption(
		name = "cool",
		description = "A super cool value.",
		type = ApplicationCommandOptionType.Integer,
		choices = [
			ApplicationCommandOptionChoice( "This is number 1", 1 ),
			ApplicationCommandOptionChoice( "This is number 2", 2 ),
			ApplicationCommandOptionChoice( "This is number 3", 3 )
		]
	),
	ApplicationCommandOption(
		name = "epic",
		description = "An amazingly epic value.",
		type = ApplicationCommandOptionType.String,
		choices = [
			ApplicationCommandOptionChoice( "This is choice 1", "one" ),
			ApplicationCommandOptionChoice( "This is choice 2", "two" )
		]
	)
] )
async def foo( guild, channel, member, options ):
	print( "Foo Bar!" )

# Example
@slashCommands( description = "Fourth testing command, we're testing sub-commands here.", options = [
	ApplicationCommandOption(
		name = "idk",
		description = "I don't know tbh.",
		type = ApplicationCommandOptionType.SubCommand,
		options = [
			ApplicationCommandOption(
				name = "number",
				description = "It's just a number bro.",
				type = ApplicationCommandOptionType.Integer,
			),
			ApplicationCommandOption(
				name = "kthxbai",
				description = "I'm running out of ideas for argument names.",
				type = ApplicationCommandOptionType.String,
				choices = [
					ApplicationCommandOptionChoice( "AAAAAAAAAAAAAAAA", "mood" ),
					ApplicationCommandOptionChoice( "eternal pain", "life" )
				]
			)
		]
	)
] )
async def example( guild, channel, member, options ):
	print( "Example!" )