package com.smartcampus.backend.controller;

import com.smartcampus.backend.entity.CourseModule;
import com.smartcampus.backend.entity.DegreeModule;
import com.smartcampus.backend.entity.Faculty;
import com.smartcampus.backend.entity.Degree;

import com.smartcampus.backend.repository.CourseModuleRepository;
import com.smartcampus.backend.repository.DegreeModuleRepository;
import com.smartcampus.backend.repository.DegreeRepository;
import com.smartcampus.backend.repository.FacultyRepository;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/reference")
@CrossOrigin(origins = "http://localhost:5173")
public class ReferenceController {

    private final FacultyRepository facultyRepository;
    private final DegreeRepository degreeRepository;
    private final DegreeModuleRepository degreeModuleRepository;
    private final CourseModuleRepository courseModuleRepository;

    public ReferenceController(
            FacultyRepository facultyRepository,
            DegreeRepository degreeRepository,
            DegreeModuleRepository degreeModuleRepository,
            CourseModuleRepository courseModuleRepository
    ) {
        this.facultyRepository = facultyRepository;
        this.degreeRepository = degreeRepository;
        this.degreeModuleRepository = degreeModuleRepository;
        this.courseModuleRepository = courseModuleRepository;
    }


    // =========================================================
    // FACULTIES
    // =========================================================

    @GetMapping("/faculties")
    public ResponseEntity<List<Faculty>> getFaculties() {

        return ResponseEntity.ok(
                facultyRepository.findAll()
        );
    }


    // =========================================================
    // DEGREES
    // =========================================================

    @GetMapping("/degrees")
    public ResponseEntity<List<Degree>> getDegrees() {

        return ResponseEntity.ok(
                degreeRepository.findAll()
        );
    }


    // =========================================================
    // MODULES BY DEGREE + SEMESTER
    // =========================================================

    @GetMapping(
            "/degrees/{degreeId}/semesters/{semester}/modules"
    )
    public ResponseEntity<List<Map<String, Object>>> getModules(
            @PathVariable String degreeId,
            @PathVariable Integer semester
    ) {

        System.out.println(
                "=============================================="
        );

        System.out.println(
                "GET MODULES"
        );

        System.out.println(
                "Degree ID : " + degreeId
        );

        System.out.println(
                "Semester  : " + semester
        );


        // -----------------------------------------------------
        // Validate semester
        // -----------------------------------------------------

        if (semester < 1 || semester > 8) {

            System.out.println(
                    "Invalid semester: " + semester
            );

            return ResponseEntity.badRequest().body(
                    Collections.emptyList()
            );
        }


        // -----------------------------------------------------
        // Check degree mappings
        // -----------------------------------------------------

        List<DegreeModule> mappings =
                degreeModuleRepository.findByDegreeId(degreeId);

        System.out.println(
                "Degree mappings found: "
                        + mappings.size()
        );


        if (mappings.isEmpty()) {

            System.out.println(
                    "WARNING: No degree mappings found for "
                            + degreeId
            );

            return ResponseEntity.ok(
                    Collections.emptyList()
            );
        }


        // -----------------------------------------------------
        // Get modules directly using degree + semester
        // -----------------------------------------------------

        List<CourseModule> modules =
                courseModuleRepository
                        .findModulesByDegreeAndSemester(
                                degreeId,
                                semester
                        );


        System.out.println(
                "Course modules found: "
                        + modules.size()
        );


        // -----------------------------------------------------
        // Get module type from degree_modules
        // -----------------------------------------------------

        Map<String, String> moduleTypes =
                new HashMap<>();

        for (DegreeModule mapping : mappings) {

            moduleTypes.put(
                    mapping.getCourseCode().trim(),
                    mapping.getModuleType()
            );
        }


        // -----------------------------------------------------
        // Convert result
        // -----------------------------------------------------

        List<Map<String, Object>> result =
                new ArrayList<>();


        for (CourseModule module : modules) {

            String courseCode =
                    module.getCourseCode().trim();


            Map<String, Object> item =
                    new LinkedHashMap<>();


            item.put(
                    "courseCode",
                    courseCode
            );

            item.put(
                    "moduleName",
                    module.getModuleName()
            );

            item.put(
                    "year",
                    module.getYear()
            );

            item.put(
                    "semester",
                    module.getSemester()
            );

            item.put(
                    "credits",
                    module.getCredits()
            );

            item.put(
                    "moduleCategory",
                    module.getModuleCategory()
            );

            item.put(
                    "moduleType",
                    moduleTypes.getOrDefault(
                            courseCode,
                            "Core"
                    )
            );


            result.add(item);


            System.out.println(
                    "  -> "
                            + courseCode
                            + " | "
                            + module.getModuleName()
                            + " | "
                            + module.getCredits()
                            + " credits"
            );
        }


        System.out.println(
                "Returning "
                        + result.size()
                        + " modules"
        );

        System.out.println(
                "=============================================="
        );


        return ResponseEntity.ok(result);
    }


    // =========================================================
    // DEBUG ENDPOINT
    // =========================================================
    //
    // This allows you to check exactly what the backend sees
    // for a degree.
    //
    // Example:
    // /api/reference/degrees/D001/debug
    //
    // =========================================================

    @GetMapping("/degrees/{degreeId}/debug")
    public ResponseEntity<Map<String, Object>> debugDegree(
            @PathVariable String degreeId
    ) {

        List<DegreeModule> mappings =
                degreeModuleRepository
                        .findByDegreeId(degreeId);


        Map<Integer, Long> semesterCounts =
                new LinkedHashMap<>();


        for (int semester = 1; semester <= 8; semester++) {

            final int currentSemester = semester;

            long count =
                    mappings.stream()
                            .filter(mapping -> {

                                String courseCode =
                                        mapping.getCourseCode()
                                                .trim();

                                return courseModuleRepository
                                        .findById(courseCode)
                                        .map(course ->
                                                course.getSemester()
                                                        .equals(
                                                                currentSemester
                                                        )
                                        )
                                        .orElse(false);
                            })
                            .count();

            semesterCounts.put(
                    semester,
                    count
            );
        }


        Map<String, Object> response =
                new LinkedHashMap<>();

        response.put(
                "degreeId",
                degreeId
        );

        response.put(
                "totalDegreeMappings",
                mappings.size()
        );

        response.put(
                "semesterCounts",
                semesterCounts
        );


        return ResponseEntity.ok(response);
    }
}