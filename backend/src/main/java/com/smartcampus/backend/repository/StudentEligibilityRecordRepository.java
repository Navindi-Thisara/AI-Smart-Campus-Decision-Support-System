package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.StudentEligibilityRecord;
import com.smartcampus.backend.entity.User;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface StudentEligibilityRecordRepository
        extends JpaRepository<StudentEligibilityRecord, Long> {

    Optional<StudentEligibilityRecord> findByUserAndSemester(
            User user,
            Integer semester
    );

    Optional<StudentEligibilityRecord> findByUser_IdAndSemester(
            Long userId,
            Integer semester
    );

    @EntityGraph(attributePaths = {"user"})
    List<StudentEligibilityRecord> findAllByOrderBySemesterAsc();
}
