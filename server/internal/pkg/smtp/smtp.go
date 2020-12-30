package smtp

import (
	"net/smtp"
	"strings"
)

type Smtp struct {
	server   string
	username string
	password string
}

func NewSmtp(server string, username string, password string) *Smtp {
	return &Smtp{server: server, username: username, password: password}
}

func (s *Smtp) SendToMail(to, subject, body, mailType string) error {
	hp := strings.Split(s.server, ":")
	auth := smtp.PlainAuth("", s.username, s.password, hp[0])
	var contentType string
	if mailType == "html" {
		contentType = "Content-Type: text/" + mailType + "; charset=UTF-8"
	} else {
		contentType = "Content-Type: text/plain" + "; charset=UTF-8"
	}

	msg := []byte("To: " + to + "\r\nFrom: " + s.username + "\r\nSubject: " + subject + "\r\n" + contentType + "\r\n\r\n" + body)
	sendTo := strings.Split(to, ";")
	err := smtp.SendMail(s.server, auth, s.username, sendTo, msg)
	return err
}
