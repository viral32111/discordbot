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
from __main__ import chatCommands, configuration

# Import required modules
import discord

##############################################
# Define chat commands
##############################################

# Timeout a user
@chatCommands( category = "Moderation" )
async def timeout( message, arguments, client ):

	# Does the user not have the manage messages permission?
	if not message.author.guild_permissions.manage_messages:

		# Feedback message
		return { "content": ":no_entry_sign: This command can only be used by staff members." }

	# Was there no mentions?
	if len( message.mentions ) < 1:

		# Friendly message
		return { "content": ":grey_exclamation: You must mention at least one member." }

	# Fetch the timeout role
	timeoutRole = message.channel.guild.get_role( configuration[ "roles" ][ "timeout" ] )

	# Loop through every mentioned member
	for member in message.mentions:

		# Give the member the timeout role
		await member.add_roles( timeoutRole, reason = "Member timed out by " + str( message.author ) )

		# Send message feedback
		await message.channel.send( "Timed out " + member.mention + " indefinitely." )

# Remove a user from timeout
@chatCommands( category = "Moderation" )
async def untimeout( message, arguments, client ):

	# Does the user not have the manage messages permission?
	if not message.author.guild_permissions.manage_messages:

		# Feedback message
		return { "content": ":no_entry_sign: This command can only be used by staff members." }

	# Was there no mentions?
	if len( message.mentions ) < 1:

		# Friendly message
		return { "content": ":grey_exclamation: You must mention at least one member." }

	# Fetch the timeout role
	timeoutRole = message.channel.guild.get_role( configuration[ "roles" ][ "timeout" ] )

	# Loop through every mentioned member
	for member in message.mentions:

		# Are they using it on themselves?
		if member.id == message.author.id:

			# Friendly message
			await message.channel.send( ":no_entry_sign: You cannot remove yourself from timeout." )

			# Prevent further execution
			return

		# Remove the timeout role from the member
		await member.remove_roles( timeoutRole, reason = "Member removed from timeout by " + str( message.author ) )

		# Send message feedback
		await message.channel.send( "Removed " + member.mention + " from timeout." )

# Restrict member(s) to text channel(s) for a optional amount of time
@chatCommands( category = "Moderation" )
async def restrict( message, arguments, client ):

	# Stop with a message if the calling member does not have the Manage Messages permission
	if not message.channel.permissions_for( message.author ).manage_messages: return { "content": ":no_entry_sign: This command can only be used by Moderators." }

	# Stop with a message if no members were mentioned in the message
	if len( message.mentions ) < 1: return { "content": ":grey_exclamation: You must mention at least 1 member." }

	# Stop with a message if no text channels were mentioned in the message
	if len( message.channel_mentions ) < 1: return { "content": ":grey_exclamation: You must mention at least 1 text channel." }

	member_mentions = [ member.mention for member in message.mentions ]
	channel_mentions = [ channel.mention for channel in message.channel_mentions ]
	duration_text = " ".join( [ argument for argument in arguments if argument not in member_mentions and argument not in channel_mentions ] )

	fancy_member_mentions = ( ", ".join( member_mentions[ : -1 ] ) + " & " + member_mentions[ -1 ] ) if len( member_mentions ) > 1 else member_mentions[ 0 ]
	fancy_channel_mentions = ( ", ".join( channel_mentions[ : -1 ] ) + " & " + channel_mentions[ -1 ] ) if len( channel_mentions ) > 1 else channel_mentions[ 0 ]

	return { "content": ":lock: Restricted " + fancy_member_mentions + " to " + fancy_channel_mentions + " for **" + duration_text + "**." }
