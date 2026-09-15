package com.smartcampus.backend.dto;

import java.util.List;

public class EligibilityResponse {

    private String studentId;
    private Integer semester;
    private String status;
    private boolean eligible;
    private List<String> explanations;

    public EligibilityResponse() {
    }

    public EligibilityResponse(
            String studentId,
            Integer semester,
            String status,
            boolean eligible,
            List<String> explanations
    ) {
        this.studentId = studentId;
        this.semester = semester;
        this.status = status;
        this.eligible = eligible;
        this.explanations = explanations;
    }

    public String getStudentId() {
        return studentId;
    }

    public Integer getSemester() {
        return semester;
    }

    public String getStatus() {
        return status;
    }

    public boolean isEligible() {
        return eligible;
    }

    public List<String> getExplanations() {
        return explanations;
    }
}