package main

import (
	"filetransfer/internal/app/migrator"
	"filetransfer/internal/pkg/config"
	"flag"
)

func main() {
	template := flag.String("template", "initial", "The template that migration applies")
	flag.Parse()
	m, err := migrator.New(config.Load("./configs/server.json"), *template)
	if err != nil {
		panic(err)
	}
	m.Execute()
}
