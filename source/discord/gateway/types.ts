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

// https://discord.com/developers/docs/topics/gateway#list-of-intents
export enum Intents {
	Guilds = 1 << 0,
	GuildMembers = 1 << 1,
	GuildBans = 1 << 2,
	GuildEmojisStickers = 1 << 3,
	GuildIntegrations = 1 << 4,
	GuildWebhooks = 1 << 5,
	GuildInvites = 1 << 6,
	GuildVoiceStates = 1 << 7,
	GuildPresences = 1 << 8,
	GuildMessages = 1 << 9,
	GuildMessageReactions = 1 << 10,
	GuildMessageTyping = 1 << 11,
	DirectMessages = 1 << 12,
	DirectMessageReactions = 1 << 13,
	DirectMessageTyping = 1 << 14,
	MessageContent = 1 << 15,
	GuildScheduledEvents = 1 << 16,
	AutoModerationConfiguration = 1 << 20,
	AutoModerationExecution = 1 << 21,

	All = Guilds | GuildMembers | GuildBans | GuildEmojisStickers | GuildIntegrations | GuildWebhooks | GuildIntegrations | GuildVoiceStates | GuildPresences | GuildMessages | GuildMessageReactions | GuildMessageTyping | DirectMessages | DirectMessageReactions | DirectMessageTyping | MessageContent | GuildScheduledEvents | AutoModerationConfiguration | AutoModerationExecution
}
