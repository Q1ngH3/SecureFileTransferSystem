package users

import (
	"filetransfer/internal/app/server/middlewares"
	"github.com/gin-gonic/gin"
)

func RegisterRouter(g *gin.Engine) {
	h := &Handler{}
	g.POST("/login", h.Login())
	g.POST("/register", h.Register())
	g.GET("/logout", middlewares.RequireLogin(), h.Logout())
	g.POST("/update_info", middlewares.RequireLogin(), h.UpdateInfo())
	g.GET("/whoami", middlewares.RequireLogin(), h.Whoami())
	g.GET("/heartbeat", middlewares.RequireLogin(), h.HeartBeat())
	g.POST("/active", h.Active())
}
