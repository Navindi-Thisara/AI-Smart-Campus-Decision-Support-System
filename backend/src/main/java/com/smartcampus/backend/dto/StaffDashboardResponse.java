package com.smartcampus.backend.dto;

import java.math.BigDecimal;
import java.util.List;

public class StaffDashboardResponse {

    private long totalStudents;
    private long eligibleStudents;
    private long conditionallyEligibleStudents;
    private long notEligibleStudents;

    private BigDecimal overallAverageSgpa;

    private List<SemesterPerformance> semesterPerformance;
    private List<StudentAttention> studentsRequiringAttention;

    public StaffDashboardResponse() {
    }

    public StaffDashboardResponse(
            long totalStudents,
            long eligibleStudents,
            long conditionallyEligibleStudents,
            long notEligibleStudents,
            BigDecimal overallAverageSgpa,
            List<SemesterPerformance> semesterPerformance,
            List<StudentAttention> studentsRequiringAttention
    ) {
        this.totalStudents = totalStudents;
        this.eligibleStudents = eligibleStudents;
        this.conditionallyEligibleStudents = conditionallyEligibleStudents;
        this.notEligibleStudents = notEligibleStudents;
        this.overallAverageSgpa = overallAverageSgpa;
        this.semesterPerformance = semesterPerformance;
        this.studentsRequiringAttention = studentsRequiringAttention;
    }

    public long getTotalStudents() {
        return totalStudents;
    }

    public void setTotalStudents(long totalStudents) {
        this.totalStudents = totalStudents;
    }

    public long getEligibleStudents() {
        return eligibleStudents;
    }

    public void setEligibleStudents(long eligibleStudents) {
        this.eligibleStudents = eligibleStudents;
    }

    public long getConditionallyEligibleStudents() {
        return conditionallyEligibleStudents;
    }

    public void setConditionallyEligibleStudents(long conditionallyEligibleStudents) {
        this.conditionallyEligibleStudents = conditionallyEligibleStudents;
    }

    public long getNotEligibleStudents() {
        return notEligibleStudents;
    }

    public void setNotEligibleStudents(long notEligibleStudents) {
        this.notEligibleStudents = notEligibleStudents;
    }

    public BigDecimal getOverallAverageSgpa() {
        return overallAverageSgpa;
    }

    public void setOverallAverageSgpa(BigDecimal overallAverageSgpa) {
        this.overallAverageSgpa = overallAverageSgpa;
    }

    public List<SemesterPerformance> getSemesterPerformance() {
        return semesterPerformance;
    }

    public void setSemesterPerformance(List<SemesterPerformance> semesterPerformance) {
        this.semesterPerformance = semesterPerformance;
    }

    public List<StudentAttention> getStudentsRequiringAttention() {
        return studentsRequiringAttention;
    }

    public void setStudentsRequiringAttention(
            List<StudentAttention> studentsRequiringAttention
    ) {
        this.studentsRequiringAttention = studentsRequiringAttention;
    }

    public static class SemesterPerformance {

        private Integer semester;
        private BigDecimal averageSgpa;

        public SemesterPerformance() {
        }

        public SemesterPerformance(
                Integer semester,
                BigDecimal averageSgpa
        ) {
            this.semester = semester;
            this.averageSgpa = averageSgpa;
        }

        public Integer getSemester() {
            return semester;
        }

        public void setSemester(Integer semester) {
            this.semester = semester;
        }

        public BigDecimal getAverageSgpa() {
            return averageSgpa;
        }

        public void setAverageSgpa(BigDecimal averageSgpa) {
            this.averageSgpa = averageSgpa;
        }
    }

    public static class StudentAttention {

        private String studentId;
        private String fullName;
        private String email;
        private String degreeId;
        private String facultyId;
        private Integer currentYear;
        private Integer currentSemester;

        private BigDecimal currentSgpa;
        private BigDecimal attendancePercentage;

        private Boolean feePaid;

        private String eligibilityStatus;
        private String attentionReason;

        public StudentAttention() {
        }

        public StudentAttention(
                String studentId,
                String fullName,
                String email,
                String degreeId,
                String facultyId,
                Integer currentYear,
                Integer currentSemester,
                BigDecimal currentSgpa,
                BigDecimal attendancePercentage,
                Boolean feePaid,
                String eligibilityStatus,
                String attentionReason
        ) {
            this.studentId = studentId;
            this.fullName = fullName;
            this.email = email;
            this.degreeId = degreeId;
            this.facultyId = facultyId;
            this.currentYear = currentYear;
            this.currentSemester = currentSemester;
            this.currentSgpa = currentSgpa;
            this.attendancePercentage = attendancePercentage;
            this.feePaid = feePaid;
            this.eligibilityStatus = eligibilityStatus;
            this.attentionReason = attentionReason;
        }

        public String getStudentId() {
            return studentId;
        }

        public void setStudentId(String studentId) {
            this.studentId = studentId;
        }

        public String getFullName() {
            return fullName;
        }

        public void setFullName(String fullName) {
            this.fullName = fullName;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }

        public String getDegreeId() {
            return degreeId;
        }

        public void setDegreeId(String degreeId) {
            this.degreeId = degreeId;
        }

        public String getFacultyId() {
            return facultyId;
        }

        public void setFacultyId(String facultyId) {
            this.facultyId = facultyId;
        }

        public Integer getCurrentYear() {
            return currentYear;
        }

        public void setCurrentYear(Integer currentYear) {
            this.currentYear = currentYear;
        }

        public Integer getCurrentSemester() {
            return currentSemester;
        }

        public void setCurrentSemester(Integer currentSemester) {
            this.currentSemester = currentSemester;
        }

        public BigDecimal getCurrentSgpa() {
            return currentSgpa;
        }

        public void setCurrentSgpa(BigDecimal currentSgpa) {
            this.currentSgpa = currentSgpa;
        }

        public BigDecimal getAttendancePercentage() {
            return attendancePercentage;
        }

        public void setAttendancePercentage(BigDecimal attendancePercentage) {
            this.attendancePercentage = attendancePercentage;
        }

        public Boolean getFeePaid() {
            return feePaid;
        }

        public void setFeePaid(Boolean feePaid) {
            this.feePaid = feePaid;
        }

        public String getEligibilityStatus() {
            return eligibilityStatus;
        }

        public void setEligibilityStatus(String eligibilityStatus) {
            this.eligibilityStatus = eligibilityStatus;
        }

        public String getAttentionReason() {
            return attentionReason;
        }

        public void setAttentionReason(String attentionReason) {
            this.attentionReason = attentionReason;
        }
    }
}
