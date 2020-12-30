package middlewares

import (
	"context"
	"filetransfer/internal/pkg/models"
	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	"strconv"
)

func HeartBeat() gin.HandlerFunc {
	return func(c *gin.Context) {
		ctx := context.Background()
		obj := c.MustGet("user")
		if obj != nil {
			user := obj.(models.User)
			redisClient := c.MustGet("redis").(*redis.Client)
			redisClient.Set(ctx, strconv.Itoa(int(user.ID)), "Active", 60)
		}
	}
}
