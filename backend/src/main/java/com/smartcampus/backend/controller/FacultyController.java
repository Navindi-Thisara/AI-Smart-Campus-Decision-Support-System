package com.smartcampus.backend.controller;

import com.smartcampus.backend.entity.Faculty;
import com.smartcampus.backend.repository.FacultyRepository;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/faculties")
@CrossOrigin(origins = "http://localhost:5173")
public class FacultyController {

    private final FacultyRepository facultyRepository;

    public FacultyController(FacultyRepository facultyRepository) {
        this.facultyRepository = facultyRepository;
    }

    @GetMapping
    public List<Faculty> getAllFaculties() {
        return facultyRepository.findAll();
    }
}
