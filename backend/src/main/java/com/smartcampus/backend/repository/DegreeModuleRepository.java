package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.DegreeModule;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DegreeModuleRepository
        extends JpaRepository<DegreeModule, String> {

    List<DegreeModule> findByDegreeId(String degreeId);

    List<DegreeModule> findByDegreeIdAndCourseCodeIn(
            String degreeId,
            List<String> courseCodes
    );
}