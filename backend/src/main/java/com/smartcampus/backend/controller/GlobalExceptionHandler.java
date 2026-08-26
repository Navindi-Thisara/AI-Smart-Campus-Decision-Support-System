package com.smartcampus.backend.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.LinkedHashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {


    // =========================================================
    // VALIDATION ERRORS
    // =========================================================

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidation(
            MethodArgumentNotValidException exception
    ) {

        Map<String, String> errors =
                new LinkedHashMap<>();

        exception.getBindingResult()
                .getFieldErrors()
                .forEach(error ->
                        errors.put(
                                error.getField(),
                                error.getDefaultMessage()
                        )
                );


        Map<String, Object> response =
                new LinkedHashMap<>();

        response.put(
                "message",
                "Please correct the highlighted fields."
        );

        response.put(
                "errors",
                errors
        );


        return ResponseEntity
                .badRequest()
                .body(response);
    }
}