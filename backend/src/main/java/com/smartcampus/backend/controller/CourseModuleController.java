package com.smartcampus.backend.controller;

import com.smartcampus.backend.entity.CourseModule;
import com.smartcampus.backend.repository.CourseModuleRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/course-modules")
@CrossOrigin(origins = "http://localhost:5173")
public class CourseModuleController {

    private final CourseModuleRepository courseModuleRepository;

    public CourseModuleController(
            CourseModuleRepository courseModuleRepository
    ) {
        this.courseModuleRepository = courseModuleRepository;
    }

    @GetMapping
    public List<CourseModule> getAllCourseModules() {
        return courseModuleRepository.findAll();
    }

    @GetMapping("/semester/{semester}")
    public List<CourseModule> getBySemester(
            @PathVariable Integer semester
    ) {
        return courseModuleRepository
                .findBySemesterOrderByCourseCode(semester);
    }
}
