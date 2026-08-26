package com.smartcampus.backend.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;

public class RegisterRequest {

    // =========================================================
    // FULL NAME
    // =========================================================

    @NotBlank(message = "Full name is required.")
    @Size(
        min = 5,
        message = "Full name must contain at least 5 characters."
    )
    private String fullName;


    // =========================================================
    // UNIVERSITY EMAIL
    // =========================================================

    @NotBlank(message = "University email is required.")
    @Email(message = "Please enter a valid email address.")
    @Pattern(
        regexp = "^[A-Za-z0-9._%+-]+@kdu\\.ac\\.lk$",
        message = "University email must end with @kdu.ac.lk."
    )
    private String email;


    // =========================================================
    // STUDENT ID / STAFF ID
    // =========================================================

    @NotBlank(message = "Student ID / Staff ID is required.")
    private String studentId;


    // =========================================================
    // PASSWORD
    // =========================================================

    @NotBlank(message = "Password is required.")
    @Size(
        min = 8,
        message = "Password must contain at least 8 characters."
    )
    @Pattern(
        regexp = "^(?=.*[A-Z])(?=.*[a-z])(?=.*\\d).+$",
        message = "Password must contain an uppercase letter, lowercase letter, and number."
    )
    private String password;


    // =========================================================
    // CONFIRM PASSWORD
    // =========================================================

    @NotBlank(message = "Confirm password is required.")
    private String confirmPassword;


    // =========================================================
    // ROLE
    // =========================================================

    @NotNull(message = "Account role is required.")
    private UserRole role;


    // =========================================================
    // GETTERS
    // =========================================================

    public String getFullName() {
        return fullName;
    }

    public String getEmail() {
        return email;
    }

    public String getStudentId() {
        return studentId;
    }

    public String getPassword() {
        return password;
    }

    public String getConfirmPassword() {
        return confirmPassword;
    }

    public UserRole getRole() {
        return role;
    }


    // =========================================================
    // SETTERS
    // =========================================================

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public void setStudentId(String studentId) {
        this.studentId = studentId;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public void setConfirmPassword(String confirmPassword) {
        this.confirmPassword = confirmPassword;
    }

    public void setRole(UserRole role) {
        this.role = role;
    }
}