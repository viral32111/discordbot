// https://discord.com/developers/docs/topics/gateway#get-gateway-bot-json-response
export interface Get {
	url: string,
	shards: number,
	session_start_limit: any
}

// https://discord.com/developers/docs/topics/gateway#payloads-gateway-payload-structure
export interface Payload {
	op: OperationCode,
	d?: any,
	s?: number,
	t?: string,
}

// https://discord.com/developers/docs/topics/opcodes-and-status-codes#gateway-gateway-opcodes
export enum OperationCode {
	Dispatch = 0,
	Heartbeat = 1, // Command (sent by client)
	Identify = 2, // Command (sent by client)
	PresenceUpdate = 3, // Command (sent by client)
	VoiceStateUpdate = 4, // Command (sent by client)
	Resume = 6, // Command (sent by client)
	Reconnect = 7,
	RequestGuildMembers = 8, // Command (sent by client)
	InvalidSession = 9,
	Hello = 10,
	HeartbeatAcknowledgement = 11
}

// https://discord.com/developers/docs/topics/gateway#update-presence-status-types
export enum StatusType {
	Online = "online",
	Idle = "idle",
	DoNotDisturb = "dnd",
	Invisible = "invisible",
	Offline = "offline"
}

// https://discord.com/developers/docs/topics/gateway#activity-object-activity-types
export enum ActivityType {
	Playing = 0, // Game
	Streaming = 1,
	Listening = 2,
	Watching = 3,
	Custom = 4, // Cannot be used by bots
	Competing = 5
}

// https://discord.com/developers/docs/topics/gateway#activity-object-activity-structure
export interface Activity {
	name: string,
	type: ActivityType,
	url?: string,
	created_at?: number,
	timestamps?: any, // TODO
	application_id?: string,
	details?: string,
	state?: string,
	emoji?: any, // TODO
	party?: any, // TODO
	assets?: any, // TODO
	secrets?: any, // TODO
	instance?: boolean,
	flags?: number,
	buttons?: any[] // TODO
}

// https://discord.com/developers/docs/topics/gateway#commands-and-events-gateway-events
// This is ONLY dispatched events, it does NOT include server-to-client events already defined in OperationCode
export enum DispatchEvent {
	Ready = "READY", // Contains the initial state information
	Resumed = "RESUMED", // Response to Resume (Opcode 6)
	GuildCreate = "GUILD_CREATE" // Lazy-load for unavailable guild, guild became available, or user joined a new guild
}
