# Conspiracy AI

This is the official Discord bot for the Conspiracy Servers community.

The structure of the MySQL database is within the [database.sql](https://github.com/conspiracy-servers/conspiracy-ai/blob/master/database.sql) file.

Check the [project board](https://github.com/conspiracy-servers/conspiracy-ai/projects/2) to see what features are planned and being worked on.

Report bugs by creating a [new issue](https://github.com/conspiracy-servers/conspiracy-ai/issues/new).

## Dependencies

### Native

[json](https://docs.python.org/3/library/json.html), [re](https://docs.python.org/3/library/re.html), [datetime](https://docs.python.org/3/library/datetime.html), [time](https://docs.python.org/3/library/time.html), [random](https://docs.python.org/3/library/random.html), [os](https://docs.python.org/3/library/os.html), [sys](https://docs.python.org/3/library/sys.html), [traceback](https://docs.python.org/3/library/traceback.html), [hashlib](https://docs.python.org/3/library/hashlib.html), [xml.etree.ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html), [mimetypes](https://docs.python.org/3/library/mimetypes.html), [shutil](https://docs.python.org/3/library/shutil.html), [inspect](https://docs.python.org/3/library/inspect.html), [itertools](https://docs.python.org/3/library/itertools.html), [urllib.parse](https://docs.python.org/3/library/urllib.parse.html), [difflib](https://docs.python.org/3/library/difflib.html), [operator](https://docs.python.org/3/library/operator.html), [asyncio](https://docs.python.org/3/library/asyncio.html).

### Thirdparty

[discord.py](https://pypi.org/project/discord.py/), [requests](https://pypi.org/project/requests/), [hurry.filesize](https://pypi.org/project/hurry.filesize/), [mysql-connector-python](https://pypi.org/project/mysql-connector-python/), [pytz](https://pypi.org/project/pytz/), [dotmap](https://pypi.org/project/dotmap/), [beautifulsoup4](https://pypi.org/project/beautifulsoup4/), [youtube_dl](https://pypi.org/project/youtube_dl/).

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

## Legal

### License

This software is licensed and distributed under the [GNU Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.html) in the hope that it will be useful to the open-source community and help educate future generations. This is free, open-source software meaning everyone is allowed to take this source code to modify it, redistribute it, use it privately or commercially so long as they publicly disclose the complete source code, state the changes they have made to the source code, provide a license and copyright notice however is appropriate and finally, retain the same license. Detailed information is available in [the included license file](LICENSE.md).

### Distribution

I kindly ask anyone who wishes to redistribute this software to [contact us](mailto:contact@conspiracyservers.com?subject=Conspiracy%20AI%20redistribution) beforehand so that I may review how the software is being used. Of course, I cannot stop you from distributing it, but I would love to see how others have taken our work and adapted it. This is in your best interest, as adaptations and redistributions that I see as interesting or high quality may be listed here and given extra publicity.

Do not redistribute the software with or without changes because this repository seems stale, dead, or otherwise abandoned. You should contribute your changes directly to this repository and keep it active. If you are redistributing this software at a cost, or over a network, ensure you are following the conditions described in the license. Most importantly, the complete public disclosure of the license, changes, and source code of your redistribution.

### Contributing

Furthermore, anyone who contributes here has an express grant of patent rights over their contribution, this means they hold the copyright for the code that they create. If you are contributing content that is not originally authored by you, please ensure that you have the appropriate permission from the original author beforehand, or better, request the original author to contribute it on your behalf.

All contributed code still falls under the same license permissions and conditions described in the license, so others are still free to adapt, modify and redistribute it. If you do not wish for this, then please do not contribute to this software.

A list of contributors can be found on [the repository's insights page](https://github.com/conspiracy-servers/conspiracy-ai/graphs/contributors).

### Liability

I and other contributors are not responsible for anything you do while using this software. Any general, special, incidental, or consequential damages, data loss, reports, penalties, or other repercussions of utilisation caused by your abuse, misuse, or inability to use this software correctly fall solely under your responsibility.

### Warranty

This software is provided as-is, without any warranty of any kind, without even the implied warranty of merchantability or fitness for a particular purpose. More information is available on [the GNU licensing website](https://www.gnu.org/licenses/).

If you discover the software is defective while using it, then you may report it on [the repository's issue page](https://github.com/conspiracy-servers/conspiracy-ai/issues) as it may turn out to be an issue with the software as a whole. This does not guarantee that it will be fixed, nor does it imply responsibility by the author of the defective code, as bugs are often accidental mistakes caused by human error. In any other situation, you assume the responsibility and cost of all necessary servicing, repair, or correction.

### Copyright

Copyright (C) 2016 - 2020 [viral32111](https://github.com/viral32111).
