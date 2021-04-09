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
from __main__ import configuration

# Import required modules
import slashcommands, discord

##############################################
# Define slash commands
##############################################

# Timeout a user
@slashcommands.new( "Prevents a user from talking ever again.", options = [ slashcommands.option(
	name = "member",
	description = "The member to time out.",
	type = slashcommands.option.type.user,
	required = True
) ], guild = 240167618575728644 )
async def timeout( interaction ):
	permissions = discord.Permissions( permissions = int( interaction.member.permissions ) )

	# Does the user not have the manage messages permission?
	if not permissions.manage_messages:
		await interaction.respond( ":no_entry_sign: This command can only be used by staff members.", hidden = True )
		return

	# Fetch the member to time out
	member = interaction.client.guilds[ 0 ].get_member( int( interaction.arguments[ "member" ] ) )

	# Fetch the timeout role
	timeoutRole = interaction.client.guilds[ 0 ].get_role( configuration[ "roles" ][ "timeout" ] )

	# Give the member the timeout role
	await member.add_roles( timeoutRole, reason = "Member timed out by " + interaction.user.username + "#" + interaction.user.discriminator )

	# Send message feedback
	await interaction.respond( "Timed out " + member.mention + " indefinitely.", hidden = True )

# Remove a user from timeout
@slashcommands.new( "Prevents a user from talking ever again.", options = [ slashcommands.option(
	name = "member",
	description = "The member to time out.",
	type = slashcommands.option.type.user,
	required = True
) ], guild = 240167618575728644 )
async def untimeout( interaction ):
	permissions = discord.Permissions( permissions = int( interaction.member.permissions ) )

	# Does the user not have the manage messages permission?
	if not permissions.manage_messages:
		await interaction.respond( ":no_entry_sign: This command can only be used by staff members.", hidden = True )
		return

	# Fetch the member to time out
	member = interaction.client.guilds[ 0 ].get_member( int( interaction.arguments[ "member" ] ) )

	# Are they using it on themselves?
	if member.id == interaction.user.id:
		await interaction.respond( ":no_entry_sign: You cannot remove yourself from timeout.", hidden = True )
		return

	# Fetch the timeout role
	timeoutRole = interaction.client.guilds[ 0 ].get_role( configuration[ "roles" ][ "timeout" ] )

	# Give the member the timeout role
	await member.remove_roles( timeoutRole, reason = "Member removed from timeout by " + interaction.user.username + "#" + interaction.user.discriminator )

	# Send message feedback
	await interaction.respond( "Removed " + member.mention + " from timeout.", hidden = True )
