package middlewares

import (
	"filetransfer/internal/pkg/smtp"
	"github.com/gin-gonic/gin"
)

func SetSmtp(_smtp *smtp.Smtp) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Set("smtp", _smtp)
	}
}
