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

// https://discord.com/developers/docs/topics/opcodes-and-status-codes#gateway-gateway-opcodes
export enum OperationCode {
	Dispatch = 0,
	Heartbeat = 1,
	Reconnect = 7,
	InvalidSession = 9,
	Hello = 10,
	HeartbeatAcknowledgement = 11
}

// https://discord.com/developers/docs/topics/gateway#commands-and-events-gateway-commands
export enum Command {
	Heartbeat = 1,
	Identify = 2,
	PresenceUpdate = 3,
	VoiceStateUpdate = 4,
	Resume = 6,
	RequestGuildMembers = 8,
}

// https://discord.com/developers/docs/topics/gateway#commands-and-events-gateway-events
export enum Event {
	Ready = "READY", // Contains the initial state information
	Resumed = "RESUMED", // Response to Opcode 6 Resume
	ApplicationCommandPermissionsUpdate = "APPLICATION_COMMAND_PERMISSIONS_UPDATE",
	AutoModerationRuleCreate = "AUTO_MODERATION_RULE_CREATE",
	AutoModerationRuleUpdate = "AUTO_MODERATION_RULE_UPDATE",
	AutoModerationRuleDelete = "AUTO_MODERATION_RULE_DELETE",
	AutoModerationActionExecution = "AUTO_MODERATION_ACTION_EXECUTION",
	ChannelCreate = "CHANNEL_CREATE",
	ChannelUpdate = "CHANNEL_UPDATE",
	ChannelDelete = "CHANNEL_DELETE",
	ChannelPinsUpdate = "CHANNEL_PINS_UPDATE",
	ThreadCreate = "THREAD_CREATE",
	ThreadUpdate = "THREAD_UPDATE",
	ThreadDelete = "THREAD_DELETE",
	ThreadListSync = "THREAD_LIST_SYNC",
	ThreadMemberUpdate = "THREAD_MEMBER_UPDATE",
	ThreadMembersUpdate = "THREAD_MEMBERS_UPDATE",
	GuildCreate = "GUILD_CREATE",
	GuildUpdate = "GUILD_UPDATE",
	GuildDelete = "GUILD_DELETE",
	GuildBanAdd = "GUILD_BAN_ADD",
	GuildBanRemove = "GUILD_BAN_REMOVE",
	GuildEmojisUpdate = "GUILD_EMOJIS_UPDATE",
	GuildStickersUpdate = "GUILD_STICKERS_UPDATE",
	GuildIntegrationsUpdate = "GUILD_INTEGRATIONS_UPDATE",
	GuildMemberAdd = "GUILD_MEMBER_ADD",
	GuildMemberRemove = "GUILD_MEMBER_REMOVE",
	GuildMemberUpdate = "GUILD_MEMBER_UPDATE",
	GuildMembersChunk = "GUILD_MEMBERS_CHUNK",
	GuildRoleCreate = "GUILD_ROLE_CREATE",
	GuildRoleUpdate = "GUILD_ROLE_UPDATE",
	GuildRoleDelete = "GUILD_ROLE_DELETE",
	GuildScheduledEventCreate = "GUILD_SCHEDULED_EVENT_CREATE",
	GuildScheduledEventUpdate = "GUILD_SCHEDULED_EVENT_UPDATE",
	GuildScheduledEventDelete = "GUILD_SCHEDULED_EVENT_DELETE",
	GuildScheduledEventUserAdd = "GUILD_SCHEDULED_EVENT_USER_ADD",
	GuildScheduledEventUserRemove = "GUILD_SCHEDULED_EVENT_USER_REMOVE",
	IntegrationCreate = "INTEGRATION_CREATE",
	IntegrationUpdate = "INTEGRATION_UPDATE",
	IntegrationDelete = "INTEGRATION_DELETE",
	InteractionCreate = "INTERACTION_CREATE",
	InviteCreate = "INVITE_CREATE",
	InviteDelete = "INVITE_DELETE",
	MessageCreate = "MESSAGE_CREATE",
	MessageUpdate = "MESSAGE_UPDATE",
	MessageDelete = "MESSAGE_DELETE",
	MessageDeleteBulk = "MESSAGE_DELETE_BULK",
	MessageReactionAdd = "MESSAGE_REACTION_ADD",
	MessageReactionRemove = "MESSAGE_REACTION_REMOVE",
	MessageReactionRemoveAll = "MESSAGE_REACTION_REMOVE_ALL",
	MessageReactionRemoveEmoji = "MESSAGE_REACTION_REMOVE_EMOJI",
	PresenceUpdate = "PRESENCE_UPDATE",
	StageInstanceCreate = "STAGE_INSTANCE_CREATE",
	StageInstanceDelete = "STAGE_INSTANCE_DELETE",
	StageInstanceUpdate = "STAGE_INSTANCE_UPDATE",
	TypingStart = "TYPING_START",
	UserUpdate = "USER_UPDATE",
	VoiceStateUpdate = "VOICE_STATE_UPDATE",
	VoiceServerUpdate = "VOICE_SERVER_UPDATE",
	WebhooksUpdate = "WEBHOOKS_UPDATE"
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
