package com.smartcampus.backend.entity;

import com.smartcampus.backend.dto.UserRole;
import jakarta.persistence.*;

@Entity
@Table(
    name = "users",
    uniqueConstraints = {
        @UniqueConstraint(
            name = "uk_users_email",
            columnNames = "email"
        ),
        @UniqueConstraint(
            name = "uk_users_student_id",
            columnNames = "student_id"
        )
    }
)
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(
        name = "full_name",
        nullable = false,
        length = 150
    )
    private String fullName;

    @Column(
        nullable = false,
        unique = true,
        length = 150
    )
    private String email;

    @Column(
        name = "student_id",
        nullable = false,
        unique = true,
        length = 30
    )
    private String studentId;

    @Column(
        nullable = false,
        length = 255
    )
    private String password;

    @Enumerated(EnumType.STRING)
    @Column(
        nullable = false,
        length = 20
    )
    private UserRole role;

    public User() {
    }

    public User(
            String fullName,
            String email,
            String studentId,
            String password,
            UserRole role
    ) {
        this.fullName = fullName;
        this.email = email;
        this.studentId = studentId;
        this.password = password;
        this.role = role;
    }

    public Long getId() {
        return id;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getStudentId() {
        return studentId;
    }

    public void setStudentId(String studentId) {
        this.studentId = studentId;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public UserRole getRole() {
        return role;
    }

    public void setRole(UserRole role) {
        this.role = role;
    }
}