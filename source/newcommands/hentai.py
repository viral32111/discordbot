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
import discord, requests, slashcommands
import random, xml.etree.ElementTree, datetime, dateutil.parser

##############################################
# Define slash commands
##############################################

# Hentai
@slashcommands.new( "Finds and then posts recent hentai matching the provided tags, can only be used in #nsfw.", options = [
	slashcommands.option(
		type = slashcommands.option.type.string,
		name = "source",
		description = "Where to search",
		required = True,
		choices = [
			slashcommands.option.choice( "Rule 34", "rule34" ),
			slashcommands.option.choice( "Xbooru", "xbooru" ),
			slashcommands.option.choice( "Gelbooru", "gelbooru" ),
			slashcommands.option.choice( "Danbooru", "danbooru" ),
			slashcommands.option.choice( "HypnoHub", "hypnohub" )
		]
	),
	slashcommands.option(
		type = slashcommands.option.type.string,
		name = "tags",
		description = "Space-separated list of tags to search with.",
		required = True
	)
], guild = 240167618575728644 )
async def hentai( interaction ):

	# If this is not the NSFW channel (or my testing channel)
	if interaction.channelID != 682646257205903440 and interaction.channelID != 420369246363844613:

		# Send an error message only to the calling user
		await interaction.respond( ":exclamation: This can only be used in <#682646257205903440>.", hidden = True )
		
		# Prevent further execution
		return
	
	# Set the command status to thinking
	message = await interaction.think()

	# Is this for Rule 34?
	if interaction.arguments[ "source" ] == "rule34":

		# Send a request to the API for the most recent posts matching the provided tags
		searchResponse = requests.request( "GET", "https://rule34.xxx/index.php", params = {
			"page": "dapi",
			"s": "post",
			"q": "index",
			"tags": interaction.arguments[ "tags" ]
		}, headers = {
			"Accept": "application/xml",
			"User-Agent": USER_AGENT_HEADER,
			"From": settings.email
		} )

		# Throw an error if the request was unsuccessful
		searchResponse.raise_for_status()

		# Parse the XML response
		root = xml.etree.ElementTree.fromstring( searchResponse.text )

		# Were there no elements in the tree?
		if len( root ) < 1:

			# Send an error message only to the calling user
			await interaction.respond( f":mag_right: I could not find anything with the tags: `{ interaction.arguments[ 'tags' ] }`!\nMaybe you are searching wrong? Check out <https://rule34.xxx/index.php?page=help&topic=cheatsheet>.", hidden = True )
			
			# Prevent further execution
			return

		# Create a proper list from the tree
		posts = [ element for element in root ]

		# Sort that list by highest to lowest score of each post
		posts.sort( key = lambda post: post.attrib[ "score" ], reverse = True )

		# Get a random post from the top 10 highest scored posts
		post = random.choice( posts[ :10 ] )

		# Parse the uploaded and last modified times
		uploadedAt = datetime.datetime.strptime( post.attrib[ "created_at" ], "%a %b %d %H:%M:%S %z %Y" )
		modifiedAt = datetime.datetime.fromtimestamp( int( post.attrib[ "change" ] ) )

		# Get all the tags as a safe Discord string
		tags = discord.utils.escape_markdown( post.attrib[ "tags" ] )

		# Send a request to the image for getting the file size
		sizeResponse = requests.request( "HEAD", post.attrib[ "file_url" ], headers = {
			"User-Agent": USER_AGENT_HEADER,
			"From": settings.email
		} )

		# Get the file size in bytes from the returned headers
		fileSize = int( sizeResponse.headers[ "content-length" ] )

		# Use the sample image if the actual image's filesize is greater than 8MB - redd.it/aflp3p
		imageURL = post.attrib[ "sample_url" ] if fileSize > 8388119 else post.attrib[ "file_url" ]
	
		# Create an embed
		embed = discord.Embed(
			url = "https://rule34.xxx/index.php?page=post&s=view&id=" + post.attrib[ "id" ],
			title = "Score: " + post.attrib[ "score" ],
			description = ( tags[ :200 ].strip() + "... [[view all](https://rule34.xxx/index.php?page=history&type=tag_history&id=" + post.attrib[ "id" ] + ")]" if len( tags ) > 200 else tags ),
			color = 0xAAE5A4
		)

		# Set the embed author
		embed.set_author(
			name = "Rule 34",
			url = "https://rule34.xxx",
			icon_url = "https://viral32111.com/images/conspiracyai/icons/rule34.png"
		)

		# Set the embed image
		embed.set_image( url = imageURL )

		# set the embed footer
		embed.set_footer( text = modifiedAt.strftime( "Uploaded on %A %d %B %Y, %H:%M:%S." ) )

		# Send the embed
		await message.edit( embeds = [ embed ] )

	# Is this for Xbooru?
	elif interaction.arguments[ "source" ] == "xbooru":

		# Send a request to the API for the most recent posts matching the provided tags
		searchResponse = requests.request( "GET", "https://xbooru.com/index.php", params = {
			"page": "dapi",
			"s": "post",
			"q": "index",
			"tags": interaction.arguments[ "tags" ]
		}, headers = {
			"Accept": "application/xml",
			"User-Agent": USER_AGENT_HEADER,
			"From": settings.email
		} )

		# Throw an error if the request was unsuccessful
		searchResponse.raise_for_status()

		# Parse the XML response
		root = xml.etree.ElementTree.fromstring( searchResponse.text )

		# Were there no elements in the tree?
		if len( root ) < 1:

			# Send an error message only to the calling user
			await interaction.respond( f":mag_right: I could not find anything with the tags: `{ interaction.arguments[ 'tags' ] }`!\nMaybe you are searching wrong? Check out <https://xbooru.com/index.php?page=help&topic=cheatsheet>.", hidden = True )
			
			# Prevent further execution
			return

		# Create a proper list from the tree
		posts = [ element for element in root ]

		# Sort that list by highest to lowest score of each post
		posts.sort( key = lambda post: post.attrib[ "score" ], reverse = True )

		# Get a random post from the top 10 highest scored posts
		post = random.choice( posts[ :10 ] )

		# Parse the uploaded and last modified times
		uploadedAt = datetime.datetime.strptime( post.attrib[ "created_at" ], "%a %b %d %H:%M:%S %z %Y" )
		modifiedAt = datetime.datetime.fromtimestamp( int( post.attrib[ "change" ] ) )

		# Get all the tags as a safe Discord string
		tags = discord.utils.escape_markdown( post.attrib[ "tags" ] )

		# Send a request to the image for getting the file size
		sizeResponse = requests.request( "HEAD", post.attrib[ "file_url" ], headers = {
			"User-Agent": USER_AGENT_HEADER,
			"From": settings.email
		} )

		# Get the file size in bytes from the returned headers
		fileSize = int( sizeResponse.headers[ "content-length" ] )

		# Use the sample image if the actual image's filesize is greater than 8MB - redd.it/aflp3p
		imageURL = post.attrib[ "sample_url" ] if fileSize > 8388119 else post.attrib[ "file_url" ]
	
		# Create an embed
		embed = discord.Embed(
			url = "https://xbooru.com/index.php?page=post&s=view&id=" + post.attrib[ "id" ],
			title = "Score: " + post.attrib[ "score" ],
			description = ( tags[ :200 ].strip() + "... [[view all](https://xbooru.com/index.php?page=history&type=tag_history&id=" + post.attrib[ "id" ] + ")]" if len( tags ) > 200 else tags ),
			color = 0xF3EFC0
		)

		# Set the embed author
		embed.set_author(
			name = "Xbooru",
			url = "https://xbooru.com",
			icon_url = "https://viral32111.com/images/conspiracyai/icons/xbooru.png"
		)

		# Set the embed image
		embed.set_image( url = imageURL )

		# set the embed footer
		embed.set_footer( text = modifiedAt.strftime( "Uploaded on %A %d %B %Y, %H:%M:%S." ) )

		# Send the embed
		await message.edit( embeds = [ embed ] )

	# Is this for Gelbooru?
	elif interaction.arguments[ "source" ] == "gelbooru":

		# Send a request to the API for the most recent posts matching the provided tags
		searchResponse = requests.request( "GET", "https://gelbooru.com/index.php", params = {
			"page": "dapi",
			"s": "post",
			"q": "index",
			"tags": interaction.arguments[ "tags" ]
		}, headers = {
			"Accept": "application/xml",
			"User-Agent": USER_AGENT_HEADER,
			"From": settings.email
		} )

		# Throw an error if the request was unsuccessful
		searchResponse.raise_for_status()

		# Parse the XML response
		root = xml.etree.ElementTree.fromstring( searchResponse.text )

		# Were there no elements in the tree?
		if len( root ) < 1:

			# Send an error message only to the calling user
			await interaction.respond( f":mag_right: I could not find anything with the tags: `{ interaction.arguments[ 'tags' ] }`!\nMaybe you are searching wrong? Check out <https://gelbooru.com/index.php?page=wiki&s=&s=view&id=26263>.", hidden = True )
			
			# Prevent further execution
			return

		# Create a proper list from the tree
		posts = [ element for element in root ]

		# Sort that list by highest to lowest score of each post
		posts.sort( key = lambda post: post.attrib[ "score" ], reverse = True )

		# Get a random post from the top 10 highest scored posts
		post = random.choice( posts[ :10 ] )

		# Parse the uploaded and last modified times
		uploadedAt = datetime.datetime.strptime( post.attrib[ "created_at" ], "%a %b %d %H:%M:%S %z %Y" )
		modifiedAt = datetime.datetime.fromtimestamp( int( post.attrib[ "change" ] ) )

		# Get all the tags as a safe Discord string
		tags = discord.utils.escape_markdown( post.attrib[ "tags" ] )

		# Send a request to the image for getting the file size
		sizeResponse = requests.request( "HEAD", post.attrib[ "file_url" ], headers = {
			"User-Agent": USER_AGENT_HEADER,
			"From": settings.email
		} )

		# Get the file size in bytes from the returned headers
		fileSize = int( sizeResponse.headers[ "content-length" ] )

		# Use the sample image if the actual image's filesize is greater than 8MB - redd.it/aflp3p
		imageURL = post.attrib[ "sample_url" ] if fileSize > 8388119 else post.attrib[ "file_url" ]
	
		# Create an embed
		embed = discord.Embed(
			url = "https://gelbooru.com/index.php?page=post&s=view&id=" + post.attrib[ "id" ],
			title = "Score: " + post.attrib[ "score" ],
			description = ( tags[ :200 ].strip() + "... [[view all](https://gelbooru.com/index.php?page=history&type=tag_history&id=" + post.attrib[ "id" ] + ")]" if len( tags ) > 200 else tags ),
			color = 0x0773FB
		)

		# Set the embed author
		embed.set_author(
			name = "Gelbooru",
			url = "https://gelbooru.com",
			icon_url = "https://viral32111.com/images/conspiracyai/icons/gelbooru.png"
		)

		# Set the embed image
		embed.set_image( url = imageURL )

		# set the embed footer
		embed.set_footer( text = modifiedAt.strftime( "Uploaded on %A %d %B %Y, %H:%M:%S." ) )

		# Send the embed
		await message.edit( embeds = [ embed ] )

	# Is this for Danbooru?
	elif interaction.arguments[ "source" ] == "danbooru":

		# Send a request to the API for the most recent posts matching the provided tags
		searchResponse = requests.request( "GET", "https://danbooru.donmai.us/posts.json", params = {
			"tags": interaction.arguments[ "tags" ]
		}, headers = {
			"Accept": "application/json",
			"User-Agent": USER_AGENT_HEADER,
			"From": settings.email
		} )

		# Throw an error if the request was unsuccessful
		searchResponse.raise_for_status()

		# Store the returned posts
		posts = searchResponse.json()

		# Are there no posts?
		if len( posts ) < 1:

			# Send an error message only to the calling user
			await interaction.respond( f":mag_right: I could not find anything with the tags: `{ interaction.arguments[ 'tags' ] }`!\nMaybe you are searching wrong? Check out <https://danbooru.donmai.us/wiki_pages/help:cheatsheet>.", hidden = True )
			
			# Prevent further execution
			return

		# Sort the posts by highest to lowest score
		posts.sort( key = lambda post: post[ "score" ], reverse = True )

		# Get a random post from the top 10 highest scored posts
		post = random.choice( posts[ :10 ] )

		# Parse the uploaded and last modified times
		uploadedAt = dateutil.parser.parse( post[ "created_at" ] )
		modifiedAt = dateutil.parser.parse( post[ "updated_at" ] )

		# Get all the tags as a safe Discord string
		tags = discord.utils.escape_markdown( post[ "tag_string" ] )

		# Send a request to the image for getting the file size
		sizeResponse = requests.request( "HEAD", post[ "file_url" ], headers = {
			"User-Agent": USER_AGENT_HEADER,
			"From": settings.email
		} )

		# Get the file size in bytes from the returned headers
		fileSize = int( sizeResponse.headers[ "content-length" ] )

		# Use the sample image if the actual image's filesize is greater than 8MB - redd.it/aflp3p
		imageURL = post[ "large_file_url" ] if fileSize > 8388119 else post[ "file_url" ]
	
		# Create an embed
		embed = discord.Embed(
			url = "https://danbooru.donmai.us/posts/" + str( post[ "id" ] ),
			title = "Score: " + str( post[ "score" ] ),
			description = ( tags[ :200 ].strip() + "... [[view all](https://danbooru.donmai.us/post_versions?search[post_id]=" + str( post[ "id" ] ) + ")]" if len( tags ) > 200 else tags ),
			color = 0xF4F6FF
		)

		# Set the embed author
		embed.set_author(
			name = "Danbooru",
			url = "https://danbooru.donmai.us",
			icon_url = "https://viral32111.com/images/conspiracyai/icons/danbooru.png"
		)

		# Set the embed image
		embed.set_image( url = imageURL )

		# set the embed footer
		embed.set_footer( text = modifiedAt.strftime( "Uploaded on %A %d %B %Y, %H:%M:%S." ) )

		# Send the embed
		await message.edit( embeds = [ embed ] )

	# Is this for Hypnohub?
	elif interaction.arguments[ "source" ] == "hypnohub":

		# Send a request to the API for the most recent posts matching the provided tags
		searchResponse = requests.request( "GET", "https://hypnohub.net/post.json", params = {
			"tags": interaction.arguments[ "tags" ]
		}, headers = {
			"Accept": "application/json",
			"User-Agent": USER_AGENT_HEADER,
			"From": settings.email
		} )

		# Throw an error if the request was unsuccessful
		searchResponse.raise_for_status()

		# Store the returned posts
		posts = searchResponse.json()

		# Are there no posts?
		if len( posts ) < 1:

			# Send an error message only to the calling user
			await interaction.respond( f":mag_right: I could not find anything with the tags: `{ interaction.arguments[ 'tags' ] }`!\nMaybe you are searching wrong? Check out <https://hypnohub.net/help/cheatsheet>.", hidden = True )
			
			# Prevent further execution
			return

		# Sort the posts by highest to lowest score
		posts.sort( key = lambda post: post[ "score" ], reverse = True )

		# Get a random post from the top 10 highest scored posts
		post = random.choice( posts[ :10 ] )

		# Parse the uploaded and last modified times
		uploadedAt = datetime.datetime.fromtimestamp( post[ "created_at" ] )

		# Get all the tags as a safe Discord string
		tags = discord.utils.escape_markdown( post[ "tags" ] )

		# Send a request to the image for getting the file size
		sizeResponse = requests.request( "HEAD", post[ "file_url" ], headers = {
			"User-Agent": USER_AGENT_HEADER,
			"From": settings.email
		} )

		# Get the file size in bytes from the returned headers
		fileSize = int( sizeResponse.headers[ "content-length" ] )

		# Use the sample image if the actual image's filesize is greater than 8MB - redd.it/aflp3p
		imageURL = post[ "sample_url" ] if fileSize > 8388119 else post[ "file_url" ]
	
		# Create an embed
		embed = discord.Embed(
			url = "https://hypnohub.net/post/show/" + str( post[ "id" ] ),
			title = "Score: " + str( post[ "score" ] ),
			description = ( tags[ :200 ].strip() + "... [[view all](https://hypnohub.net/history?search=post:" + str( post[ "id" ] ) + ")]" if len( tags ) > 200 else tags ),
			color = 0xEE8887
		)

		# Set the embed author
		embed.set_author(
			name = "Hypnohub",
			url = "https://hypnohub.net",
			icon_url = "https://viral32111.com/images/conspiracyai/icons/hypnohub.png"
		)

		# Set the embed image
		embed.set_image( url = imageURL )

		# set the embed footer
		embed.set_footer( text = uploadedAt.strftime( "Uploaded on %A %d %B %Y, %H:%M:%S." ) )

		# Send the embed
		await message.edit( embeds = [ embed ] )

	# This was another source
	else:
		await message.edit( f"Source: `{ interaction.arguments[ 'source' ] }`\nTags: `{ interaction.arguments[ 'tags' ] }`" )
