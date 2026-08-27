package com.smartcampus.backend.service;

import com.smartcampus.backend.dto.LoginRequest;
import com.smartcampus.backend.dto.LoginResponse;
import com.smartcampus.backend.dto.RegisterRequest;
import com.smartcampus.backend.entity.User;
import com.smartcampus.backend.repository.UserRepository;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AuthService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    // REGISTER
    public void register(RegisterRequest request) {

        String email =
                request.getEmail()
                        .trim()
                        .toLowerCase();

        String studentId =
                request.getStudentId()
                        .trim()
                        .toUpperCase();


        // PASSWORD CONFIRMATION
        if (!request.getPassword()
                .equals(request.getConfirmPassword())) {

            throw new IllegalArgumentException(
                    "Passwords do not match."
            );
        }

        // EMAIL DUPLICATE CHECK
        if (userRepository.existsByEmail(email)) {

            throw new IllegalArgumentException(
                    "An account with this university email already exists."
            );
        }

        // ID DUPLICATE CHECK
        if (userRepository.existsByStudentId(studentId)) {

            String idType =
                    request.getRole().name().equals("STAFF")
                            ? "Staff ID"
                            : "Student ID";

            throw new IllegalArgumentException(
                    "An account with this "
                            + idType
                            + " already exists."
            );
        }

        // PASSWORD ENCODING
        String encodedPassword =
                passwordEncoder.encode(
                        request.getPassword()
                );


        // CREATE USER
        User user = new User(
                request.getFullName().trim(),
                email,
                studentId,
                encodedPassword,
                request.getRole()
        );


        // SAVE USER
        userRepository.save(user);
    }


    // LOGIN
    public LoginResponse login(LoginRequest request) {

        String email =
                request.getEmail()
                        .trim()
                        .toLowerCase();


        // FIND USER
        User user =
                userRepository
                        .findByEmail(email)
                        .orElseThrow(() ->
                                new IllegalArgumentException(
                                        "Invalid email or password."
                                )
                        );


        // CHECK PASSWORD
        boolean passwordMatches =
                passwordEncoder.matches(
                        request.getPassword(),
                        user.getPassword()
                );


        if (!passwordMatches) {

            throw new IllegalArgumentException(
                    "Invalid email or password."
            );
        }

        // RETURN USER INFORMATION
        LoginResponse.UserResponse userResponse =
                new LoginResponse.UserResponse(user);


        return new LoginResponse(
                "Login successful.",
                userResponse
        );
    }
}