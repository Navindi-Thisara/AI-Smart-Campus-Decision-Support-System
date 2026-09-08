package com.smartcampus.backend.controller;

import com.smartcampus.backend.entity.Degree;
import com.smartcampus.backend.repository.DegreeRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/degrees")
@CrossOrigin(origins = "http://localhost:5173")
public class DegreeController {

    private final DegreeRepository degreeRepository;

    public DegreeController(DegreeRepository degreeRepository) {
        this.degreeRepository = degreeRepository;
    }

    @GetMapping
    public List<Degree> getAllDegrees() {
        return degreeRepository.findAll();
    }

    @GetMapping("/faculty/{facultyId}")
    public List<Degree> getDegreesByFaculty(
            @PathVariable String facultyId
    ) {
        return degreeRepository.findByFacultyId(facultyId);
    }
}
