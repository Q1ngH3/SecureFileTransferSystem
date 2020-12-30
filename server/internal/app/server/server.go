package server

import (
	"context"
	"filetransfer/internal/app/server/controllers/friends"
	"filetransfer/internal/app/server/controllers/users"
	"filetransfer/internal/app/server/middlewares"
	"filetransfer/internal/pkg/config"
	"filetransfer/internal/pkg/random"
	"filetransfer/internal/pkg/smtp"
	"fmt"
	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	"github.com/jinzhu/gorm"
	_ "github.com/jinzhu/gorm/dialects/mysql"
	"os"
)

const (
	DebugMode   = "debug"
	ReleaseMode = "release"
)

type Server struct {
	_gin    *gin.Engine
	_gorm   *gorm.DB
	_conf   *config.Config
	_redis  *redis.Client
	_smtp   *smtp.Smtp
	signKey string
}

func (s *Server) setRouter() {
	users.RegisterRouter(s._gin)
	friends.RegisterRouter(s._gin)
}

func (s *Server) initGin() {
	s._gin = gin.New()
	gin.SetMode(getMode())
	s._gin.Use(gin.Logger())
	s._gin.Use(middlewares.Recovery())
	s._gin.Use(middlewares.SetConfig(s._conf))
	s._gin.Use(middlewares.SetDB(s._gorm))
	s._gin.Use(middlewares.SetSmtp(s._smtp))
	s._gin.Use(middlewares.Auth(s.signKey))
	s.setRouter()
}

func (s *Server) initGorm() {
	var err error
	s._gorm, err = gorm.Open("mysql", buildMySQLURL(&s._conf.Database))
	if err != nil {
		panic(err)
	}
}

func (s *Server) initSmtp() {
	s._smtp = smtp.NewSmtp(s._conf.SMTP.Address, s._conf.SMTP.Username, s._conf.SMTP.Password)
}

func (s *Server) initRedis() {
	ctx := context.Background()
	s._redis = redis.NewClient(&redis.Options{
		Addr:     s._conf.Redis.Address,
		Password: s._conf.Redis.Password,
		DB:       s._conf.Redis.DB,
	})
	_, err := s._redis.Ping(ctx).Result()
	if err != nil {
		panic(err)
	}
}

func (s *Server) run() {
	var err error
	err = s._gin.Run(fmt.Sprintf("0.0.0.0:%d", s._conf.Port))
	if err != nil {
		panic(err)
	}
}

func (s *Server) Start() {
	s.initGorm()
	s.initSmtp()
	s.initGin()
	s.run()
}

func buildMySQLURL(conf *config.DatabaseConfig) string {
	return fmt.Sprintf("%s:%s@(%s:%d)/%s?charset=utf8mb4&parseTime=True&loc=Local", conf.User, conf.Pass, conf.Host, conf.Port, conf.Name)
}

func getMode() string {
	if os.Getenv("GYM_SERVER_MODE") != DebugMode {
		return ReleaseMode
	}
	return DebugMode
}

func NewServer(conf *config.Config) *Server {
	return &Server{
		_conf:   conf,
		signKey: random.String(16, "ayfudrtetuyihf6rt8uib!@#$%^&*()($Q@#$%^&*^%$#@!#$%^"),
	}
}
