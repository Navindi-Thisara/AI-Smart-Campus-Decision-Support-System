package com.smartcampus.backend.service;

import com.smartcampus.backend.dto.EligibilityResponse;
import com.smartcampus.backend.entity.CourseModule;
import com.smartcampus.backend.entity.StudentAcademicProfile;
import com.smartcampus.backend.entity.StudentEligibilityRecord;
import com.smartcampus.backend.entity.StudentResult;
import com.smartcampus.backend.entity.User;
import com.smartcampus.backend.repository.CourseModuleRepository;
import com.smartcampus.backend.repository.StudentAcademicProfileRepository;
import com.smartcampus.backend.repository.StudentEligibilityRecordRepository;
import com.smartcampus.backend.repository.StudentResultRepository;
import com.smartcampus.backend.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class EligibilityService {

    private static final BigDecimal MIN_ATTENDANCE =
            new BigDecimal("80.00");

    private final UserRepository userRepository;
    private final StudentAcademicProfileRepository profileRepository;
    private final StudentEligibilityRecordRepository eligibilityRepository;
    private final CourseModuleRepository courseModuleRepository;
    private final StudentResultRepository studentResultRepository;

    public EligibilityService(
            UserRepository userRepository,
            StudentAcademicProfileRepository profileRepository,
            StudentEligibilityRecordRepository eligibilityRepository,
            CourseModuleRepository courseModuleRepository,
            StudentResultRepository studentResultRepository
    ) {
        this.userRepository = userRepository;
        this.profileRepository = profileRepository;
        this.eligibilityRepository = eligibilityRepository;
        this.courseModuleRepository = courseModuleRepository;
        this.studentResultRepository = studentResultRepository;
    }

    /**
     * Single source of truth for eligibility.
     *
     * The semester is NOT received from the frontend.
     * It is always taken from the student's academic profile.
     */
    public EligibilityResponse evaluateEligibility(String studentId) {

        List<String> explanations = new ArrayList<>();

        // =========================================================
        // FIND STUDENT
        // =========================================================

        User user = userRepository.findByStudentId(studentId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Student not found: " + studentId
                        )
                );

        // =========================================================
        // RULE 01 - ACADEMIC PROFILE
        // =========================================================

        StudentAcademicProfile profile =
                profileRepository.findByUser(user)
                        .orElse(null);

        if (profile == null) {

            explanations.add(
                    "Academic profile not found."
            );

            return new EligibilityResponse(
                    studentId,
                    null,
                    EligibilityStatus.NOT_ELIGIBLE.name(),
                    false,
                    explanations
            );
        }

        explanations.add(
                "Academic profile exists."
        );

        // =========================================================
        // GET CURRENT SEMESTER FROM DATABASE
        // =========================================================

        Integer currentSemester =
                profile.getCurrentSemester();

        if (currentSemester == null) {

            explanations.add(
                    "Current semester information is not available."
            );

            return new EligibilityResponse(
                    studentId,
                    null,
                    EligibilityStatus.CONDITIONALLY_ELIGIBLE.name(),
                    false,
                    explanations
            );
        }

        explanations.add(
                "Current semester: " + currentSemester + "."
        );

        // =========================================================
        // GET ATTENDANCE + FEE RECORD
        // =========================================================

        StudentEligibilityRecord record =
                eligibilityRepository
                        .findByUserAndSemester(
                                user,
                                currentSemester
                        )
                        .orElse(null);

        // =========================================================
        // RULE 02 - ATTENDANCE
        // =========================================================

        boolean attendanceEvaluated = false;
        boolean attendancePassed = false;

        if (record != null &&
                record.getAttendancePercentage() != null) {

            attendanceEvaluated = true;

            attendancePassed =
                    record.getAttendancePercentage()
                            .compareTo(MIN_ATTENDANCE) >= 0;

            if (attendancePassed) {

                explanations.add(
                        "Attendance requirement satisfied: "
                                + record.getAttendancePercentage()
                                + "%."
                );

            } else {

                explanations.add(
                        "Attendance requirement not satisfied: "
                                + record.getAttendancePercentage()
                                + "%."
                );
            }

        } else {

            explanations.add(
                    "Attendance information is not available."
            );
        }

        // =========================================================
        // RULE 03 - FEE PAYMENT
        // =========================================================

        boolean feeEvaluated = false;
        boolean feePassed = false;

        if (record != null &&
                record.getFeePaid() != null) {

            feeEvaluated = true;

            feePassed =
                    Boolean.TRUE.equals(
                            record.getFeePaid()
                    );

            if (feePassed) {

                explanations.add(
                        "Semester fee payment requirement satisfied."
                );

            } else {

                explanations.add(
                        "Semester fee has not been paid."
                );
            }

        } else {

            explanations.add(
                    "Semester fee payment information is not available."
            );
        }

        // =========================================================
        // RULE 04 - PREVIOUS REQUIRED MODULES
        // =========================================================

        boolean previousModulesPassed =
                checkPreviousRequiredModules(
                        user,
                        profile,
                        currentSemester,
                        explanations
                );

        // =========================================================
        // FINAL DECISION
        // =========================================================

        /*
         * Any evaluated mandatory rule that fails
         * means NOT_ELIGIBLE.
         */
        if ((attendanceEvaluated && !attendancePassed)
                || (feeEvaluated && !feePassed)
                || !previousModulesPassed) {

            return new EligibilityResponse(
                    studentId,
                    currentSemester,
                    EligibilityStatus.NOT_ELIGIBLE.name(),
                    false,
                    explanations
            );
        }

        /*
         * Everything required has been evaluated
         * and all requirements have passed.
         */
        if (attendanceEvaluated
                && feeEvaluated
                && attendancePassed
                && feePassed
                && previousModulesPassed) {

            return new EligibilityResponse(
                    studentId,
                    currentSemester,
                    EligibilityStatus.ELIGIBLE.name(),
                    true,
                    explanations
            );
        }

        /*
         * No evaluated rule has failed, but some required
         * information is missing.
         */
        return new EligibilityResponse(
                studentId,
                currentSemester,
                EligibilityStatus.CONDITIONALLY_ELIGIBLE.name(),
                false,
                explanations
        );
    }

    // =============================================================
    // RULE 04 - PREVIOUS REQUIRED MODULES
    // =============================================================

    private boolean checkPreviousRequiredModules(
            User user,
            StudentAcademicProfile profile,
            Integer currentSemester,
            List<String> explanations
    ) {

        /*
         * Semester 1 has no previous semester requirements.
         */
        if (currentSemester == null || currentSemester <= 1) {

            explanations.add(
                    "No previous required modules exist for Semester "
                            + currentSemester + "."
            );

            return true;
        }

        // =========================================================
        // GET STUDENT RESULTS
        // =========================================================

        List<StudentResult> studentResults =
                studentResultRepository
                        .findByUserOrderBySemesterAscCourseCodeAsc(
                                user
                        );

        // =========================================================
        // MAP RESULTS BY COURSE CODE
        // =========================================================

        Map<String, StudentResult> resultMap =
                new HashMap<>();

        for (StudentResult result : studentResults) {

            if (result.getCourseCode() != null) {

                resultMap.put(
                        result.getCourseCode().trim().toUpperCase(),
                        result
                );
            }
        }

        boolean allPreviousModulesPassed = true;

        // =========================================================
        // CHECK ALL PREVIOUS SEMESTERS
        // =========================================================

        for (int semester = 1;
             semester < currentSemester;
             semester++) {

            List<CourseModule> previousModules =
                    courseModuleRepository
                            .findModulesByDegreeAndSemester(
                                    profile.getDegreeId(),
                                    semester
                            );

            for (CourseModule courseModule : previousModules) {

                String courseCode =
                        courseModule.getCourseCode();

                if (courseCode == null) {
                    continue;
                }

                String normalizedCourseCode =
                        courseCode.trim().toUpperCase();

                StudentResult result =
                        resultMap.get(normalizedCourseCode);

                // -------------------------------------------------
                // NO RESULT
                // -------------------------------------------------

                if (result == null) {

                    allPreviousModulesPassed = false;

                    explanations.add(
                            "Previous required module not completed: "
                                    + courseCode
                                    + " - "
                                    + courseModule.getModuleName()
                    );

                    continue;
                }

                // -------------------------------------------------
                // RESULT EXISTS BUT NOT PASSED
                // -------------------------------------------------

                if (!isPassingGrade(result.getGrade())) {

                    allPreviousModulesPassed = false;

                    explanations.add(
                            "Previous required module not passed: "
                                    + courseCode
                                    + " - "
                                    + courseModule.getModuleName()
                                    + " (Grade: "
                                    + result.getGrade()
                                    + ")."
                    );
                }
            }
        }

        // =========================================================
        // ALL PREVIOUS MODULES PASSED
        // =========================================================

        if (allPreviousModulesPassed) {

            explanations.add(
                    "All required modules from previous semesters "
                            + "have been successfully completed."
            );
        }

        return allPreviousModulesPassed;
    }

    // =============================================================
    // PASSING GRADE
    // =============================================================

    private boolean isPassingGrade(String grade) {

        if (grade == null) {
            return false;
        }

        return switch (grade.trim().toUpperCase()) {

            case "A+",
                 "A",
                 "A-",
                 "B+",
                 "B",
                 "B-",
                 "C+",
                 "C",
                 "C-" -> true;

            default -> false;
        };
    }
}