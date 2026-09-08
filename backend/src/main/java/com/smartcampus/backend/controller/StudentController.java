package com.smartcampus.backend.controller;

import com.smartcampus.backend.entity.CourseModule;
import com.smartcampus.backend.entity.StudentAcademicProfile;
import com.smartcampus.backend.entity.StudentResult;
import com.smartcampus.backend.entity.StudentSemesterGpa;
import com.smartcampus.backend.entity.User;

import com.smartcampus.backend.repository.CourseModuleRepository;
import com.smartcampus.backend.repository.DegreeModuleRepository;
import com.smartcampus.backend.repository.StudentAcademicProfileRepository;
import com.smartcampus.backend.repository.StudentResultRepository;
import com.smartcampus.backend.repository.StudentSemesterGpaRepository;
import com.smartcampus.backend.repository.UserRepository;

import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;


@RestController
@RequestMapping("/api/students")
@CrossOrigin(origins = "http://localhost:5173")
public class StudentController {

    private final UserRepository userRepository;
    private final StudentAcademicProfileRepository profileRepository;
    private final StudentSemesterGpaRepository gpaRepository;
    private final StudentResultRepository resultRepository;
    private final CourseModuleRepository courseModuleRepository;
    private final DegreeModuleRepository degreeModuleRepository;


    public StudentController(
            UserRepository userRepository,
            StudentAcademicProfileRepository profileRepository,
            StudentSemesterGpaRepository gpaRepository,
            StudentResultRepository resultRepository,
            CourseModuleRepository courseModuleRepository,
            DegreeModuleRepository degreeModuleRepository
    ) {
        this.userRepository = userRepository;
        this.profileRepository = profileRepository;
        this.gpaRepository = gpaRepository;
        this.resultRepository = resultRepository;
        this.courseModuleRepository = courseModuleRepository;
        this.degreeModuleRepository = degreeModuleRepository;
    }


    // =========================================================
    // GET STUDENT DASHBOARD
    //
    // GET /api/students/dashboard?studentId=KDU/BSE/25/0001
    // =========================================================

    @GetMapping("/dashboard")
    public ResponseEntity<?> getDashboard(
            @RequestParam String studentId
    ) {

        User user = findUser(studentId);

        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        Map<String, Object> response =
                new LinkedHashMap<>();


        // =====================================================
        // STUDENT PROFILE
        // =====================================================

        StudentAcademicProfile profile =
                profileRepository
                        .findByUser(user)
                        .orElse(null);


        if (profile == null) {

            response.put("profile", null);

        } else {

            Map<String, Object> profileData =
                    new LinkedHashMap<>();

            profileData.put(
                    "userId",
                    user.getId()
            );

            profileData.put(
                    "studentId",
                    user.getStudentId()
            );

            profileData.put(
                    "intake",
                    profile.getIntake()
            );

            profileData.put(
                    "facultyId",
                    profile.getFacultyId()
            );

            profileData.put(
                    "degreeId",
                    profile.getDegreeId()
            );

            profileData.put(
                    "currentYear",
                    profile.getCurrentYear()
            );

            profileData.put(
                    "currentSemester",
                    profile.getCurrentSemester()
            );

            response.put(
                    "profile",
                    profileData
            );
        }


        // =====================================================
        // SEMESTER GPA RECORDS
        // =====================================================

        List<StudentSemesterGpa> gpas =
                gpaRepository.findByUserOrderBySemesterAsc(user);


        List<Map<String, Object>> semesterRecords =
                gpas.stream()
                        .map(gpa -> {

                            Map<String, Object> record =
                                    new LinkedHashMap<>();

                            record.put(
                                    "semester",
                                    gpa.getSemester()
                            );

                            record.put(
                                    "sgpa",
                                    gpa.getSgpa()
                            );

                            return record;
                        })
                        .toList();


        response.put(
                "semesterRecords",
                semesterRecords
        );


        // =====================================================
        // STUDENT GRADES
        // =====================================================

        List<StudentResult> results =
                resultRepository
                        .findByUserOrderBySemesterAscCourseCodeAsc(user);


        Map<String, List<Map<String, Object>>> grades =
                new LinkedHashMap<>();


        for (StudentResult result : results) {

            String semesterKey =
                    String.valueOf(
                            result.getSemester()
                    );


            Map<String, Object> gradeData =
                    new LinkedHashMap<>();


            gradeData.put(
                    "courseCode",
                    result.getCourseCode()
            );

            gradeData.put(
                    "grade",
                    result.getGrade()
            );

            gradeData.put(
                    "gradePoint",
                    result.getGradePoint()
            );


            grades.computeIfAbsent(
                    semesterKey,
                    key -> new ArrayList<>()
            ).add(gradeData);
        }


        response.put(
                "grades",
                grades
        );


        return ResponseEntity.ok(response);
    }


