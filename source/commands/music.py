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

# Import required modules
import slashcommands

##############################################
# Define slash commands
##############################################

# Add/remove a member from the Music DJ role
@slashcommands.new( "Add or remove a member from the Music DJ role (only usable by other Music DJs).", options = [ slashcommands.option(
	name = "member",
	description = "The member to add or remove the Music DJ role from.",
	type = slashcommands.option.type.user,
	required = True
) ], guild = 240167618575728644 )
async def toggledj( interaction ):
	# Get the DJ role
	musicDJ = interaction.client.guilds[ 0 ].get_role( 784532835348381776 )

	# Get the Music voice channel
	musicChannel = interaction.client.guilds[ 0 ].get_channel( 257480146762596352 )

	author = interaction.client.guilds[ 0 ].get_member( interaction.user.id )
	member = interaction.client.guilds[ 0 ].get_member( int( interaction.arguments[ "member" ] ) )

	# Send a message if the caller is not a Music DJ
	if musicDJ not in author.roles:
		await interaction.respond( ":no_entry_sign: This command can only be used by a " + musicDJ.mention + ".", hidden = True )
		return

	# Is the member not in the Music voice channel?
	if member not in musicChannel.members:
		await interaction.respond( member.mention + " needs to be in the Music voice channel.", hidden = True )
		return

	# Does the member already have the Music DJ role?
	if musicDJ in member.roles:

		# Remove the role from them
		await member.remove_roles( musicDJ, reason = "Member was removed from Music DJ by " + str( author ) + "." )

		# Send a message
		await interaction.respond( ":white_check_mark: " + member.mention + " is no longer a " + musicDJ.mention + ".", hidden = True )

	# They do not have the Music DJ role
	else:

		# Add the role to them
		await member.add_roles( musicDJ, reason = "Member was added to Music DJ added by " + str( author ) + "." )

		# Send a message
		await interaction.respond( ":white_check_mark: " + member.mention + " is now a " + musicDJ.mention + ".", hidden = True )
