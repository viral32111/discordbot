// Import from my scripts
import { User, Application, Guild } from "./types.js"

// Internal state for all Discord objects
const cache = {
	application: null as Application | null,
	user: new Map<string, User>(),
	guild: new Map<string, Guild>()
}

// Application
export const updateApplication = ( application: Application ) => {
	cache.application = { ...cache.application, ...application }
	return cache.application!
}
export const getApplication = () => cache.application

// Users
export const updateUser = ( data: any ) => {
	const identifier = data[ "id" ]

	if ( cache.user.has( identifier ) ) {
		cache.user.get( identifier )!.Update( data )
	} else {
		cache.user.set( identifier, new User( data ) )
	}

	return cache.user.get( identifier )!
}
export const getUser = ( identifier: string ) => cache.user.get( identifier )
export const getUsers = () => Array.from( cache.user.values() )

// Guilds
export const updateGuild = ( guild: Guild ) => cache.guild.set( guild.id, { ...cache.guild.get( guild.id ), ...guild } ).get( guild.id )!
export const getGuild = ( identifier: string ) => cache.guild.get( identifier )
export const getGuilds = () => Array.from( cache.guild.values() )
