package com.smartcampus.backend.dto;

import java.math.BigDecimal;

public class UpdateEligibilityRequest {

    private String studentId;
    private Integer semester;
    private BigDecimal attendancePercentage;
    private Boolean feePaid;

    public UpdateEligibilityRequest() {
    }

    public String getStudentId() {
        return studentId;
    }

    public void setStudentId(String studentId) {
        this.studentId = studentId;
    }

    public Integer getSemester() {
        return semester;
    }

    public void setSemester(Integer semester) {
        this.semester = semester;
    }

    public BigDecimal getAttendancePercentage() {
        return attendancePercentage;
    }

    public void setAttendancePercentage(
            BigDecimal attendancePercentage
    ) {
        this.attendancePercentage =
                attendancePercentage;
    }

    public Boolean getFeePaid() {
        return feePaid;
    }

    public void setFeePaid(Boolean feePaid) {
        this.feePaid = feePaid;
    }
}