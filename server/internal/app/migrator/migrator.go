package migrator

import (
	"filetransfer/internal/app/migrator/templates"
	"filetransfer/internal/pkg/config"
	"fmt"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/mysql"
)

const (
	VersionInitial = "initial"
)

type Migrator struct {
	_version string
	_gorm    *gorm.DB
}

func (m *Migrator) Execute() {
	var err error
	switch m._version {
	case VersionInitial:
		err = (&templates.Initial{}).Execute(m._gorm)
	}
	buildOutput(err)
}

func New(conf *config.Config, version string) (*Migrator, error) {
	db, err := gorm.Open("mysql", buildMySQLURL(&conf.Database))
	if err != nil {
		return nil, err
	}
	return &Migrator{
		_version: version,
		_gorm:    db,
	}, nil
}

func buildOutput(err error) {
	if err != nil {
		fmt.Println("Migrate failed!")
		fmt.Printf("error: %v\n", err)
	} else {
		fmt.Println("Migrate successful!")
	}
}

func buildMySQLURL(conf *config.DatabaseConfig) string {
	return fmt.Sprintf("%s:%s@(%s:%d)/%s?charset=utf8mb4&parseTime=True&loc=Local", conf.User, conf.Pass, conf.Host, conf.Port, conf.Name)
}

type Template interface {
	Execute(db *gorm.DB) error
}
