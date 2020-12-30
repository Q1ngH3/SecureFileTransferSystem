package main

import (
	"filetransfer/internal/app/server"
	"filetransfer/internal/pkg/config"
)

func main() {
	conf := config.Load("./configs/server.json")
	s := server.NewServer(conf)
	s.Start()
}
