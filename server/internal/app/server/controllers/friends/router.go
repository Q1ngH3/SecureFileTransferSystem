package friends

import (
	"filetransfer/internal/app/server/middlewares"
	"github.com/gin-gonic/gin"
)

func RegisterRouter(g *gin.Engine) {
	h := &Handler{}
	g.GET("/friends/list", middlewares.RequireLogin(), h.List())
	g.POST("/friends/add", middlewares.RequireLogin(), h.Add())
	g.POST("/friends/delete", middlewares.RequireLogin(), h.Delete())
	g.GET("/friends/query/:id", middlewares.RequireLogin(), h.Query())
	g.GET("/friends/request/list", middlewares.RequireLogin(), h.GetAllRequest())
	g.POST("/friends/request/commit", middlewares.RequireLogin(), h.CommitRequest())
}
