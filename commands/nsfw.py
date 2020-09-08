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

##############################################
# Define chat commands
##############################################

# Rule #34
@chatCommands( category = "NSFW", aliases = [ "r34" ], nsfw = True )
async def rule34( message, arguments ):

	# Send a message if no arguments were provided
	if len( arguments ) < 1: return { "content": ":grey_exclamation: You must provide at least one tag to search for." }

	# Search the Rule #34 API with the tags provided by the user (always excluding loli & shota)
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
	if len( posts ) < 1: return { "content": ":mag_right: I wasn't able to find anything matching the provided tags." }

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
