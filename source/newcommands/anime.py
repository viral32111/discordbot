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
from __main__ import settings, USER_AGENT_HEADER

# Import required modules
import slashcommands, requests, discord

##############################################
# Define slash commands
##############################################

# MyAnimeList
@slashcommands.new( "Lookup an anime or manga from MyAnimeList.", options = [
	slashcommands.option(
		type = slashcommands.option.type.string,
		name = "search",
		description = "The name of the anime or manga to search for.",
		required = True
	)
] )
async def anime( interaction ):
	message = await interaction.think()

	apiResponse = requests.request( "GET", "https://api.jikan.moe/v3/search/anime", params = {
		"q": interaction.arguments[ "search" ]
	}, headers = {
		"Accept": "application/json",
		"User-Agent": USER_AGENT_HEADER,
		"From": settings.email
	} )

	apiResponse.raise_for_status()

	data = apiResponse.json()

	if len( data ) < 1:
		await message.edit( ":mag_right: I wasn't able to find an anime or manga with that name." )
		return

	anime = data[ "results" ][ 0 ]

	embed = discord.Embed(
		title = anime[ "title" ],
		description = anime[ "synopsis" ],
		url = anime[ "url" ],
		color = 0x2E51A2
	)

	embed.set_thumbnail(
		url = anime[ "image_url" ]
	)

	embed.add_field(
		name = "Score",
		value = str( anime[ "score" ] ),
		inline = True
	)

	embed.add_field(
		name = "Rating",
		value = anime[ "rated" ],
		inline = True
	)

	embed.add_field(
		name = "Episodes",
		value = str( anime[ "episodes" ] ),
		inline = True
	)

	embed.add_field(
		name = "Type",
		value = anime[ "type" ],
		inline = True
	)

	embed.add_field(
		name = "Currently Airing",
		value = ( "Yes" if anime[ "airing" ] == True else "No" ),
		inline = True
	)

	additionalResultsCount = len( data[ "results" ] ) - 1

	if additionalResultsCount > 0:
		embed.set_footer( text = str( additionalResultsCount ) + " additional anime(s) were found with that name, this one was the best match." )

	await message.edit( embeds = [ embed ] )