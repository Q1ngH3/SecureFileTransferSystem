package middlewares

import (
	"filetransfer/internal/app/server/errors"
	"filetransfer/internal/pkg/jwt"
	"filetransfer/internal/pkg/models"
	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	"net/http"
	"strings"
)

func Auth(signKey string) gin.HandlerFunc {
	return func(c *gin.Context) {
		j := jwt.NewJWT(signKey)
		c.Set("jwt", j)
		token := c.Request.Header.Get("Authorization")
		if token != "" {
			s := strings.Split(token, " ")
			if len(s) == 2 {
				if s[0] != "JWT" && s[0] != "jwt" {
					c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
						"error_code": errors.CodeNotSupportedAuthorization,
						"error":      "Please Login",
					})
					return
				}
				token = s[1]
				claims, err := j.ParseToken(token)
				if err != nil {
					c.AbortWithStatusJSON(http.StatusBadRequest, gin.H{
						"error_code": errors.CodeTokenError,
						"error":      "Please Login",
					})
					return
				}
				db := c.MustGet("db").(*gorm.DB)
				var user models.User
				if v := db.Where(&models.User{
					ID: claims.UserID,
				}).First(&user); v.Error != nil {
					panic(v.Error)
				}

				if user.Active == false {
					c.AbortWithStatusJSON(http.StatusOK, gin.H{
						"error_code": errors.CodeUserNotActive,
						"error":      "not an active user, please check your email",
					})
				}
				c.Set("user", &user)
			}
		}
		c.Next()
	}
}
