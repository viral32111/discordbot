##############################################
# Setup this script
##############################################

# Import variables, globals and functions from the main script
from __main__ import chatCommands, settings, USER_AGENT_HEADER, downloadWebMedia

# Import required modules
import discord # Discord.py
import requests # HTTP requests
import random # Randomisation
import xml.etree.ElementTree # XML parser for Rule #34 API responses
import os # Host operaring system interaction
import json # JSON parser

##############################################
# Define chat commands
##############################################

# Rule #34
@chatCommands( category = "NSFW", aliases = [ "r34" ], nsfw = True )
async def rule34( message, arguments ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must provide at least one tag to search for.\n(Cheatsheet: <https://rule34.xxx/index.php?page=help&topic=cheatsheet>)" }

	# Search with the tags provided by the user (always excluding loli & shota)
	request = requests.get( "https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit=100&tags=" + ( "%20".join( arguments ) ) + "%20-loli%20-shota", headers = {
		"Accept": "application/xml",
		"User-Agent": USER_AGENT_HEADER,
		"From": settings.email
	} )

	# Throw an error if the request wasn't successful
	if request.status_code != 200: raise Exception( "Received an unsuccessful API response: " + str( request.status_code ) + "\n" + str( request.text ) )

	# Parse the XML response from the API
	root = xml.etree.ElementTree.fromstring( request.text )

	# Create a native list of post objects from each child element
	posts = [ child for child in root ]

	# Send a message if no posts were returned
	if len( posts ) < 1: return { "content": ":mag_right: I wasn't able to find anything matching the provided tags.\n(Cheatsheet: <https://rule34.xxx/index.php?page=help&topic=cheatsheet>)" }

	# Sort the posts by highest to lowest score
	posts.sort( key = lambda post: int( post.get( "score" ) ), reverse = True )

	# Pick a random post from the top 10 with the highest score
	post = random.choice( posts[ :10 ] )

	# Download that post
	path = downloadWebMedia( post.get( "file_url" ) )

	# Send a message with the post inline if the post failed to download
	if path == None: return { "content": "Score: **" + post.get( "score" ) + "**.\n||" + post.get( "file_url" ) + "||" }

	# Send a message with the post inline if the file size is greater than 8MB (~8,388,119 bytes)? - See redd.it/aflp3p
	if os.path.getsize( path ) > 8388119: return { "content": "Score: **" + post.get( "score" ) + "**.\n||" + post.get( "file_url" ) + "||" }

	# Create a file attachment marked as spoiler for uploading
	attachment = discord.File( path, filename = post.get( "md5" ) + os.path.splitext( path )[ 1 ], spoiler = True )

	# Be safe!
	try:

		# Send a message with the file as an attachment
		return { "content": "Score: **" + post.get( "score" ) + "**.", "file": attachment }

	# Catch discord HTTP errors
	except discord.HTTPException as error:

		# Is this error caused by the file being too large?
		if error.code == 40005:

			# Send a message with the post inline
			return { "content": "Score: " + post.get( "score" ) + ".\n||" + post.get( "file_url" ) + "||" }

		# Re-raise the error if it was caused by something else
		else: raise error

# Xbooru
@chatCommands( category = "NSFW", aliases = [ "xb" ], nsfw = True )
async def xbooru( message, arguments ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must provide at least one tag to search for.\n(Cheatsheet: <https://xbooru.com/index.php?page=help&topic=cheatsheet>)" }

	# Search with the tags provided by the user (always excluding loli & shota)
	request = requests.get( "https://xbooru.com/index.php?page=dapi&s=post&q=index&limit=100&tags=" + ( "%20".join( arguments ) ) + "%20-loli%20-shota", headers = {
		"Accept": "application/xml",
		"User-Agent": USER_AGENT_HEADER,
		"From": settings.email
	} )

	# Throw an error if the request wasn't successful
	if request.status_code != 200: raise Exception( "Received an unsuccessful API response: " + str( request.status_code ) + "\n" + str( request.text ) )

	# Parse the XML response from the API
	root = xml.etree.ElementTree.fromstring( request.text )

	# Create a native list of post objects from each child element
	posts = [ child for child in root ]

	# Send a message if no posts were returned
	if len( posts ) < 1: return { "content": ":mag_right: I wasn't able to find anything matching the provided tags.\n(Cheatsheet: <https://xbooru.com/index.php?page=help&topic=cheatsheet>)" }

	# Sort the posts by highest to lowest score
	posts.sort( key = lambda post: int( post.get( "score" ) ), reverse = True )

	# Pick a random post from the top 10 with the highest score
	post = random.choice( posts[ :10 ] )

	# Download that post
	path = downloadWebMedia( post.get( "file_url" ) )

	# Send a message with the post inline if the post failed to download
	if path == None: return { "content": "Score: **" + post.get( "score" ) + "**.\n||" + post.get( "file_url" ) + "||" }

	# Send a message with the post inline if the file size is greater than 8MB (~8,388,119 bytes)? - See redd.it/aflp3p
	if os.path.getsize( path ) > 8388119: return { "content": "Score: **" + post.get( "score" ) + "**.\n||" + post.get( "file_url" ) + "||" }

	# Create a file attachment marked as spoiler for uploading
	attachment = discord.File( path, filename = post.get( "md5" ) + os.path.splitext( path )[ 1 ], spoiler = True )

	# Be safe!
	try:

		# Send a message with the file as an attachment
		return { "content": "Score: **" + post.get( "score" ) + "**.", "file": attachment }

	# Catch discord HTTP errors
	except discord.HTTPException as error:

		# Is this error caused by the file being too large?
		if error.code == 40005:

			# Send a message with the post inline
			return { "content": "Score: " + post.get( "score" ) + ".\n||" + post.get( "file_url" ) + "||" }

		# Re-raise the error if it was caused by something else
		else: raise error

# FurryBooru
@chatCommands( category = "NSFW", aliases = [ "fur" ], nsfw = True )
async def furrybooru( message, arguments ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must provide at least one tag to search for.\n(Cheatsheet: <https://furry.booru.org/index.php?page=help&topic=cheatsheet>)" }

	# Search with the tags provided by the user (always excluding loli & shota)
	request = requests.get( "https://furry.booru.org/index.php?page=dapi&s=post&q=index&limit=100&tags=" + ( "%20".join( arguments ) ) + "%20-loli%20-shota", headers = {
		"Accept": "application/xml",
		"User-Agent": USER_AGENT_HEADER,
		"From": settings.email
	} )

	# Throw an error if the request wasn't successful
	if request.status_code != 200: raise Exception( "Received an unsuccessful API response: " + str( request.status_code ) + "\n" + str( request.text ) )

	# Parse the XML response from the API
	root = xml.etree.ElementTree.fromstring( request.text )

	# Create a native list of post objects from each child element
	posts = [ child for child in root ]

	# Send a message if no posts were returned
	if len( posts ) < 1: return { "content": ":mag_right: I wasn't able to find anything matching the provided tags.\n(Cheatsheet: <https://furry.booru.org/index.php?page=help&topic=cheatsheet>)" }

	# Sort the posts by highest to lowest score
	posts.sort( key = lambda post: int( post.get( "score" ) ), reverse = True )

	# Pick a random post from the top 10 with the highest score
	post = random.choice( posts[ :10 ] )

	# Download that post
	path = downloadWebMedia( post.get( "file_url" ) )

	# Send a message with the post inline if the post failed to download
	if path == None: return { "content": "Score: **" + post.get( "score" ) + "**.\n||" + post.get( "file_url" ) + "||" }

	# Send a message with the post inline if the file size is greater than 8MB (~8,388,119 bytes)? - See redd.it/aflp3p
	if os.path.getsize( path ) > 8388119: return { "content": "Score: **" + post.get( "score" ) + "**.\n||" + post.get( "file_url" ) + "||" }

	# Create a file attachment marked as spoiler for uploading
	attachment = discord.File( path, filename = post.get( "md5" ) + os.path.splitext( path )[ 1 ], spoiler = True )

	# Be safe!
	try:

		# Send a message with the file as an attachment
		return { "content": "Score: **" + post.get( "score" ) + "**.", "file": attachment }

	# Catch discord HTTP errors
	except discord.HTTPException as error:

		# Is this error caused by the file being too large?
		if error.code == 40005:

			# Send a message with the post inline
			return { "content": "Score: " + post.get( "score" ) + ".\n||" + post.get( "file_url" ) + "||" }

		# Re-raise the error if it was caused by something else
		else: raise error

# Gelbooru
@chatCommands( category = "NSFW", aliases = [ "gel" ], nsfw = True )
async def gelbooru( message, arguments ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must provide at least one tag to search for.\n(Cheatsheet: <https://gelbooru.com/index.php?page=help&topic=cheatsheet>)" }

	# Search with the tags provided by the user (always excluding loli & shota)
	request = requests.get( "https://gelbooru.com/index.php?page=dapi&s=post&q=index&limit=100&json=1&tags=" + ( "%20".join( arguments ) ) + "%20-loli%20-shota", headers = {
		"Accept": "application/json",
		"User-Agent": USER_AGENT_HEADER,
		"From": settings.email
	} )

	# Throw an error if the request wasn't successful
	if request.status_code != 200: raise Exception( "Received an unsuccessful API response: " + str( request.status_code ) + "\n" + str( request.text ) )

	# Store the returned JSON data
	posts = request.json()

	# Send a message if no posts were returned
	if len( posts ) < 1: return { "content": ":mag_right: I wasn't able to find anything matching the provided tags.\n(Cheatsheet: <https://gelbooru.com/index.php?page=help&topic=cheatsheet>)" }

	# Sort the posts by highest to lowest score
	posts.sort( key = lambda post: post[ "score" ], reverse = True )

	# Pick a random post from the top 10 with the highest score
	post = random.choice( posts[ :10 ] )

	# Download that post
	path = downloadWebMedia( post[ "file_url" ] )

	# Send a message with the post inline if the post failed to download
	if path == None: return { "content": "Score: **" + str( post[ "score" ] ) + "**.\n||" + post[ "file_url" ] + "||" }

	# Send a message with the post inline if the file size is greater than 8MB (~8,388,119 bytes)? - See redd.it/aflp3p
	if os.path.getsize( path ) > 8388119: return { "content": "Score: **" + str( post[ "score" ] ) + "**.\n||" + post[ "file_url" ] + "||" }

	# Create a file attachment marked as spoiler for uploading
	attachment = discord.File( path, filename = post[ "hash" ] + os.path.splitext( path )[ 1 ], spoiler = True )

	# Be safe!
	try:

		# Send a message with the file as an attachment
		return { "content": "Score: **" + str( post[ "score" ] ) + "**.", "file": attachment }

	# Catch discord HTTP errors
	except discord.HTTPException as error:

		# Is this error caused by the file being too large?
		if error.code == 40005:

			# Send a message with the post inline
			return { "content": "Score: " + str( post[ "score" ] ) + ".\n||" + post[ "file_url" ] + "||" }

		# Re-raise the error if it was caused by something else
		else: raise error

# Danbooru
@chatCommands( category = "NSFW", aliases = [ "dan" ], nsfw = True )
async def danbooru( message, arguments ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must provide at least one tag to search for.\n(Cheatsheet: <https://danbooru.donmai.us/wiki_pages/help:cheatsheet>)" }

	# Send a message if more than two arguments were provided
	if len( arguments ) > 2: return { "content": ":grey_exclamation: You cannot search for more than 2 tags at a time." }

	# Search with the tags provided by the user
	request = requests.get( "https://danbooru.donmai.us/posts.json?tags=" + ( "%20".join( arguments ) ), headers = {
		"Accept": "application/json",
		"User-Agent": USER_AGENT_HEADER,
		"From": settings.email
	} )

	# Throw an error if the request wasn't successful
	if request.status_code != 200: raise Exception( "Received an unsuccessful API response: " + str( request.status_code ) + "\n" + str( request.text ) )

	# Store the returned JSON data
	posts = request.json()

	# Send a message if no posts were returned
	if len( posts ) < 1: return { "content": ":mag_right: I wasn't able to find anything matching the provided tags.\n(Cheatsheet: <https://danbooru.donmai.us/wiki_pages/help:cheatsheet>)" }

	# Sort the posts by highest to lowest score
	posts.sort( key = lambda post: post[ "score" ], reverse = True )

	# Pick a random post from the top 10 with the highest score
	post = random.choice( posts[ :10 ] )

	# Download that post
	path = downloadWebMedia( post[ "file_url" ] )

	# Send a message with the post inline if the post failed to download
	if path == None: return { "content": "Score: **" + str( post[ "score" ] ) + "**.\n||" + post[ "file_url" ] + "||" }

	# Send a message with the post inline if the file size is greater than 8MB (~8,388,119 bytes)? - See redd.it/aflp3p
	if os.path.getsize( path ) > 8388119: return { "content": "Score: **" + str( post[ "score" ] ) + "**.\n||" + post[ "file_url" ] + "||" }

	# Create a file attachment marked as spoiler for uploading
	attachment = discord.File( path, filename = post[ "md5" ] + os.path.splitext( path )[ 1 ], spoiler = True )

	# Be safe!
	try:

		# Send a message with the file as an attachment
		return { "content": "Score: **" + str( post[ "score" ] ) + "**.", "file": attachment }

	# Catch discord HTTP errors
	except discord.HTTPException as error:

		# Is this error caused by the file being too large?
		if error.code == 40005:

			# Send a message with the post inline
			return { "content": "Score: " + str( post[ "score" ] ) + ".\n||" + post[ "file_url" ] + "||" }

		# Re-raise the error if it was caused by something else
		else: raise error

# Hypnohub
@chatCommands( category = "NSFW", aliases = [ "hypno" ], nsfw = True )
async def hypnohub( message, arguments ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must provide at least one tag to search for.\n(Cheatsheet: <https://hypnohub.net/help/cheatsheet>)" }

	# Search with the tags provided by the user
	request = requests.get( "https://hypnohub.net/post.json?tags=" + ( "%20".join( arguments ) ), headers = {
		"Accept": "application/json",
		"User-Agent": USER_AGENT_HEADER,
		"From": settings.email
	} )

	# Throw an error if the request wasn't successful
	if request.status_code != 200: raise Exception( "Received an unsuccessful API response: " + str( request.status_code ) + "\n" + str( request.text ) )

	# Store the returned JSON data
	posts = request.json()

	# Send a message if no posts were returned
	if len( posts ) < 1: return { "content": ":mag_right: I wasn't able to find anything matching the provided tags.\n(Cheatsheet: <https://hypnohub.net/help/cheatsheet>)" }

	# Sort the posts by highest to lowest score
	posts.sort( key = lambda post: post[ "score" ], reverse = True )

	# Pick a random post from the top 10 with the highest score
	post = random.choice( posts[ :10 ] )

	# Download that post
	path = downloadWebMedia( post[ "file_url" ] )

	# Send a message with the post inline if the post failed to download
	if path == None: return { "content": "Score: **" + str( post[ "score" ] ) + "**.\n||" + post[ "file_url" ] + "||" }

	# Send a message with the post inline if the file size is greater than 8MB (~8,388,119 bytes)? - See redd.it/aflp3p
	if os.path.getsize( path ) > 8388119: return { "content": "Score: **" + str( post[ "score" ] ) + "**.\n||" + post[ "file_url" ] + "||" }

	# Create a file attachment marked as spoiler for uploading
	attachment = discord.File( path, filename = post[ "md5" ] + os.path.splitext( path )[ 1 ], spoiler = True )

	# Be safe!
	try:

		# Send a message with the file as an attachment
		return { "content": "Score: **" + str( post[ "score" ] ) + "**.", "file": attachment }

	# Catch discord HTTP errors
	except discord.HTTPException as error:

		# Is this error caused by the file being too large?
		if error.code == 40005:

			# Send a message with the post inline
			return { "content": "Score: " + str( post[ "score" ] ) + ".\n||" + post[ "file_url" ] + "||" }

		# Re-raise the error if it was caused by something else
		else: raise error
