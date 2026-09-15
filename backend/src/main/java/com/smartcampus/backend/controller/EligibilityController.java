package com.smartcampus.backend.controller;

import com.smartcampus.backend.dto.EligibilityResponse;
import com.smartcampus.backend.service.EligibilityService;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/eligibility")
@CrossOrigin(origins = "http://localhost:5173")
public class EligibilityController {

    private final EligibilityService eligibilityService;

    public EligibilityController(
            EligibilityService eligibilityService
    ) {
        this.eligibilityService = eligibilityService;
    }

    @GetMapping
    public EligibilityResponse checkEligibility(

            @RequestParam String studentId,

            @RequestParam Integer semester
    ) {

        return eligibilityService.evaluateEligibility(
                studentId,
                semester
        );
    }
}