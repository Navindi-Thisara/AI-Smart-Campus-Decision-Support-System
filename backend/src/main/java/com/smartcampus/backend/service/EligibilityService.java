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

    public EligibilityResponse evaluateEligibility(
            String studentId,
            Integer semester
    ) {

        List<String> explanations = new ArrayList<>();

        User user = userRepository.findByStudentId(studentId)
                .orElseThrow(() ->
                        new RuntimeException(
                                "Student not found: " + studentId
                        )
                );

        
        StudentAcademicProfile profile =
                profileRepository.findByUser(user)
                        .orElse(null);

        if (profile == null) {

            explanations.add(
                    "Academic profile not found."
            );

            return new EligibilityResponse(
                    studentId,
                    semester,
                    EligibilityStatus.NOT_ELIGIBLE.name(),
                    false,
                    explanations
            );
        }

        explanations.add(
                "Academic profile exists."
        );

       
        StudentEligibilityRecord record =
                eligibilityRepository
                        .findByUserAndSemester(user, semester)
                        .orElse(null);

        if (record == null) {

            explanations.add(
                    "Attendance and fee information is missing."
            );

            return new EligibilityResponse(
                    studentId,
                    semester,
                    EligibilityStatus.CONDITIONALLY_ELIGIBLE.name(),
                    false,
                    explanations
            );
        }

        
        boolean attendancePassed =
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

        boolean feePassed =
                Boolean.TRUE.equals(record.getFeePaid());

        if (feePassed) {

            explanations.add(
                    "Semester fee payment requirement satisfied."
            );

        } else {

            explanations.add(
                    "Semester fee has not been paid."
            );
        }

        boolean previousModulesPassed =
                checkPreviousRequiredModules(
                        user,
                        profile,
                        semester,
                        explanations
                );

        
        if (attendancePassed
                && feePassed
                && previousModulesPassed) {

            return new EligibilityResponse(
                    studentId,
                    semester,
                    EligibilityStatus.ELIGIBLE.name(),
                    true,
                    explanations
            );
        }

        if (!attendancePassed || !feePassed) {

            return new EligibilityResponse(
                    studentId,
                    semester,
                    EligibilityStatus.NOT_ELIGIBLE.name(),
                    false,
                    explanations
            );
        }

        return new EligibilityResponse(
                studentId,
                semester,
                EligibilityStatus.CONDITIONALLY_ELIGIBLE.name(),
                false,
                explanations
        );
    }


private boolean checkPreviousRequiredModules(
        User user,
        StudentAcademicProfile profile,
        Integer currentSemester,
        List<String> explanations
) {

    
    if (currentSemester == null || currentSemester <= 1) {

        explanations.add(
                "No previous required modules exist for Semester "
                        + currentSemester + "."
        );

        return true;
    }

   
    List<StudentResult> studentResults =
            studentResultRepository
                    .findByUserOrderBySemesterAscCourseCodeAsc(
                            user
                    );

    
    Map<String, StudentResult> resultMap =
            new HashMap<>();

    for (StudentResult result : studentResults) {

        if (result.getCourseCode() != null) {

            resultMap.put(
                    result.getCourseCode(),
                    result
            );
        }
    }

    boolean allPreviousModulesPassed = true;

    
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

            StudentResult result =
                    resultMap.get(courseCode);

            
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

   
    if (allPreviousModulesPassed) {

        explanations.add(
                "All required modules from previous semesters "
                        + "have been successfully completed."
        );
    }

    return allPreviousModulesPassed;
}



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