    // =========================================================
    // SAVE / UPDATE ACADEMIC PROFILE
    //
    // PUT /api/students/profile?studentId=KDU/BSE/25/0001
    //
    // Body:
    //
    // {
    //     "studentId": "KDU/BSE/25/0001",
    //     "intake": 42,
    //     "facultyId": "F001",
    //     "degreeId": "D001",
    //     "currentYear": 2,
    //     "currentSemester": 4
    // }
    // =========================================================

    @Transactional
    @PutMapping("/profile")
    public ResponseEntity<?> saveProfile(
            @RequestParam String studentId,
            @RequestBody Map<String, Object> request
    ) {

        System.out.println(
                "=============================================="
        );

        System.out.println(
                ">>> SAVE PROFILE"
        );

        System.out.println(
                ">>> studentId = [" + studentId + "]"
        );

        System.out.println(
                ">>> request = " + request
        );

        System.out.println(
                "=============================================="
        );


        User user = findUser(studentId);

        if (user == null) {
            return ResponseEntity.notFound().build();
        }


        try {

            Object intakeValue =
                    request.get("intake");

            Object facultyValue =
                    request.get("facultyId");

            Object degreeValue =
                    request.get("degreeId");

            Object currentYearValue =
                    request.get("currentYear");

            Object currentSemesterValue =
                    request.get("currentSemester");


            // =================================================
            // REQUIRED VALUES
            // =================================================

            if (intakeValue == null ||
                    facultyValue == null ||
                    degreeValue == null ||
                    currentYearValue == null ||
                    currentSemesterValue == null) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Faculty, Degree, Intake, Year and Semester are required."
                                )
                        );
            }


            Integer intake =
                    Integer.valueOf(
                            intakeValue.toString()
                    );


            String facultyId =
                    facultyValue
                            .toString()
                            .trim();


            String degreeId =
                    degreeValue
                            .toString()
                            .trim();


            Integer currentYear =
                    Integer.valueOf(
                            currentYearValue.toString()
                    );


            Integer currentSemester =
                    Integer.valueOf(
                            currentSemesterValue.toString()
                    );


            // =================================================
            // STRING VALIDATION
            // =================================================

            if (facultyId.isBlank()) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Faculty is required."
                                )
                        );
            }


            if (degreeId.isBlank()) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Degree is required."
                                )
                        );
            }


            // =================================================
            // INTAKE VALIDATION
            // =================================================

            if (intake < 1) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Invalid intake."
                                )
                        );
            }


            // =================================================
            // YEAR VALIDATION
            // =================================================

            if (currentYear < 1 ||
                    currentYear > 4) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Year must be between 1 and 4."
                                )
                        );
            }


            // =================================================
            // SEMESTER VALIDATION
            // =================================================

            if (currentSemester < 1 ||
                    currentSemester > 8) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Semester must be between 1 and 8."
                                )
                        );
            }


            // =================================================
            // FIND EXISTING PROFILE
            // =================================================

            StudentAcademicProfile profile =
                    profileRepository
                            .findByUser(user)
                            .orElse(null);


            if (profile == null) {

                profile =
                        new StudentAcademicProfile();

                profile.setUser(user);
            }


            // =================================================
            // UPDATE PROFILE
            // =================================================

            profile.setIntake(intake);
            profile.setFacultyId(facultyId);
            profile.setDegreeId(degreeId);
            profile.setCurrentYear(currentYear);
            profile.setCurrentSemester(currentSemester);


            StudentAcademicProfile saved =
                    profileRepository.save(profile);


            // =================================================
            // REMOVE FUTURE SEMESTER GPA RECORDS
            //
            // Example:
            //
            // Old current semester = 6
            // New current semester = 4
            //
            // Delete semesters 5, 6, 7 and 8.
            // =================================================

            gpaRepository.deleteByUserAndSemesterGreaterThan(
                    user,
                    currentSemester
            );


            // =================================================
            // REMOVE FUTURE SEMESTER GRADE RECORDS
            // =================================================

            resultRepository.deleteByUserAndSemesterGreaterThan(
                    user,
                    currentSemester
            );


            // =================================================
            // RESPONSE
            // =================================================

            Map<String, Object> response =
                    new LinkedHashMap<>();


            response.put(
                    "userId",
                    user.getId()
            );

            response.put(
                    "studentId",
                    user.getStudentId()
            );

            response.put(
                    "intake",
                    saved.getIntake()
            );

            response.put(
                    "facultyId",
                    saved.getFacultyId()
            );

            response.put(
                    "degreeId",
                    saved.getDegreeId()
            );

            response.put(
                    "currentYear",
                    saved.getCurrentYear()
            );

            response.put(
                    "currentSemester",
                    saved.getCurrentSemester()
            );

            response.put(
                    "message",
                    "Academic profile saved successfully."
            );


            return ResponseEntity.ok(response);


        } catch (NumberFormatException exception) {

            return ResponseEntity.badRequest()
                    .body(
                            Map.of(
                                    "message",
                                    "Invalid numeric academic profile value."
                            )
                    );


        } catch (Exception exception) {

            exception.printStackTrace();

            return ResponseEntity.internalServerError()
                    .body(
                            Map.of(
                                    "message",
                                    "Unable to save academic profile."
                            )
                    );
        }
    }


    // =========================================================
    // SAVE / UPDATE ONE SEMESTER GPA
    //
    // PUT /api/students/sgpa?studentId=KDU/BSE/25/0001
    //
    // Body:
    //
    // {
    //     "semester": 2,
    //     "sgpa": 3.7500
    // }
    // =========================================================

    @PutMapping("/sgpa")
    public ResponseEntity<?> saveStudentSemesterGpa(
            @RequestParam String studentId,
            @RequestBody Map<String, Object> request
    ) {

        User user = findUser(studentId);

        if (user == null) {
            return ResponseEntity.notFound().build();
        }


        try {

            Object semesterValue =
                    request.get("semester");

            Object sgpaValue =
                    request.get("sgpa");


            // =================================================
            // REQUIRED VALUES
            // =================================================

            if (semesterValue == null ||
                    sgpaValue == null) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Semester and SGPA are required."
                                )
                        );
            }


            Integer semester =
                    Integer.valueOf(
                            semesterValue.toString()
                    );


            BigDecimal sgpa =
                    new BigDecimal(
                            sgpaValue.toString()
                    );


            // =================================================
            // SEMESTER VALIDATION
            // =================================================

            if (semester < 1 ||
                    semester > 8) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Semester must be between 1 and 8."
                                )
                        );
            }


            // =================================================
            // CHECK CURRENT SEMESTER
            // =================================================

            StudentAcademicProfile profile =
                    profileRepository
                            .findByUser(user)
                            .orElse(null);


            if (profile != null &&
                    profile.getCurrentSemester() != null &&
                    semester > profile.getCurrentSemester()) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "You cannot save SGPA for Semester "
                                                + semester
                                                + ". Your current semester is Semester "
                                                + profile.getCurrentSemester()
                                                + "."
                                )
                        );
            }


            // =================================================
            // SGPA VALIDATION
            // =================================================

            if (sgpa.compareTo(
                    BigDecimal.ZERO
            ) < 0 ||
                    sgpa.compareTo(
                            new BigDecimal("4.0000")
                    ) > 0) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "SGPA must be between 0.0000 and 4.0000."
                                )
                        );
            }


            // =================================================
            // ALWAYS STORE 4 DECIMAL PLACES
            // =================================================

            sgpa =
                    sgpa.setScale(
                            4,
                            RoundingMode.HALF_UP
                    );


            // =================================================
            // FIND EXISTING GPA
            // =================================================

            Optional<StudentSemesterGpa> existingRecord =
                    gpaRepository.findByUserAndSemester(
                            user,
                            semester
                    );


            StudentSemesterGpa record;


            if (existingRecord.isPresent()) {

                record =
                        existingRecord.get();

            } else {

                record =
                        new StudentSemesterGpa();

                record.setUser(user);
                record.setSemester(semester);
            }


            // =================================================
            // SAVE GPA
            // =================================================

            record.setSgpa(sgpa);


            StudentSemesterGpa saved =
                    gpaRepository.save(record);


            // =================================================
            // RESPONSE
            // =================================================

            Map<String, Object> response =
                    new LinkedHashMap<>();


            response.put(
                    "id",
                    saved.getId()
            );

            response.put(
                    "semester",
                    saved.getSemester()
            );

            response.put(
                    "sgpa",
                    saved.getSgpa()
            );

            response.put(
                    "message",
                    "SGPA saved successfully."
            );


            return ResponseEntity.ok(response);


        } catch (NumberFormatException exception) {

            return ResponseEntity.badRequest()
                    .body(
                            Map.of(
                                    "message",
                                    "Invalid semester or SGPA value."
                            )
                    );


        } catch (Exception exception) {

            exception.printStackTrace();

            return ResponseEntity.internalServerError()
                    .body(
                            Map.of(
                                    "message",
                                    "Unable to save SGPA."
                            )
                    );
        }
    }


    // =========================================================
    // SAVE / UPDATE SEMESTER GRADES
    //
    // PUT /api/students/results?studentId=KDU/BSE/25/0001
    //
    // Body:
    //
    // {
    //     "studentId": "KDU/BSE/25/0001",
    //     "degreeId": "D001",
    //     "semester": 1,
    //     "grades": [
    //         {
    //             "courseCode": "CS22012",
    //             "grade": "A",
    //             "gradePoint": 4
    //         }
    //     ]
    // }
    // =========================================================

    @Transactional
    @PutMapping("/results")
    public ResponseEntity<?> saveStudentResults(
            @RequestParam String studentId,
            @RequestBody Map<String, Object> request
    ) {

        System.out.println(
                "=============================================="
        );

        System.out.println(
                ">>> SAVE STUDENT RESULTS"
        );

        System.out.println(
                ">>> studentId = [" + studentId + "]"
        );

        System.out.println(
                ">>> request = " + request
        );

        System.out.println(
                "=============================================="
        );


        User user = findUser(studentId);

        if (user == null) {
            return ResponseEntity.notFound().build();
        }


        try {

            Object degreeIdValue =
                    request.get("degreeId");

            Object semesterValue =
                    request.get("semester");

            Object gradesValue =
                    request.get("grades");


            // =================================================
            // REQUIRED VALUES
            // =================================================

            if (degreeIdValue == null ||
                    semesterValue == null ||
                    gradesValue == null) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Degree, semester and grades are required."
                                )
                        );
            }


            String degreeId =
                    degreeIdValue
                            .toString()
                            .trim();


            Integer semester =
                    Integer.valueOf(
                            semesterValue.toString()
                    );


            // =================================================
            // BASIC VALIDATION
            // =================================================

            if (degreeId.isBlank()) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Degree is required."
                                )
                        );
            }


            if (semester < 1 ||
                    semester > 8) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Semester must be between 1 and 8."
                                )
                        );
            }


            // =================================================
            // GET STUDENT ACADEMIC PROFILE
            // =================================================

            StudentAcademicProfile profile =
                    profileRepository
                            .findByUser(user)
                            .orElse(null);


            if (profile == null ||
                    profile.getCurrentSemester() == null) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Please complete your academic profile first."
                                )
                        );
            }


            Integer currentSemester =
                    profile.getCurrentSemester();


            // =================================================
            // PREVENT FUTURE SEMESTER GRADES
            // =================================================

            if (semester > currentSemester) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "You cannot save grades for Semester "
                                                + semester
                                                + ". Your current semester is Semester "
                                                + currentSemester
                                                + "."
                                )
                        );
            }


            // =================================================
            // VERIFY DEGREE
            // =================================================

            if (!degreeId.equals(
                    profile.getDegreeId()
            )) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "The selected degree does not match the student's academic profile."
                                )
                        );
            }


            // =================================================
            // VALIDATE GRADES ARRAY
            // =================================================

            if (!(gradesValue instanceof List<?> gradesList) ||
                    gradesList.isEmpty()) {

                return ResponseEntity.badRequest()
                        .body(
                                Map.of(
                                        "message",
                                        "Please provide at least one module grade."
                                )
                        );
            }


            // =================================================
            // PROCESS EACH GRADE
            // =================================================

            for (Object gradeObject : gradesList) {

                if (!(gradeObject instanceof Map<?, ?> gradeMap)) {

                    return ResponseEntity.badRequest()
                            .body(
                                    Map.of(
                                            "message",
                                            "Invalid grade data."
                                    )
                            );
                }


                Object courseCodeValue =
                        gradeMap.get("courseCode");

                Object gradeValue =
                        gradeMap.get("grade");

                Object gradePointValue =
                        gradeMap.get("gradePoint");


                // =================================================
                // REQUIRED GRADE VALUES
                // =================================================

                if (courseCodeValue == null ||
                        gradeValue == null) {

                    return ResponseEntity.badRequest()
                            .body(
                                    Map.of(
                                            "message",
                                            "Course code and grade are required."
                                    )
                            );
                }


                String courseCode =
                        courseCodeValue
                                .toString()
                                .trim();


                String grade =
                        gradeValue
                                .toString()
                                .trim()
                                .toUpperCase();


                if (courseCode.isBlank()) {

                    return ResponseEntity.badRequest()
                            .body(
                                    Map.of(
                                            "message",
                                            "Course code cannot be empty."
                                    )
                            );
                }


                if (grade.isBlank()) {

                    return ResponseEntity.badRequest()
                            .body(
                                    Map.of(
                                            "message",
                                            "Grade cannot be empty."
                                    )
                            );
                }


                // =================================================
                // VERIFY COURSE EXISTS
                // =================================================

                CourseModule courseModule =
                        courseModuleRepository
                                .findById(courseCode)
                                .orElse(null);


                if (courseModule == null) {

                    return ResponseEntity.badRequest()
                            .body(
                                    Map.of(
                                            "message",
                                            "Course "
                                                    + courseCode
                                                    + " does not exist."
                                    )
                            );
                }


                // =================================================
                // VERIFY COURSE SEMESTER
                // =================================================

                if (!semester.equals(
                        courseModule.getSemester()
                )) {

                    return ResponseEntity.badRequest()
                            .body(
                                    Map.of(
                                            "message",
                                            "Course "
                                                    + courseCode
                                                    + " does not belong to Semester "
                                                    + semester
                                                    + "."
                                    )
                            );
                }


                // =================================================
                // VERIFY COURSE BELONGS TO DEGREE
                // =================================================

                boolean belongsToDegree =
                        degreeModuleRepository
                                .findByDegreeId(degreeId)
                                .stream()
                                .anyMatch(
                                        degreeModule ->
                                                courseCode.equals(
                                                        degreeModule.getCourseCode()
                                                )
                                );


                if (!belongsToDegree) {

                    return ResponseEntity.badRequest()
                            .body(
                                    Map.of(
                                            "message",
                                            "Course "
                                                    + courseCode
                                                    + " does not belong to the selected degree."
                                    )
                            );
                }


                // =================================================
                // PARSE GRADE POINT
                // =================================================

                BigDecimal gradePoint = null;


                if (gradePointValue != null &&
                        !gradePointValue
                                .toString()
                                .isBlank() &&
                        !"null".equalsIgnoreCase(
                                gradePointValue.toString()
                        )) {

                    gradePoint =
                            new BigDecimal(
                                    gradePointValue
                                            .toString()
                            );


                    if (gradePoint.compareTo(
                            BigDecimal.ZERO
                    ) < 0 ||
                            gradePoint.compareTo(
                                    new BigDecimal("4.00")
                            ) > 0) {

                        return ResponseEntity.badRequest()
                                .body(
                                        Map.of(
                                                "message",
                                                "Grade point for "
                                                        + courseCode
                                                        + " must be between 0.00 and 4.00."
                                        )
                                );
                    }


                    gradePoint =
                            gradePoint.setScale(
                                    2,
                                    RoundingMode.HALF_UP
                            );
                }


                // =================================================
                // SAVE / UPDATE GRADE
                // =================================================

                Optional<StudentResult> existing =
                        resultRepository
                                .findByUserAndCourseCodeAndSemester(
                                        user,
                                        courseCode,
                                        semester
                                );


                StudentResult result;


                if (existing.isPresent()) {

                    result =
                            existing.get();

                } else {

                    result =
                            new StudentResult();

                    result.setUser(user);
                    result.setCourseCode(courseCode);
                    result.setSemester(semester);
                }


                result.setGrade(grade);
                result.setGradePoint(gradePoint);


                resultRepository.save(result);
            }


            // =================================================
            // RESPONSE
            // =================================================

            Map<String, Object> response =
                    new LinkedHashMap<>();


            response.put(
                    "studentId",
                    user.getStudentId()
            );

            response.put(
                    "semester",
                    semester
            );

            response.put(
                    "message",
                    "Semester "
                            + semester
                            + " grades saved successfully."
            );


            return ResponseEntity.ok(response);


        } catch (NumberFormatException exception) {

            return ResponseEntity.badRequest()
                    .body(
                            Map.of(
                                    "message",
                                    "Invalid semester or grade point value."
                            )
                    );


        } catch (Exception exception) {

            exception.printStackTrace();

            return ResponseEntity.internalServerError()
                    .body(
                            Map.of(
                                    "message",
                                    "Unable to save student grades."
                            )
                    );
        }
    }


    // =========================================================
    // FIND USER
    //
    // Supports:
    //
    // 1. Student ID
    //    KDU/BSE/25/0001
    //
    // 2. Numeric User ID
    //    1
    // =========================================================

    private User findUser(String studentId) {

        if (studentId == null ||
                studentId.isBlank()) {

            return null;
        }


        String value =
                studentId.trim();


        // =====================================================
        // FIRST: STUDENT ID
        // =====================================================

        User user =
                userRepository
                        .findByStudentId(value)
                        .orElse(null);


        if (user != null) {
            return user;
        }


        // =====================================================
        // SECOND: NUMERIC USER ID
        // =====================================================

        try {

            Long userId =
                    Long.valueOf(value);


            return userRepository
                    .findById(userId)
                    .orElse(null);


        } catch (NumberFormatException ignored) {

            return null;
        }
    }
}

