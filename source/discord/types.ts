import { format } from "util"

// https://discord.com/developers/docs/resources/user#user-object-user-structure
/*export interface User {
	id: string,
	username: string,
	discriminator: string,
	avatar?: string,
	bot?: boolean,
	system?: boolean,
	mfa_enabled?: boolean,
	banner?: string,
	accent_color?: number,
	locale?: string,
	verified?: boolean,
	email?: string,
	flags?: number,
	premium_type?: number,
	public_flags?: number
}*/

// https://discord.com/developers/docs/reference#snowflakes
export class Snowflake {
	public readonly Value: BigInt

	public readonly Timestamp: Date
	public readonly Worker: number
	public readonly Process: number
	public readonly Increment: number

	constructor( identifier: string ) {
		this.Value = BigInt( identifier )

		// TODO
		this.Timestamp = new Date( 0 )
		this.Worker = 0
		this.Process = 0
		this.Increment = 0
	}

	public valueOf() { return this.Value }
	public toString() { return this.Value.toString() }
}

// https://discord.com/developers/docs/resources/user#user-object-user-structure
export class User {
	public Identifier!: Snowflake

	public Name!: string
	public Discriminator!: number

	public Avatar?: string

	constructor( data: any ) {
		this.Update( data )
	}

	public Update( data: any ) {
		this.Identifier = new Snowflake( data[ "id" ] )

		this.Name = data[ "username" ]
		this.Discriminator = Number( data[ "discriminator" ] )

		this.Avatar = data[ "avatar" ]
	}

	// https://discord.com/developers/docs/reference#image-formatting
	public AvatarUrl( size: number, animated: boolean ) {
		if ( !size ) size = 512

		return format( "https://cdn.discordapp.com/avatars/%d/%s.%s?size=", this.Identifier, this.Avatar, ( animated === true ? "gif" : "png" ), size )
	}
}

// https://discord.com/developers/docs/resources/application#application-object
export interface Application {
	id: string,
	flags: number
	// TODO
}

// https://discord.com/developers/docs/resources/guild#guild-object
export interface Guild {
	id: string,
	name: string,
	// TODO
}
