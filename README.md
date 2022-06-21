# Discord Bot

This is the official bot for my community Discord server.

**NOTE**: This repository is very barebones at present as I am in the process of slowly rewriting my *"Discord Bot from Scratch"* (a bot made in Node.js without any third-party libraries) from my personal Git server and publishing that here.

## History

Over the years, this bot has gone through countless language changes, complete rewrites, and branding changes. I have done my best to collate a small list of them below, but do note that the dates are rough estimates.

Sadly, half of these are not in this repository's commit history as I either worked on them in private without Git, on my personal Git server, or in a separate repository which has since been deleted.

### Conspiracy AI

This was the original bot back when the community was branded as *Conspiracy Servers*, its name was carried over from an automation bot we used on the MyBB forums before we made the move to Discord.

* **2016**: RedBot with custom configurations (Temporary bot until I started coding my own).
* **2016/2017**: Started with C# on the .NET Framework using [Discord.NET](https://github.com/discord-net/Discord.Net).
* **2017**: Moved to Python using [discord.py](https://github.com/Rapptz/discord.py), as I did not like Discord.NET's command-oriented approach to everything.
* **2017-2019**: Stayed on Python for a while, but went through about half a dozen major rewrites.
* **2019/2020**: Tried out Node.js using [discord.js](https://discord.js.org), but I did not like it so this one was quickly abandoned.

### Suimin

This is the current bot for the community, which started when the community was rebranded to *viral32111's community*.

* **2020**: Continued to use the latest version of Conspiracy AI's code in Python with [discord.py](https://github.com/Rapptz/discord.py), with a few minor changes.
* **2021**: [discord.py got deprecated](https://gist.github.com/Rapptz/4a2f62751b9600a31a0d3c78100287f1), so I tried out Node.js again, but this time without [discord.js](https://discord.js.org) or any third-party libraries, this went great but was never finished and thus never published.
* **2021**: Tried making a low-level bot in C, but I ended up abandoning it when it came to coding my own JSON parser.
* **2022**: Went back to the no libraries bot using Node.js as it was the most successful, moved it over to TypeScript, and continued to use it.

## License

Copyright (C) 2016-2022 [viral32111](https://viral32111.com).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see https://www.gnu.org/licenses.
