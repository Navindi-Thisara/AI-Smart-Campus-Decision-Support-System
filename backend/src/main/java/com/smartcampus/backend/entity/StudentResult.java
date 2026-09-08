package com.smartcampus.backend.entity;

import jakarta.persistence.*;

import java.math.BigDecimal;

@Entity
@Table(
        name = "student_results",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_student_result_course_semester",
                        columnNames = {
                                "user_id",
                                "course_code",
                                "semester"
                        }
                )
        }
)
public class StudentResult {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(
            name = "user_id",
            nullable = false
    )
    private User user;

    @Column(
            name = "course_code",
            nullable = false,
            length = 30
    )
    private String courseCode;

    @Column(
            nullable = false
    )
    private Integer semester;

    @Column(
            nullable = false,
            length = 10
    )
    private String grade;

    @Column(
            name = "grade_point",
            precision = 4,
            scale = 2,
            nullable = true
    )
    private BigDecimal gradePoint;


    public StudentResult() {
    }


    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }


    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }


    public String getCourseCode() {
        return courseCode;
    }

    public void setCourseCode(String courseCode) {
        this.courseCode =
                courseCode == null
                        ? null
                        : courseCode.trim();
    }


    public Integer getSemester() {
        return semester;
    }

    public void setSemester(Integer semester) {
        this.semester = semester;
    }


    public String getGrade() {
        return grade;
    }

    public void setGrade(String grade) {
        this.grade =
                grade == null
                        ? null
                        : grade.trim();
    }


    public BigDecimal getGradePoint() {
        return gradePoint;
    }

    public void setGradePoint(BigDecimal gradePoint) {
        this.gradePoint = gradePoint;
    }
}