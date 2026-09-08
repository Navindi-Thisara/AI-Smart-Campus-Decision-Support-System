package com.smartcampus.backend.controller;

import com.smartcampus.backend.entity.DegreeModule;
import com.smartcampus.backend.repository.DegreeModuleRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/degree-modules")
@CrossOrigin(origins = "http://localhost:5173")
public class DegreeModuleController {

    private final DegreeModuleRepository degreeModuleRepository;

    public DegreeModuleController(
            DegreeModuleRepository degreeModuleRepository
    ) {
        this.degreeModuleRepository = degreeModuleRepository;
    }

    @GetMapping
    public List<DegreeModule> getAllDegreeModules() {
        return degreeModuleRepository.findAll();
    }

    @GetMapping("/degree/{degreeId}")
    public List<DegreeModule> getByDegree(
            @PathVariable String degreeId
    ) {
        return degreeModuleRepository.findByDegreeId(degreeId);
    }

    @PostMapping("/degree/{degreeId}/courses")
    public List<DegreeModule> getByDegreeAndCourses(
            @PathVariable String degreeId,
            @RequestBody List<String> courseCodes
    ) {
        return degreeModuleRepository
                .findByDegreeIdAndCourseCodeIn(
                        degreeId,
                        courseCodes
                );
    }
}
