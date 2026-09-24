package com.smartcampus.backend.controller;

import com.smartcampus.backend.dto.StaffDashboardResponse;
import com.smartcampus.backend.service.StaffDashboardService;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/staff")
@CrossOrigin(origins = "http://localhost:5173")
public class StaffDashboardController {

    private final StaffDashboardService staffDashboardService;

    public StaffDashboardController(
            StaffDashboardService staffDashboardService
    ) {
        this.staffDashboardService =
                staffDashboardService;
    }

    @GetMapping("/dashboard")
    public StaffDashboardResponse getDashboard() {

        return staffDashboardService.getDashboard();
    }
}