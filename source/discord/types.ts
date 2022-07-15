import { format } from "util"

import { DISCORD_CDN_URL } from "../config.js"
import { request } from "./api.js"
import { Gateway } from "./gateway/gateway.js"

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
	// @ts-ignore
	private client: Gateway

	public Identifier!: Snowflake

	public Name!: string
	public Discriminator!: number

	public Avatar?: string

	public IsBot?: boolean
	public IsSystem?: boolean
	
	public PrivateFlags?: number
	public PublicFlags?: number

	public PremiumType?: number

	constructor( data: any, client: Gateway ) {
		this.client = client

		this.Update( data )
	}

	public Update( data: any ) {
		this.Identifier = new Snowflake( data[ "id" ] )

		this.Name = data[ "username" ]
		this.Discriminator = Number( data[ "discriminator" ] )

		this.Avatar = data[ "avatar" ]

		this.IsBot = ( data[ "bot" ] === true )
		this.IsSystem = ( data[ "system" ] === true )

		if ( data[ "flags" ] ) this.PrivateFlags = Number( data[ "flags" ] )
		if ( data[ "public_flags" ] ) this.PublicFlags = Number( data[ "public_flags" ] )

		if ( data[ "premium_type" ] ) this.PremiumType = Number( data[ "premium_type" ] )
	}

	// https://discord.com/developers/docs/reference#image-formatting
	public AvatarUrl( size = 512, animated = true, extension = "png" ) {
		if ( this.Avatar ) {
			return format( "https://%s/avatars/%d/%s.%s?size=%d", DISCORD_CDN_URL, this.Identifier, this.Avatar, ( animated && this.Avatar.startsWith( "a_" ) ? "gif" : extension ), size )
		} else {
			return format( "https://%s/embed/avatars/%d.png?size=%d", DISCORD_CDN_URL, this.Discriminator % 5, size )
		}
	}
}

// https://discord.com/developers/docs/resources/channel#message-object
export class Message {
	// @ts-ignore
	private client: Gateway

	public identifier!: Snowflake

	public content!: string

	//public channel: Channel
	private channelId!: Snowflake

	constructor( data: any, client: Gateway ) {
		this.client = client

		this.update( data )
	}

	public update( data: any ) {
		this.identifier = new Snowflake( data[ "id" ] )

		this.content = data[ "content" ]

		//this.channel = getChannel( data[ "channel_id" ] )
		this.channelId = new Snowflake( data[ "channel_id" ] )
	}

	public async reply( content: string ) {
		await request( format( "channels/%s/messages", this.channelId ), "POST", {
			"content": content,
			"message_reference": {
				"message_id": this.identifier.toString(),
				"fail_if_not_exists": true
			}
		} )
	}
}
