package com.smartcampus.backend.controller;

import com.smartcampus.backend.dto.RegisterRequest;
import com.smartcampus.backend.service.AuthService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;


    // =========================================================
    // CONSTRUCTOR
    // =========================================================

    public AuthController(AuthService authService) {
        this.authService = authService;
    }


    // =========================================================
    // REGISTER
    // =========================================================

    @PostMapping("/register")
    public ResponseEntity<?> register(
            @Valid @RequestBody RegisterRequest request
    ) {

        try {

            authService.register(request);

            return ResponseEntity
                    .status(HttpStatus.CREATED)
                    .body(
                        Map.of(
                            "message",
                            "Your account has been created successfully."
                        )
                    );

        } catch (IllegalArgumentException exception) {

            return ResponseEntity
                    .badRequest()
                    .body(
                        Map.of(
                            "message",
                            exception.getMessage()
                        )
                    );
        }
    }
}