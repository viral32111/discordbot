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
	Heartbeat = 1,
	Identify = 2,
	PresenceUpdate = 3,
	VoiceStateUpdate = 4,
	Resume = 6,
	Reconnect = 7,
	RequestGuildMembers = 8,
	InvalidSession = 9,
	Hello = 10,
	HeartbeatAcknowledgement = 11
}
