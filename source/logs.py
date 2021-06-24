# TO-DO: Helper functions for commonly repeated values, such as {member}, {message} and {location}.

# Import dependencies
import os, datetime

# The rules of logging:
# * User controlled values should be wrapped in single quotes
# * Additional information comes after primary information in brackets
# * Applicable values should be prefixed or suffixed to indicate what they mean
# * Lists should be wrapped in square brackets
# * Anything that is void should be replaced with a placeholder hyphen
# * Do not relog past information, just give an ID in curly brackets to refer back to it
# * Respect user privacy and redact information for direct messages

# The log file handle
logFile = None

# Writes a message to the console and log file
def write( message ):

	# Fail if the log file handle is not valid
	if not logFile: return False

	# Add the current date & time to the message
	prefixedMessage = "[{datetime:%d-%m-%Y %H:%M:%S.%f %z}] {message}".format(
		datetime = datetime.datetime.now( datetime.timezone.utc ),
		message = message
	)

	# Write to the log file with a new line
	logFile.write( prefixedMessage + "\n" )
	logFile.flush()

	# Print to the console
	print( prefixedMessage )

	# Success
	return True

# Creates the log file with the specified path template and writes a start message
def start( logPathTemplate ):

	# Apply changes to global variables
	global logFile

	# Fail if the log file handle is already valid
	if logFile: return False

	# The number to start at for the log file name
	logNumber = 1

	# Increment the number until no log file with this number exists
	while os.path.isfile( logPathTemplate.format( logNumber ) ): logNumber += 1

	# Create and open the log file handle
	logFile = open( logPathTemplate.format( logNumber ), "w" )
	
	# Write an initial start message to the logs
	write( "Opened log file '{logPath}'.".format(
		logPath = logFile.name
	) )

	# Successful, give back the path
	return logFile.name

# Closes the log file and writes a stop message
def stop():

	# Apply changes to global variables
	global logFile

	# Fail if the log file handle is not valid
	if not logFile: return False

	# Write a final stop message to the logs
	write( "Closing log file '{logPath}'...".format(
		logPath = logFile.name
	) )

	# Close the log file handle
	logFile.close()

	# Set the log file handle to null
	logFile = None

	# Success
	return True
