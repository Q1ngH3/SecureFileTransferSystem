package users

type UserInput struct {
	Username string `json:"username"`
	Password string `json:"password"`
	Email    string `json:"email"`
}

type UserInfo struct {
	PublicKey  string `json:"public_key"`
	RemoteAddr string `json:"remote_addr"`
	RemotePort uint   `json:"remote_port"`
}
