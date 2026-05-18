package com.java.orm.controllers;

import org.springframework.web.bind.annotation.*;

import com.java.orm.models.User;
import com.java.orm.models.UserResponse;
import com.java.orm.services.UserService;

@RestController
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/user/{id}")
    public UserResponse getUserById(@PathVariable Long id) {
        return new UserResponse(userService.getUserById(id));
    }
}
