package com.smartcampus.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(
        name = "degree_modules",
        uniqueConstraints = {
                @UniqueConstraint(
                        name = "uk_degree_course",
                        columnNames = {
                                "degree_id",
                                "course_code"
                        }
                )
        }
)
public class DegreeModule {

    @Id
    @Column(
            name = "degree_module_id",
            length = 30,
            nullable = false
    )
    private String degreeModuleId;


    @Column(
            name = "degree_id",
            nullable = false,
            length = 20
    )
    private String degreeId;


    @Column(
            name = "course_code",
            nullable = false,
            length = 30
    )
    private String courseCode;


    @Column(
            name = "module_type",
            nullable = false,
            length = 20
    )
    private String moduleType;


    public DegreeModule() {
    }


    public DegreeModule(
            String degreeModuleId,
            String degreeId,
            String courseCode,
            String moduleType
    ) {
        this.degreeModuleId = degreeModuleId;
        this.degreeId = degreeId;
        this.courseCode = courseCode;
        this.moduleType = moduleType;
    }


    public String getDegreeModuleId() {
        return degreeModuleId;
    }


    public void setDegreeModuleId(String degreeModuleId) {
        this.degreeModuleId = degreeModuleId;
    }


    public String getDegreeId() {
        return degreeId;
    }


    public void setDegreeId(String degreeId) {
        this.degreeId =
                degreeId == null
                        ? null
                        : degreeId.trim();
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


    public String getModuleType() {
        return moduleType;
    }


    public void setModuleType(String moduleType) {
        this.moduleType = moduleType;
    }
}