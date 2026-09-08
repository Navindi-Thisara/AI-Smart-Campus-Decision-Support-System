package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.Faculty;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FacultyRepository
        extends JpaRepository<Faculty, String> {
}