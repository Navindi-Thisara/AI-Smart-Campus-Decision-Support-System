package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.CourseModule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface CourseModuleRepository
        extends JpaRepository<CourseModule, String> {

    /**
     * Get all course modules belonging to a specific degree
     * and semester.
     *
     * The relationship is:
     *
     * degree_modules.degree_id
     *        ↓
     * degree_modules.course_code
     *        ↓
     * course_modules.course_code
     */
    @Query("""
        SELECT cm
        FROM CourseModule cm
        WHERE cm.semester = :semester
        AND cm.courseCode IN (
            SELECT dm.courseCode
            FROM DegreeModule dm
            WHERE dm.degreeId = :degreeId
        )
        ORDER BY cm.courseCode
        """)
    List<CourseModule> findModulesByDegreeAndSemester(
            @Param("degreeId") String degreeId,
            @Param("semester") Integer semester
    );

    /**
     * Get all course modules for a specific semester,
     * ordered by course code.
     */
    List<CourseModule> findBySemesterOrderByCourseCode(Integer semester);
}