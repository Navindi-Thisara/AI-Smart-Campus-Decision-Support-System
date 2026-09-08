package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.StudentSemesterGpa;
import com.smartcampus.backend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface StudentSemesterGpaRepository
        extends JpaRepository<StudentSemesterGpa, Long> {

    List<StudentSemesterGpa> findByUserOrderBySemesterAsc(
        User user
    );

    Optional<StudentSemesterGpa> findByUserAndSemester(
        User user,
        Integer semester
    );

    // Delete SGPA records for semesters after the student's current semester
    void deleteByUserAndSemesterGreaterThan(
        User user,
        Integer semester
    );
}