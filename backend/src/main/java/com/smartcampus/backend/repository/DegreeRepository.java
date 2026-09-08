package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.Degree;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DegreeRepository
        extends JpaRepository<Degree, String> {

    List<Degree> findByFacultyId(String facultyId);
}