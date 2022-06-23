export enum OperationCode {
	Continuation = 0,
	Text = 1,
	Binary = 2,
	Close = 8,
	Ping = 9,
	Pong = 10
}

export enum CloseCode {
	Normal = 1000,
	GoingAway = 1001,
	ProtocolError = 1002,
	NotSupported = 1003,
	InconsistentData = 1007,
	PolicyViolation = 1008,
	MessageTooLarge = 1009,
	ExtensionNotAccepted = 1010,
	UnexpectedCondition = 1011
}
