package com.smartcampus.backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "course_modules")
public class CourseModule {

    @Id
    @Column(
            name = "course_code",
            length = 30,
            nullable = false
    )
    private String courseCode;


    @Column(
            name = "module_name",
            nullable = false,
            length = 200
    )
    private String moduleName;


    @Column(nullable = false)
    private Integer year;


    @Column(nullable = false)
    private Integer semester;


    @Column(nullable = false)
    private Integer credits;


    @Column(
            name = "module_category",
            nullable = false,
            length = 20
    )
    private String moduleCategory;


    public CourseModule() {
    }


    public CourseModule(
            String courseCode,
            String moduleName,
            Integer year,
            Integer semester,
            Integer credits,
            String moduleCategory
    ) {
        this.courseCode = courseCode;
        this.moduleName = moduleName;
        this.year = year;
        this.semester = semester;
        this.credits = credits;
        this.moduleCategory = moduleCategory;
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


    public String getModuleName() {
        return moduleName;
    }


    public void setModuleName(String moduleName) {
        this.moduleName = moduleName;
    }


    public Integer getYear() {
        return year;
    }


    public void setYear(Integer year) {
        this.year = year;
    }


    public Integer getSemester() {
        return semester;
    }


    public void setSemester(Integer semester) {
        this.semester = semester;
    }


    public Integer getCredits() {
        return credits;
    }


    public void setCredits(Integer credits) {
        this.credits = credits;
    }


    public String getModuleCategory() {
        return moduleCategory;
    }


    public void setModuleCategory(String moduleCategory) {
        this.moduleCategory = moduleCategory;
    }
}