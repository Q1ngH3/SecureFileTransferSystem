package config

import (
	"encoding/json"
	"io/ioutil"
	"os"
)

type Config struct {
	Port     uint           `json:"port"`
	Database DatabaseConfig `json:"database"`
	Redis    RedisConfig    `json:"redis"`
	SMTP     SMTPConfig     `json:"smtp"`
}

type SMTPConfig struct {
	Address  string `json:"address"`
	Username string `json:"username"`
	Password string `json:"password"`
	Template string `json:"template"`
}

type RedisConfig struct {
	Address  string `json:"address"`
	Password string `json:"password"`
	DB       int    `json:"db"`
}

type DatabaseConfig struct {
	Host string `json:"host"`
	Port uint   `json:"port"`
	User string `json:"user"`
	Pass string `json:"pass"`
	Name string `json:"name"`
}

func Load(path string) *Config {
	var conf Config
	f, err := os.Open(path)
	if err != nil {
		panic(err)
	}
	ctx, err := ioutil.ReadAll(f)
	if err != nil {
		panic(err)
	}
	err = json.Unmarshal(ctx, &conf)
	if err != nil {
		panic(err)
	}
	return &conf
}
