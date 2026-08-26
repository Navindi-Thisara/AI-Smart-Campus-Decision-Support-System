package com.smartcampus.backend.repository;

import com.smartcampus.backend.dto.UserRole;
import com.smartcampus.backend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {

    boolean existsByEmail(String email);

    boolean existsByStudentId(String studentId);

    boolean existsByStudentIdAndRole(
            String studentId,
            UserRole role
    );

}