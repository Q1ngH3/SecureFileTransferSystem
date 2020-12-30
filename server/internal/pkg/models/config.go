package models

import "time"

const (
	TableConfig = "config"
)

type Config struct {
	ID        uint   `gorm:"primary_key"`
	Key       string `gorm:"size:50"`
	Value     string `gorm:"type:longtext"`
	CreatedAt time.Time
	UpdatedAt time.Time
}

func (c *Config) TableName() string {
	return TableConfig
}
