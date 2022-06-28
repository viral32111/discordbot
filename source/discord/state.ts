import { User } from "./types.js"

const cache = {
	users: new Map<string, User>()
}

export function updateUser( user: User ) {
	cache.users.set( user.id, { ...cache.users.get( user.id ), ...user } )

	return cache.users.get( user.id )!
}
