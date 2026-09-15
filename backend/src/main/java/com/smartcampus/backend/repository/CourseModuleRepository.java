package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.CourseModule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface CourseModuleRepository
        extends JpaRepository<CourseModule, String> {

    
    @Query("""
    SELECT cm
    FROM CourseModule cm
    WHERE cm.semester = :semester
    AND cm.courseCode IN (
        SELECT dm.courseCode
        FROM DegreeModule dm
        WHERE dm.degreeId = :degreeId
        AND LOWER(dm.moduleType) = 'core'
    )
    ORDER BY cm.courseCode
    """)
List<CourseModule> findModulesByDegreeAndSemester(
        @Param("degreeId") String degreeId,
        @Param("semester") Integer semester
);

    List<CourseModule> findBySemesterOrderByCourseCode(Integer semester);
}