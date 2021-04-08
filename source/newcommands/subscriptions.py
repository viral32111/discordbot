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

# Import variables, globals and functions from the main script
from __main__ import settings

# Import required modules
import slashcommands

##############################################
# Define slash commands
##############################################

# Manage subscriptions
@slashcommands.new( "Manage your news notification subscriptions.", options = [
	slashcommands.option(
		type = slashcommands.option.type.subCommand,
		name = "join",
		description = "Subscribe to a type of news notification.",
		options = [ slashcommands.option(
			type = slashcommands.option.type.string,
			name = "type",
			description = "The type of news notification.",
			choices = [
				slashcommands.option.choice( "Community", "community" ),
				slashcommands.option.choice( "Minecraft", "minecraft" ),
				slashcommands.option.choice( "Conspiracy AI", "conspiracy-ai" )
			],
			required = True
		) ]
	),
	slashcommands.option(
		type = slashcommands.option.type.subCommand,
		name = "leave",
		description = "Unsubscribe from a type of news notification.",
		options = [ slashcommands.option(
			type = slashcommands.option.type.string,
			name = "type",
			description = "The type of news notification.",
			choices = [
				slashcommands.option.choice( "Community", "community" ),
				slashcommands.option.choice( "Minecraft", "minecraft" ),
				slashcommands.option.choice( "Conspiracy AI", "conspiracy-ai" )
			],
			required = True
		) ]
	)
], guild = 240167618575728644 )
async def subscriptions( interaction ):
	subCommand = interaction.data.options[ 0 ].name
	notificationType = interaction.data.options[ 0 ].options[ 0 ].value

	guild = interaction.client.guilds[ 0 ]
	member = guild.get_member( interaction.user.id )
	role = guild.get_role( settings.roles.subscriptions[ notificationType ] )

	if subCommand == "join":
		await member.add_roles( role, reason = f"Subscribed to { role }." )
		await interaction.respond( f"You have subscribed to **{ role }**!\n\nMake sure you have the `Suppress All Role @mentions` option disabled in your notification settings for the server so you receive the pings.", hidden = True )
		print( f"{ member } subscribed to { role }." )

	elif subCommand == "leave":
		await member.remove_roles( role, reason = f"Unsubscribed from { role }." )
		await interaction.respond( f"You have unsubscribed from **{ role }**.", hidden = True )
		print( f"{ member } unsubscribed from { role }." )
