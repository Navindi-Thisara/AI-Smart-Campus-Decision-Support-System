package com.smartcampus.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(
    name = "student_academic_profiles",
    uniqueConstraints = {
        @UniqueConstraint(
            name = "uk_student_profile_user",
            columnNames = "user_id"
        )
    }
)
public class StudentAcademicProfile {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(
        name = "user_id",
        nullable = false,
        unique = true,
        foreignKey = @ForeignKey(
            name = "fk_student_profile_user"
        )
    )
    private User user;

    @Column(nullable = false)
    private Integer intake;

    @Column(name = "faculty_id", nullable = false, length = 20)
    private String facultyId;

    @Column(name = "degree_id", nullable = false, length = 20)
    private String degreeId;

    @Column(name = "current_year", nullable = false)
    private Integer currentYear;

    @Column(name = "current_semester", nullable = false)
    private Integer currentSemester;

    public StudentAcademicProfile() {
    }

    public Long getId() {
        return id;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public Integer getIntake() {
        return intake;
    }

    public void setIntake(Integer intake) {
        this.intake = intake;
    }

    public String getFacultyId() {
        return facultyId;
    }

    public void setFacultyId(String facultyId) {
        this.facultyId = facultyId;
    }

    public String getDegreeId() {
        return degreeId;
    }

    public void setDegreeId(String degreeId) {
        this.degreeId = degreeId;
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
}
