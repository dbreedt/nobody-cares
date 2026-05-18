package main

import (
	"encoding/json"
	"errors"
	"net/http"
	"strings"

	"gorm.io/gorm"
)

func getUser(w http.ResponseWriter, r *http.Request) {
	parts := strings.Split(r.URL.Path, "/")
	if len(parts) < 3 {
		http.Error(w, "Invalid URL", http.StatusBadRequest)
		return
	}
	id := parts[2]

	if len(id) == 0 {
		http.NotFound(w, r)
		return
	}

	var user User
	if err := db.First(&user, id).Error; err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			http.NotFound(w, r)
			return
		}
	}

	w.Header().Set("Content-Type", "application/json")
	err := json.NewEncoder(w).Encode(NewUserResponse(user))
	if err != nil {
		panic(err)
	}

}
