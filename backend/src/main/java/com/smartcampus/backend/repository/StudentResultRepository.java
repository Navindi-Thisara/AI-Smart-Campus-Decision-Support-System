package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.StudentResult;
import com.smartcampus.backend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface StudentResultRepository
        extends JpaRepository<StudentResult, Long> {

    List<StudentResult> findByUserOrderBySemesterAscCourseCodeAsc(
            User user
    );

    List<StudentResult> findByUserAndSemesterOrderByCourseCodeAsc(
            User user,
            Integer semester
    );

    Optional<StudentResult> findByUserAndCourseCodeAndSemester(
            User user,
            String courseCode,
            Integer semester
    );

    void deleteByUserAndSemesterGreaterThan(
            User user,
            Integer semester
    );
}