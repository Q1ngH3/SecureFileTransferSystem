package middlewares

import (
	"filetransfer/internal/pkg/config"
	"github.com/gin-gonic/gin"
)

func SetConfig(_config *config.Config) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Set("config", _config)
	}
}
