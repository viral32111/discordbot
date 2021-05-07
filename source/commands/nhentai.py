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
from __main__ import configuration, USER_AGENT_HEADER

# Import required modules
import discord, requests, slashcommands
import random, datetime

##############################################
# Define slash command
##############################################

# nhentai
@slashcommands.new( "Searches nhentai.net for doujinshi & manga, then shows the best match.", options = [
	slashcommands.option(
		type = slashcommands.option.type.string,
		name = "query",
		description = "The search query, tags or a magic number.",
		required = True
	)
], guild = 240167618575728644 )
async def nhentai( interaction ):
	
	if interaction.channelID != 682646257205903440 and interaction.channelID != 420369246363844613:
		await interaction.respond( ":exclamation: This can only be used in <#682646257205903440>.", hidden = True )
		return

	query = interaction.arguments[ "query" ]
	message = await interaction.think()
	data = None

	if query.isdigit():
		apiResponse = requests.request( "GET", f"https://nhentai.net/api/gallery/{ query }", headers = {
			"Accept": "application/json",
			"User-Agent": USER_AGENT_HEADER,
			"From": configuration[ "general" ][ "email" ]
		} )

		apiResponse.raise_for_status()

		data = apiResponse.json()
	else:
		apiResponse = requests.request( "GET", "https://nhentai.net/api/galleries/search", params = {
			"query": query,
			"page": "1"
		}, headers = {
			"Accept": "application/json",
			"User-Agent": USER_AGENT_HEADER,
			"From": configuration[ "general" ][ "email" ]
		} )

		apiResponse.raise_for_status()

		tempData = apiResponse.json()

		if len( tempData[ "result" ] ) <= 0:
			await message.edit( ":mag_right: I was not able to find anything matching that search query." )
			return

		data = tempData[ "result" ][ 0 ]
		data[ "results" ] = ( tempData[ "num_pages" ] * tempData[ "per_page" ] ) - 1

	tags = [ tag[ "name" ] for tag in data[ "tags" ] if tag[ "type" ] == "tag" ]
	tags.sort()

	languages = [ tag[ "name" ].title() for tag in data[ "tags" ] if tag[ "type" ] == "language" ]
	languages.sort()

	artists = [ tag[ "name" ] for tag in data[ "tags" ] if tag[ "type" ] == "artist" ]
	artists.sort()

	categories = [ tag[ "name" ].title() for tag in data[ "tags" ] if tag[ "type" ] == "category" ]
	categories.sort()

	embed = discord.Embed(
		title = f"#{ data[ 'id' ] }: { data[ 'title' ][ 'pretty' ] }",
		url = f"https://nhentai.net/g/{ data[ 'id' ] }",
		color = 0xF15478
	)

	if len( tags ) > 0:
		embed.description = ", ".join( tags )
	
	embed.set_author(
		name = "nhentai",
		url = "https://nhentai.net",
		icon_url = "https://viral32111.github.io/conspiracy-ai/icons/nhentai.png"
	)

	if len( artists ) > 0:
		embed.add_field(
			name = "__Artists__",
			value = ", ".join( artists ),
			inline = True
		)

	if len( languages ) > 0:
		embed.add_field(
			name = "__Languages__",
			value = ", ".join( languages ),
			inline = True
		)

	if len( categories ) > 0:
		embed.add_field(
			name = "__Category__",
			value = ", ".join( categories ),
			inline = True
		)

	embed.add_field(
		name = "__Favourites__",
		value = "{:,}".format( data[ "num_favorites" ] ),
		inline = True
	)

	embed.add_field(
		name = "__Pages__",
		value = "{:,}".format( data[ "num_pages" ] ),
		inline = True
	)

	embed.add_field(
		name = "__Uploaded__",
		value = datetime.datetime.fromtimestamp( data[ "upload_date" ] ).strftime( "%A %d %b %Y, %H:%M:%S" ),
		inline = True
	)

	embed.set_image(
		url = f"https://t.nhentai.net/galleries/{ data[ 'media_id' ] }/cover.jpg",
	)

	if "results" in data:
		embed.set_footer(
			text = f"There were { '{:,}'.format( data[ 'results' ] ) } similar results found, but this one is the best match."
		)

	await message.edit( embeds = [ embed ] )
