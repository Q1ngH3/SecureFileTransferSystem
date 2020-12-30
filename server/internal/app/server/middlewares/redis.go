package middlewares

import (
	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
)

func SetRedis(client *redis.Client) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Set("redis", client)
		c.Next()
	}
}
