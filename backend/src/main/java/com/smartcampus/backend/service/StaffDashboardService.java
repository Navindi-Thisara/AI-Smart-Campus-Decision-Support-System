package com.smartcampus.backend.service;

import com.smartcampus.backend.dto.EligibilityResponse;
import com.smartcampus.backend.dto.StaffDashboardResponse;
import com.smartcampus.backend.entity.StudentAcademicProfile;
import com.smartcampus.backend.entity.StudentEligibilityRecord;
import com.smartcampus.backend.entity.StudentSemesterGpa;
import com.smartcampus.backend.entity.User;
import com.smartcampus.backend.repository.StudentAcademicProfileRepository;
import com.smartcampus.backend.repository.StudentEligibilityRecordRepository;
import com.smartcampus.backend.repository.StudentSemesterGpaRepository;
import com.smartcampus.backend.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class StaffDashboardService {

    private final StudentAcademicProfileRepository profileRepository;
    private final StudentSemesterGpaRepository gpaRepository;
    private final StudentEligibilityRecordRepository eligibilityRepository;
    private final EligibilityService eligibilityService;
    private final UserRepository userRepository;

    public StaffDashboardService(
            StudentAcademicProfileRepository profileRepository,
            StudentSemesterGpaRepository gpaRepository,
            StudentEligibilityRecordRepository eligibilityRepository,
            EligibilityService eligibilityService,
            UserRepository userRepository
    ) {
        this.profileRepository = profileRepository;
        this.gpaRepository = gpaRepository;
        this.eligibilityRepository = eligibilityRepository;
        this.eligibilityService = eligibilityService;
        this.userRepository = userRepository;
    }

    public StaffDashboardResponse getDashboard() {

        List<StudentAcademicProfile> profiles =
                profileRepository.findAllByOrderByIdAsc();

        long totalStudents =
                userRepository.countStudentUsers();

        Map<Long, Map<Integer, BigDecimal>> gpaByStudent =
                buildGpaMap();

        List<StaffDashboardResponse.SemesterPerformance>
                semesterPerformance =
                calculateSemesterPerformance();

        long eligibleStudents = 0;
        long conditionallyEligibleStudents = 0;
        long notEligibleStudents = 0;

        List<StaffDashboardResponse.StudentAttention>
                attentionStudents =
                new ArrayList<>();

        for (StudentAcademicProfile profile : profiles) {

            User user = profile.getUser();

            if (user == null) {
                continue;
            }

            Integer currentSemester =
                    profile.getCurrentSemester();

            if (currentSemester == null) {
                continue;
            }

            EligibilityResponse eligibilityResponse =
                    eligibilityService.evaluateEligibility(
                            user.getStudentId()
                    );

            String status =
                    eligibilityResponse != null
                            ? eligibilityResponse.getStatus()
                            : "CONDITIONALLY_ELIGIBLE";

            switch (status) {

                case "ELIGIBLE" ->
                        eligibleStudents++;

                case "CONDITIONALLY_ELIGIBLE" ->
                        conditionallyEligibleStudents++;

                case "NOT_ELIGIBLE" ->
                        notEligibleStudents++;

                default ->
                        conditionallyEligibleStudents++;
            }

            StudentEligibilityRecord eligibilityRecord =
                    eligibilityRepository
                            .findByUser_IdAndSemester(
                                    user.getId(),
                                    currentSemester
                            )
                            .orElse(null);

            if (!"ELIGIBLE".equals(status)) {

                BigDecimal currentSgpa =
                        gpaByStudent
                                .getOrDefault(
                                        user.getId(),
                                        Map.of()
                                )
                                .get(currentSemester);

                BigDecimal attendance =
                        eligibilityRecord != null
                                ? eligibilityRecord
                                .getAttendancePercentage()
                                : null;

                Boolean feePaid =
                        eligibilityRecord != null
                                ? eligibilityRecord.getFeePaid()
                                : null;

                String reason =
                        buildAttentionReason(
                                eligibilityResponse
                        );

                attentionStudents.add(
                        new StaffDashboardResponse.StudentAttention(
                                user.getStudentId(),
                                user.getFullName(),
                                user.getEmail(),
                                profile.getDegreeId(),
                                profile.getFacultyId(),
                                profile.getCurrentYear(),
                                currentSemester,
                                currentSgpa,
                                attendance,
                                feePaid,
                                status,
                                reason
                        )
                );
            }
        }

        attentionStudents.sort(
                Comparator
                        .comparingInt(
                                this::attentionPriority
                        )
                        .reversed()
                        .thenComparing(
                                StaffDashboardResponse.StudentAttention
                                        ::getFullName,
                                Comparator.nullsLast(
                                        String.CASE_INSENSITIVE_ORDER
                                )
                        )
        );

        List<StaffDashboardResponse.StudentAttention>
                topAttentionStudents =
                attentionStudents.stream()
                        .limit(10)
                        .toList();

        BigDecimal overallAverageSgpa =
                calculateOverallAverageSgpa();

        return new StaffDashboardResponse(
                totalStudents,
                eligibleStudents,
                conditionallyEligibleStudents,
                notEligibleStudents,
                overallAverageSgpa,
                semesterPerformance,
                topAttentionStudents
        );
    }

    private Map<Long, Map<Integer, BigDecimal>>
    buildGpaMap() {

        Map<Long, Map<Integer, BigDecimal>> result =
                new HashMap<>();

        List<StudentSemesterGpa> records =
                gpaRepository.findAllByOrderBySemesterAsc();

        for (StudentSemesterGpa record : records) {

            if (record.getUser() == null
                    || record.getSemester() == null
                    || record.getSgpa() == null) {
                continue;
            }

            result
                    .computeIfAbsent(
                            record.getUser().getId(),
                            ignored -> new HashMap<>()
                    )
                    .put(
                            record.getSemester(),
                            record.getSgpa()
                    );
        }

        return result;
    }

    private List<StaffDashboardResponse.SemesterPerformance>
    calculateSemesterPerformance() {

        Map<Integer, List<BigDecimal>> values =
                new HashMap<>();

        List<StudentSemesterGpa> records =
                gpaRepository.findAll();

        for (StudentSemesterGpa record : records) {

            if (record.getSemester() == null
                    || record.getSgpa() == null) {
                continue;
            }

            if (record.getSgpa().compareTo(
                    BigDecimal.ZERO
            ) < 0
                    || record.getSgpa().compareTo(
                    new BigDecimal("4.00")
            ) > 0) {
                continue;
            }

            values
                    .computeIfAbsent(
                            record.getSemester(),
                            ignored -> new ArrayList<>()
                    )
                    .add(record.getSgpa());
        }

        return values.entrySet()
                .stream()
                .sorted(Map.Entry.comparingByKey())
                .map(entry -> {

                    BigDecimal total =
                            entry.getValue()
                                    .stream()
                                    .reduce(
                                            BigDecimal.ZERO,
                                            BigDecimal::add
                                    );

                    BigDecimal average =
                            total.divide(
                                    BigDecimal.valueOf(
                                            entry.getValue().size()
                                    ),
                                    4,
                                    RoundingMode.HALF_UP
                            );

                    return new StaffDashboardResponse
                            .SemesterPerformance(
                                    entry.getKey(),
                                    average
                            );
                })
                .toList();
    }

    private BigDecimal calculateOverallAverageSgpa() {

        List<StudentSemesterGpa> records =
                gpaRepository.findAll();

        BigDecimal total =
                BigDecimal.ZERO;

        long count = 0;

        for (StudentSemesterGpa record : records) {

            if (record.getSgpa() == null) {
                continue;
            }

            if (record.getSgpa().compareTo(
                    BigDecimal.ZERO
            ) < 0
                    || record.getSgpa().compareTo(
                    new BigDecimal("4.00")
            ) > 0) {
                continue;
            }

            total =
                    total.add(record.getSgpa());

            count++;
        }

        if (count == 0) {

            return BigDecimal.ZERO.setScale(
                    4,
                    RoundingMode.HALF_UP
            );
        }

        return total.divide(
                BigDecimal.valueOf(count),
                4,
                RoundingMode.HALF_UP
        );
    }

    private String buildAttentionReason(
            EligibilityResponse eligibilityResponse
    ) {

        if (eligibilityResponse == null) {
            return "Academic eligibility requires review";
        }

        List<String> explanations =
                eligibilityResponse.getExplanations();

        if (explanations == null
                || explanations.isEmpty()) {

            return "Academic eligibility requires review";
        }

        /*
         * Remove explanations that only describe successful
         * checks. Keep the actual problems.
         */
        List<String> relevantReasons =
                explanations.stream()
                        .filter(explanation ->
                                explanation != null
                                        && !explanation.isBlank()
                                        && !isSuccessfulExplanation(
                                                explanation
                                        )
                        )
                        .toList();

        if (!relevantReasons.isEmpty()) {

            return String.join(
                    " • ",
                    relevantReasons
            );
        }

        return "Academic eligibility requires review";
    }

    private boolean isSuccessfulExplanation(
            String explanation
    ) {

        String text =
                explanation.toLowerCase();

        return text.contains(
                "academic profile exists"
        )
                || text.contains(
                "attendance requirement satisfied"
        )
                || text.contains(
                "semester fee payment requirement satisfied"
        )
                || text.contains(
                "all required modules from previous semesters"
        )
                || text.contains(
                "no previous required modules exist"
        );
    }

    private int attentionPriority(
            StaffDashboardResponse.StudentAttention student
    ) {

        if ("NOT_ELIGIBLE".equals(
                student.getEligibilityStatus()
        )) {
            return 3;
        }

        if ("CONDITIONALLY_ELIGIBLE".equals(
                student.getEligibilityStatus()
        )) {
            return 2;
        }

        return 1;
    }

    public void updateEligibilityData(
            String studentId,
            Integer semester,
            BigDecimal attendancePercentage,
            Boolean feePaid
    ) {

        if (studentId == null || studentId.isBlank()) {
            throw new IllegalArgumentException(
                    "Student ID is required"
            );
        }

        if (semester == null || semester < 1) {
            throw new IllegalArgumentException(
                    "Valid semester is required"
            );
        }

        if (attendancePercentage == null
                || attendancePercentage.compareTo(
                        BigDecimal.ZERO
                ) < 0
                || attendancePercentage.compareTo(
                        new BigDecimal("100.00")
                ) > 0) {

            throw new IllegalArgumentException(
                    "Attendance must be between 0 and 100"
            );
        }

        if (feePaid == null) {
            throw new IllegalArgumentException(
                    "Fee payment status is required"
            );
        }

        User user =
                userRepository
                        .findByStudentId(studentId)
                        .orElseThrow(() ->
                                new IllegalArgumentException(
                                        "Student not found: "
                                                + studentId
                                )
                        );

        StudentEligibilityRecord record =
                eligibilityRepository
                        .findByUser_IdAndSemester(
                                user.getId(),
                                semester
                        )
                        .orElseGet(() -> {

                            StudentEligibilityRecord newRecord =
                                    new StudentEligibilityRecord();

                            newRecord.setUser(user);
                            newRecord.setSemester(semester);

                            return newRecord;
                        });

        record.setAttendancePercentage(
                attendancePercentage
        );

        record.setFeePaid(feePaid);

        eligibilityRepository.save(record);
    }
}
