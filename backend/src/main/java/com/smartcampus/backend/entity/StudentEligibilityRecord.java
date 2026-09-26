package com.smartcampus.backend.entity;

import jakarta.persistence.*;
import java.math.BigDecimal;

@Entity
@Table(
    name = "student_eligibility_records",
    uniqueConstraints = {
        @UniqueConstraint(columnNames = {"user_id", "semester"})
    }
)
public class StudentEligibilityRecord {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @Column(nullable = false)
    private Integer semester;

    @Column(name = "attendance_percentage", nullable = false, precision = 5, scale = 2)
    private BigDecimal attendancePercentage;

    @Column(name = "fee_paid", nullable = false)
    private Boolean feePaid = false;

    public StudentEligibilityRecord() {
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

    public Integer getSemester() {
        return semester;
    }

    public void setSemester(Integer semester) {
        this.semester = semester;
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
}
