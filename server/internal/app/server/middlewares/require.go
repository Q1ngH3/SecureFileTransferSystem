package middlewares

import (
	"filetransfer/internal/app/server/errors"
	//"filetransfer/internal/pkg/models"
	"github.com/gin-gonic/gin"
	"net/http"
)

const (
	ResourceOverall = iota
	ResourceReserve
	RoleStudent = iota
	RoleAdmin
)

// default role -> student
func RequireLogin() gin.HandlerFunc {
	return func(c *gin.Context) {
		_, ok := c.Get("user")
		if !ok {
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{
				"error_code": errors.CodeForbidden,
			})
			return
		}
		c.Next()
	}
}
