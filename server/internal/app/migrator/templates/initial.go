package templates

import (
	"filetransfer/internal/pkg/models"
	"github.com/jinzhu/gorm"
)

type Initial struct {
}

func (t *Initial) Execute(db *gorm.DB) error {
	db = db.Begin()
	if v := db.AutoMigrate(&models.Config{}); v.Error != nil {
		db.Rollback()
		return v.Error
	}
	if v := db.AutoMigrate(&models.User{}); v.Error != nil {
		db.Rollback()
		return v.Error
	}
	if v := db.AutoMigrate(&models.Friends{}); v.Error != nil {
		db.Rollback()
		return v.Error
	}
	if v := db.Commit(); v.Error != nil {
		db.Rollback()
		return v.Error
	}
	return nil
}
