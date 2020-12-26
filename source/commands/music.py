###################################################################################
# Conspiracy AI - The official Discord bot for the Conspiracy Servers community.
# Copyright (C) 2016 - 2020 viral32111 (https://viral32111.com)
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
from __main__ import chatCommands

##############################################
# Define chat commands
##############################################

# Add/remove a member from the Music DJ role
@chatCommands( category = "Music", aliases = [ "dj" ] )
async def toggledj( message, arguments, client ):

	# Get the DJ role
	musicDJ = message.guild.get_role( 784532835348381776 )

	# Get the Music voice channel
	musicChannel = message.guild.get_channel( 257480146762596352 )

	# Send a message if the caller is not a Music DJ
	if musicDJ not in message.author.roles: return { "content": ":no_entry_sign: This command can only be used by a " + musicDJ.mention + "." }

	# Send a message if no arguments were provided
	if len( message.mentions ) < 1: return { "content": ":grey_exclamation: You must mention the member(s) to toggle " + musicDJ.mention + " on." }

	# Loop through each mentioned member
	for member in message.mentions:

		# Is the member not in the Music voice channel?
		if member not in musicChannel.members:

			# Send a message
			await message.channel.send( member.mention + " needs to be in the Music voice channel." )

			# Skip to the next member
			continue

		# Does the member already have the Music DJ role?
		if musicDJ in member.roles:

			# Remove the role from them
			await member.remove_roles( musicDJ, reason = "Member was removed from Music DJ by " + str( message.author ) + "." )

			# Send a message
			await message.channel.send( ":white_check_mark: " + member.mention + " is no longer a " + musicDJ.mention + "." )

		# They do not have the Music DJ role
		else:

			# Add the role to them
			await member.add_roles( musicDJ, reason = "Member was added to Music DJ added by " + str( message.author ) + "." )

			# Send a message
			await message.channel.send( ":white_check_mark: " + member.mention + " is now a " + musicDJ.mention + "." )
