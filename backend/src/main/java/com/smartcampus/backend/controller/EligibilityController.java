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
            @RequestParam String studentId
    ) {

        /*
         * EligibilityService is the single source of truth.
         *
         * The student's current semester is obtained from
         * the database using the academic profile.
         *
         * Do not accept semester from the frontend because
         * that could cause the Staff Dashboard and Student
         * Eligibility page to evaluate different semesters.
         */
        return eligibilityService.evaluateEligibility(
                studentId
        );
    }
}