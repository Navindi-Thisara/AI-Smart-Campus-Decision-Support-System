package com.smartcampus.backend.dto;

import com.smartcampus.backend.entity.User;

public class LoginResponse {

    private String message;
    private UserResponse user;

    public LoginResponse() {
    }

    public LoginResponse(String message, UserResponse user) {
        this.message = message;
        this.user = user;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public UserResponse getUser() {
        return user;
    }

    public void setUser(UserResponse user) {
        this.user = user;
    }

    public static class UserResponse {

        private Long id;
        private String fullName;
        private String email;
        private String studentId;
        private UserRole role;

        public UserResponse() {
        }

        public UserResponse(User user) {
            this.id = user.getId();
            this.fullName = user.getFullName();
            this.email = user.getEmail();
            this.studentId = user.getStudentId();
            this.role = user.getRole();
        }

        public Long getId() {
            return id;
        }

        public String getFullName() {
            return fullName;
        }

        public String getEmail() {
            return email;
        }

        public String getStudentId() {
            return studentId;
        }

        public UserRole getRole() {
            return role;
        }
    }
}