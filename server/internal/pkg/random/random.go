package random

import (
	"math/rand"
	"time"
)

func String(length int, dict string) string {
	rand.Seed(time.Now().UnixNano())
	dictLength := len(dict)
	result := ""
	for i := 0; i < length; i++ {
		pos := rand.Intn(dictLength)
		result += string(dict[pos])
	}
	return result
}

//func MD5(str string) string {
//	m := md5.New()
//	m.Write([]byte(str))
//	return hex.EncodeToString(m.Sum(nil))
//}
