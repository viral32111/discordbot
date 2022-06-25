// Codes to identify the types of frames
// https://www.rfc-editor.org/rfc/rfc6455.html#section-5.2
export enum OperationCode {
	Continuation = 0,
	Text = 1,
	Binary = 2,
	Close = 8,
	Ping = 9,
	Pong = 10
}

// Codes to identify reasons for disconnecting
// https://www.rfc-editor.org/rfc/rfc6455.html#section-7.4
export enum CloseCode {
	Normal = 1000,
	GoingAway = 1001,
	ProtocolError = 1002,
	NotSupported = 1003,
	// 1004, 1005, and 1006 are reserved
	InconsistentData = 1007,
	PolicyViolation = 1008,
	MessageTooLarge = 1009,
	ExtensionNotAccepted = 1010,
	UnexpectedCondition = 1011
	// 1015 is reserved
}
