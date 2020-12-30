package middlewares

import (
	"filetransfer/internal/app/server/errors"
	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	"net/http"
)

func Recovery() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				db, ok := c.Get("db")
				if ok {
					db.(*gorm.DB).RollbackUnlessCommitted()
				}
				c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
					"error_code": errors.CodeServerError,
					"error":      err,
				})
				// log
			}
		}()
		c.Next()
	}
}
