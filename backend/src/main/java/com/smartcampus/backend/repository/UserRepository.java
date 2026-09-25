package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {

    boolean existsByEmail(String email);

    boolean existsByStudentId(String studentId);

    Optional<User> findByEmail(String email);

    Optional<User> findByStudentId(String studentId);

    @Query("SELECT COUNT(u) FROM User u WHERE u.role = 'STUDENT'")
    long countStudentUsers();
}