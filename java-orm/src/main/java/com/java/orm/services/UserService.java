package com.java.orm.services;

import java.util.List;

import org.springframework.stereotype.Service;

import com.java.orm.models.User;
import com.java.orm.models.UserRepository;

@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public User getUserById(Long id) {
        return userRepository.findById(id).orElseThrow(() -> new RuntimeException("User not found"));
    }
}
