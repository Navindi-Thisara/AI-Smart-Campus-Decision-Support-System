package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.StudentEligibilityRecord;
import com.smartcampus.backend.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface StudentEligibilityRecordRepository
        extends JpaRepository<StudentEligibilityRecord, Long> {

    Optional<StudentEligibilityRecord> findByUserAndSemester(
            User user,
            Integer semester
    );
}