# Conspiracy AI

This is the official Discord bot for the Conspiracy Servers community.

The structure of the MySQL database is within the [database.sql](https://github.com/conspiracy-servers/conspiracy-ai/blob/master/database.sql) file.

Check the [project board](https://github.com/conspiracy-servers/conspiracy-ai/projects/2) to see what features are planned and being worked on.

Report bugs by creating a [new issue](https://github.com/conspiracy-servers/conspiracy-ai/issues/new).

## Dependencies

### Native

[json](https://docs.python.org/3/library/json.html), [re](https://docs.python.org/3/library/re.html), [datetime](https://docs.python.org/3/library/datetime.html), [time](https://docs.python.org/3/library/time.html), [random](https://docs.python.org/3/library/random.html), [os](https://docs.python.org/3/library/os.html), [sys](https://docs.python.org/3/library/sys.html), [traceback](https://docs.python.org/3/library/traceback.html), [hashlib](https://docs.python.org/3/library/hashlib.html), [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html), [mimetypes](https://docs.python.org/3/library/mimetypes.html), [shutil](https://docs.python.org/3/library/shutil.html), [inspect](https://docs.python.org/3/library/inspect.html), [itertools](https://docs.python.org/3/library/itertools.html), [urllib.parse](https://docs.python.org/3/library/urllib.parse.html), [difflib](https://docs.python.org/3/library/difflib.html), [operator](https://docs.python.org/3/library/operator.html), [asyncio](https://docs.python.org/3/library/asyncio.html), [signal](https://docs.python.org/3/library/signal.html), [enum](https://docs.python.org/3/library/enum.html), [socket](https://docs.python.org/3/library/socket.html).

### Thirdparty

[discord.py](https://pypi.org/project/discord.py/), [requests](https://pypi.org/project/requests/), [hurry.filesize](https://pypi.org/project/hurry.filesize/), [mysql-connector-python](https://pypi.org/project/mysql-connector-python/), [pytz](https://pypi.org/project/pytz/), [dotmap](https://pypi.org/project/dotmap/), [beautifulsoup4](https://pypi.org/project/beautifulsoup4/), [youtube_dl](https://pypi.org/project/youtube_dl/), [emoji](https://pypi.org/project/emoji/), [mcstatus](https://pypi.org/project/mcstatus/), [requests-unixsocket](https://pypi.org/project/requests-unixsocket/), [python-dateutil](https://pypi.org/project/python-dateutil/), [slashcommands](https://github.com/viral32111/slashcommands).

## Notes

### Response Emojis

Non-embedded message responses from this bot are usually prefixed with emojis to better indicate what the message is about. Below is a table that gives a brief description & example of the ones in use.

| Emoji | Code Representation | Description | Example |
|:-----:|:-------------------:|:----------- | :------ |
| ❗ | `:exclamation:` | Incorrect channel for command. | NSFW command not being used in an NSFW channel. |
| ❔ | `:grey_question:` | Unknown or invalid arguments provided. | Providing letters instead of a number for an argument. |
| ❕ | `:grey_exclamation:` | Not enough arguments provided or incorrect command usage. | Not providing any arguments to a command. |
| ⁉️ | `:interrobang:` | An internal code error occured. | A malformed response from an API. |
| 🚫 | `:no_entry_sign:` | This command cannot be used by you. | Attempting to run a moderation command as a user. |
| 🔎 | `:mag_right:` | An issue with searching. | Failed to find specified content from an API. |
| 🔧 | `:wrench:` | Command is in development. | Attempting to run any work-in-progress commands. |
| ✅ | `:white_check_mark:` | Action was successful. | A message was successfully deleted. |
| ℹ️ | `:information_source:` | Information available. | Response contains helpful information. |
| ♻️ | `:recycle:` | A repost was detected. | The content flagged has been posted by someone else in the past. |
| 🔗 | `:link:` | Link to an external website. | Response provides a link to the community website. |

## License

Copyright (C) 2016 - 2021 [viral32111](https://viral32111.com).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see https://www.gnu.org/licenses.
