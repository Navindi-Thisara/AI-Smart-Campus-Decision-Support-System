package com.smartcampus.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "degrees")
public class Degree {

    @Id
    @Column(name = "degree_id", length = 20)
    private String degreeId;

    @Column(
        name = "degree_name",
        nullable = false,
        length = 200
    )
    private String degreeName;

    @Column(
        name = "faculty_id",
        nullable = false,
        length = 20
    )
    private String facultyId;

    @Column(
        name = "department",
        length = 150
    )
    private String department;

    @Column(name = "duration_years")
    private Integer durationYears;

    public Degree() {
    }

    public Degree(
        String degreeId,
        String degreeName,
        String facultyId,
        String department,
        Integer durationYears
    ) {
        this.degreeId = degreeId;
        this.degreeName = degreeName;
        this.facultyId = facultyId;
        this.department = department;
        this.durationYears = durationYears;
    }

    public String getDegreeId() {
        return degreeId;
    }

    public void setDegreeId(String degreeId) {
        this.degreeId = degreeId;
    }

    public String getDegreeName() {
        return degreeName;
    }

    public void setDegreeName(String degreeName) {
        this.degreeName = degreeName;
    }

    public String getFacultyId() {
        return facultyId;
    }

    public void setFacultyId(String facultyId) {
        this.facultyId = facultyId;
    }

    public String getDepartment() {
        return department;
    }

    public void setDepartment(String department) {
        this.department = department;
    }

    public Integer getDurationYears() {
        return durationYears;
    }

    public void setDurationYears(Integer durationYears) {
        this.durationYears = durationYears;
    }
}