// TODO: actually use these classes at some point

// I just copied these over from CS AI v1 but only changed the syntax so they defo won't work

class Bot {
	constructor( dict ) {
		this.name = dict[ "name" ]
		this.userID = dict[ "id" ]
	}
}

class Player extends Bot {
	constructor( dict ) {
		this.steamID = dict[ "steamid" ]
		this.group = dict[ "group" ]
		this.groupPretty = GROUPS[ this.group ]
		this.time = dict[ "time" ]
		this.timePretty = dict[ "time" ]
		this.profileURL = "https://steamcommunity.com/profiles/" + this.steamID
	}
}

class Server {
	constructor(  )
}

// Expose classes and functions
module.exports = {
	Bot = Bot,
	Player = Player,
	Server = Server
}