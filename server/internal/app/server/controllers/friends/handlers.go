package friends

import (
	"filetransfer/internal/app/server/errors"
	"filetransfer/internal/pkg/models"
	"github.com/gin-gonic/gin"
	"github.com/jinzhu/gorm"
	"net/http"
)

type Handler struct {
}

func (*Handler) List() gin.HandlerFunc {
	return func(c *gin.Context) {
		var friendsList []models.Friends
		user := c.MustGet("user").(*models.User)
		db := c.MustGet("db").(*gorm.DB)
		db.Where(models.Friends{UserID: user.ID, Available: true}).Preload("Friend").Preload("User").Find(&friendsList)
		c.JSON(http.StatusOK, gin.H{
			"error_code": 0,
			"friends":    friendsList,
		})
	}
}

func (*Handler) Add() gin.HandlerFunc {
	return func(c *gin.Context) {
		var Input struct {
			Username string `json:"username"`
		}
		db := c.MustGet("db").(*gorm.DB)
		user := c.MustGet("user").(*models.User)
		err := c.ShouldBindJSON(&Input)
		if err != nil {
			panic(err)
		}
		if Input.Username == user.Username {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeNotFound,
				"error":      "Are you kidding me ?",
			})
			return
		}
		var FriendUser models.User
		var count uint
		db.Where("username = ? AND active=1", Input.Username).Find(&FriendUser).Count(&count)

		if count != 1 {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeNotFound,
				"error":      "No Such User",
			})
			return
		}
		var Friend models.Friends
		db.Where("friend_id = ? AND user_id=?", user.ID, FriendUser.ID).Find(&models.Friends{}).Count(&count)
		if count != 0 {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeUserDuplicate,
				"error":      "Already Added",
			})
			return
		}
		db.Where("friend_id = ? AND user_id=?", FriendUser.ID, user.ID).Find(&Friend).Count(&count)
		if count != 0 {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeUserDuplicate,
				"error":      "Already Added",
			})
			return
		}
		Friend.UserID = user.ID
		Friend.FriendID = FriendUser.ID
		if v := db.Create(&Friend); v.Error != nil {
			panic(v.Error)
		}
		c.JSON(http.StatusOK, gin.H{
			"error_code": 0,
		})

	}
}

func (*Handler) Query() gin.HandlerFunc {
	return func(c *gin.Context) {
		db := c.MustGet("db").(*gorm.DB)
		var input struct {
			Id uint `uri:"id" binding:"required" example:"0" format:"uint"`
		}
		err := c.ShouldBindUri(&input)
		if err != nil {
			panic(err)
		}
		var friend models.Friends
		var count uint
		db.Where(&models.Friends{ID: input.Id, Available: true}).
			Preload("Friend").Preload("User").Find(&friend).Count(&count)
		if count > 0 {
			c.JSON(http.StatusOK, gin.H{
				"error_code": 0,
				"friend":     friend,
			})
			return
		} else {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeNotFound,
			})
			return
		}
	}
}

func (*Handler) Delete() gin.HandlerFunc {
	return func(c *gin.Context) {
		var input struct {
			ID uint `json:"relation_id"`
		}
		//user := c.MustGet("user").(*models.User)
		db := c.MustGet("db").(*gorm.DB)

		err := c.ShouldBindJSON(&input)
		if err != nil {
			panic(err)
		}

		var FriendUser models.Friends
		var count uint
		db.Where(&models.Friends{ID: input.ID}).Find(&FriendUser).Count(&count)
		if count == 1 {
			db.Delete(&FriendUser)
			c.JSON(http.StatusOK, gin.H{
				"error_code": 0,
			})
			return
		} else {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeNotFound,
				"error":      "No such Friend",
			})
		}
	}
}

func (*Handler) GetAllRequest() gin.HandlerFunc {
	return func(c *gin.Context) {
		var reqList []models.Friends
		user := c.MustGet("user").(*models.User)
		db := c.MustGet("db").(*gorm.DB)
		db.Preload("User").Preload("Friend").Where("available = 0 AND friend_id = ?", user.ID).Find(&reqList)
		c.JSON(http.StatusOK, gin.H{
			"error_code":   0,
			"request_list": reqList,
		})
	}
}

func (*Handler) CommitRequest() gin.HandlerFunc {
	return func(c *gin.Context) {
		var input struct {
			RelationID uint `json:"relation_id"`
		}
		err := c.ShouldBindJSON(&input)
		if err != nil {
			panic(err)
		}
		user := c.MustGet("user").(*models.User)
		db := c.MustGet("db").(*gorm.DB)
		var originRelation models.Friends
		var count uint
		db.Where("id = ? AND available = 0", input.RelationID).Find(&originRelation).Count(&count)
		if count != 1 {
			c.JSON(http.StatusOK, gin.H{
				"error_code": errors.CodeNotFound,
				"error":      "Relation Not Found",
			})
			return
		} else {
			originRelation.Available = true
			newRelation := models.Friends{
				UserID:    user.ID,
				FriendID:  originRelation.UserID,
				Available: true,
			}
			db.Save(&originRelation)
			db.Save(&newRelation)
			c.JSON(http.StatusOK, gin.H{
				"error_code": 0,
			})
			return
		}
	}
}
