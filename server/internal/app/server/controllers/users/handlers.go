package users

import (
	//"encoding/json"
	"filetransfer/internal/app/server/errors"
	config2 "filetransfer/internal/pkg/config"
	"filetransfer/internal/pkg/jwt"
	"filetransfer/internal/pkg/models"
	"filetransfer/internal/pkg/random"
	"filetransfer/internal/pkg/smtp"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	"net/http"
	"time"
)

type Handler struct {
}

func (*Handler) Login() gin.HandlerFunc {
	return func(c *gin.Context) {
		db := c.MustGet("db").(*gorm.DB)
		var UserInput UserInput
		err := c.ShouldBindJSON(&UserInput)
		if err != nil {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeInvalidBody,
			})
			return
		}
		var count int
		var user models.User

		db.Where(&models.User{Username: UserInput.Username, Password: UserInput.Password, Active: true}).First(&user).Count(&count)
		if count == 1 {
			// 更改在线状态
			user.OnlineStatus = true
			*user.LastActiveTime = time.Now()
			db.Save(&user)

			j := c.MustGet("jwt").(*jwt.JWT)
			auth, _ := j.CreateToken(jwt.CustomClaims{
				UserID: user.ID,
			})
			c.JSON(http.StatusOK, gin.H{
				"error_code": 0,
				"auth":       auth,
			})
		} else {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeNotFound,
				"error":      "No Such User",
			})
		}

	}
}

func (*Handler) Register() gin.HandlerFunc {
	return func(c *gin.Context) {
		db := c.MustGet("db").(*gorm.DB)
		var userInput UserInput
		err := c.ShouldBindJSON(&userInput)
		if err != nil {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeInvalidBody,
			})
			return
		}
		var count int
		var user models.User
		db.Where("username = ?", userInput.Username).Find(&user).Count(&count)
		if count == 0 {
			time := time.Now()
			user.Username = userInput.Username
			user.Password = userInput.Password
			user.Email = userInput.Email
			user.LastActiveTime = &time
			user.CaptchaCode = random.String(5, "0123456789")
			user.ID = 0
			user.Active = false
			go func() {
				config := c.MustGet("config").(*config2.Config)
				smtpClient := c.MustGet("smtp").(*smtp.Smtp)
				err := smtpClient.SendToMail(
					userInput.Email,
					"FileTransfer Register",
					fmt.Sprintf(config.SMTP.Template, user.CaptchaCode),
					"",
				)
				if err != nil {
					panic(err)
				}
			}()
			if v := db.Create(&user); v.Error != nil {
				panic(v.Error)
			}
			c.JSON(http.StatusOK, gin.H{
				"error_code": 0,
			})
			return
		} else {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeUserDuplicate,
				"error":      "User Duplicated",
			})
			return
		}
	}
}

func (*Handler) Logout() gin.HandlerFunc {
	return func(c *gin.Context) {
		user := c.MustGet("user").(*models.User)
		db := c.MustGet("db").(*gorm.DB)
		user.OnlineStatus = false
		if v := db.Save(user); v.Error != nil {
			panic(v.Error)
		}
		c.JSON(http.StatusOK, gin.H{
			"error_code": 0,
		})
	}
}

func (*Handler) Whoami() gin.HandlerFunc {
	return func(c *gin.Context) {
		var user *models.User
		user = c.MustGet("user").(*models.User)
		c.JSON(http.StatusOK, gin.H{
			"error_code": 0,
			"user":       user,
		})
	}
}

func (*Handler) UpdateInfo() gin.HandlerFunc {
	return func(c *gin.Context) {
		db := c.MustGet("db").(*gorm.DB)
		user := c.MustGet("user").(*models.User)
		var Input UserInfo
		err := c.ShouldBindJSON(&Input)
		if err != nil {
			panic(err)
		}
		user.PublicKey = Input.PublicKey
		user.RemoteAddr = Input.RemoteAddr
		user.RemotePort = Input.RemotePort
		if v := db.Save(user); v.Error != nil {
			panic(v.Error)
		}
		c.JSON(http.StatusOK, gin.H{
			"error_code": 0,
			"user":       user,
		})
	}
}

func (*Handler) HeartBeat() gin.HandlerFunc {
	return func(c *gin.Context) {
		db := c.MustGet("db").(*gorm.DB)
		user := c.MustGet("user").(*models.User)
		*user.LastActiveTime = time.Now()
		db.Save(user)
		c.JSON(http.StatusOK, gin.H{
			"error_code": 0,
		})
	}
}

func (*Handler) Active() gin.HandlerFunc {
	return func(c *gin.Context) {
		db := c.MustGet("db").(*gorm.DB)
		input := struct {
			Username    string `json:"username"`
			CaptchaCode string `json:"captcha_code"`
		}{}
		err := c.ShouldBindJSON(&input)
		if err != nil {
			panic(err)
		}
		var user models.User
		var count uint
		db.Find(&models.User{Username: input.Username}).Find(&user).Count(&count)
		if count != 1 {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeNotFound,
				"error":      "No Such User",
			})
			return
		} else {
			if user.Active == true {
				c.JSON(http.StatusOK, gin.H{
					"error_code": errors.CodeForbidden,
					"error":      "user is active already",
				})
				return
			} else {
				user.Active = true
				db.Save(&user)
				c.JSON(http.StatusOK, gin.H{
					"error_code": 0,
				})
			}
		}

	}
}
