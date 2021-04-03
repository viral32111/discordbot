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

# Import required modules
import slashcommands

##############################################
# Define slash commands
##############################################

# Links
@slashcommands.new( "Links to other community resources." )
async def links( interaction ):
	await interaction.respond( """**__Website__**
:paperclip: Clearnet: <https://viral32111.com/community>
:paperclip: Darknet: http://viraldwfella5we7pdbi75pmzg4bcrehcwjstyy6tgjbqhdh6pgdi6yd.onion/community

**__Discord__**
:wave_tone1: Clearnet: <https://viral32111.com/discord>
:wave_tone1: Darknet: http://viraldwfella5we7pdbi75pmzg4bcrehcwjstyy6tgjbqhdh6pgdi6yd.onion/discord
​
**__Steam Group__**
:game_die: Clearnet: <https://viral32111.com/steamgroup>
:game_die: Darknet: http://viraldwfella5we7pdbi75pmzg4bcrehcwjstyy6tgjbqhdh6pgdi6yd.onion/steamgroup

**__Donate__**
:moneybag: Clearnet: <https://viral32111.com/donate>
:moneybag: Darknet: http://viraldwfella5we7pdbi75pmzg4bcrehcwjstyy6tgjbqhdh6pgdi6yd.onion/donate

**__Staff Application__**
:coffee: Clearnet: <https://viral32111.com/apply>
:coffee: Darknet: http://viraldwfella5we7pdbi75pmzg4bcrehcwjstyy6tgjbqhdh6pgdi6yd.onion/apply

**__Discord Bot__**
:desktop: Clearnet: <https://github.com/viral32111/conspiracy-ai>""", hidden = True )
