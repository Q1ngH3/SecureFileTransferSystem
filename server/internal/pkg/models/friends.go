package models

const (
	TableFriends = "friends"
)

type Friends struct {
	ID        uint `gorm:"primary_key" json:"relation_id"`
	UserID    uint `json:"-"`
	User      User `json:"main_user"`
	Friend    User `json:"friend"`
	FriendID  uint `json:"-"`
	Available bool `json:"available"`
}

func (u *Friends) Friends() string {
	return TableFriends
}
