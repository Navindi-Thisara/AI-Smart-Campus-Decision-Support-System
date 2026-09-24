package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.StudentSemesterGpa;
import com.smartcampus.backend.entity.User;
import org.springframework.data.jpa.repository.EntityGraph;
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

    void deleteByUserAndSemesterGreaterThan(
            User user,
            Integer semester
    );

    @EntityGraph(attributePaths = {"user"})
    List<StudentSemesterGpa> findAllByOrderBySemesterAsc();
}