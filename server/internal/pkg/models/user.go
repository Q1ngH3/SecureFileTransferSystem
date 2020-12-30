package models

import "time"

const (
	TableUser = "user"
)

type User struct {
	ID             uint       `gorm:"primary_key" json:"user_id,omitempty"`
	Email          string     `gorm:"size:100" json:"email"`
	Username       string     `gorm:"size:50" json:"username"`
	Password       string     `gorm:"size:50" json:"-"`
	OnlineStatus   bool       `json:"online_status"`
	PublicKey      string     `gorm:"size:1000" json:"public_key"`
	RemoteAddr     string     `gorm:"size:50" json:"remote_addr"`
	RemotePort     uint       `json:"remote_port"`
	CaptchaCode    string     `json:"-"`
	Active         bool       `json:"-"`
	LastActiveTime *time.Time `json:"last_active_time" `
	CreatedAt      *time.Time `json:"-"`
	UpdatedAt      *time.Time `json:"-"`
}

func (u *User) TableName() string {
	return TableUser
}
