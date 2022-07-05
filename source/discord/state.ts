import { User, Application, Guild } from "./types.js"

const cache = {
	application: null as Application | null,
	user: new Map<string, User>(),
	guild: new Map<string, Guild>()
}

export function updateApplication( application: Application ) {
	cache.application = { ...cache.application, ...application }

	return cache.application!
}

export function updateUser( user: User ) {
	cache.user.set( user.id, { ...cache.user.get( user.id ), ...user } )

	return cache.user.get( user.id )!
}

export function updateGuild( guild: Guild ) {
	cache.guild.set( guild.id, { ...cache.guild.get( guild.id ), ...guild } )

	return cache.guild.get( guild.id )!
}
