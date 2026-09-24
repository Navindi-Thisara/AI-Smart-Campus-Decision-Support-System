package com.smartcampus.backend.service;

import com.smartcampus.backend.dto.EligibilityResponse;
import com.smartcampus.backend.dto.StaffDashboardResponse;
import com.smartcampus.backend.entity.StudentAcademicProfile;
import com.smartcampus.backend.entity.StudentEligibilityRecord;
import com.smartcampus.backend.entity.StudentResult;
import com.smartcampus.backend.entity.StudentSemesterGpa;
import com.smartcampus.backend.entity.User;
import com.smartcampus.backend.repository.StudentAcademicProfileRepository;
import com.smartcampus.backend.repository.StudentEligibilityRecordRepository;
import com.smartcampus.backend.repository.StudentResultRepository;
import com.smartcampus.backend.repository.StudentSemesterGpaRepository;
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

    private static final BigDecimal MIN_ATTENDANCE =
            new BigDecimal("80.00");

    private final StudentAcademicProfileRepository profileRepository;
    private final StudentSemesterGpaRepository gpaRepository;
    private final StudentEligibilityRecordRepository eligibilityRepository;
    private final StudentResultRepository resultRepository;

    public StaffDashboardService(
            StudentAcademicProfileRepository profileRepository,
            StudentSemesterGpaRepository gpaRepository,
            StudentEligibilityRecordRepository eligibilityRepository,
            StudentResultRepository resultRepository
    ) {
        this.profileRepository = profileRepository;
        this.gpaRepository = gpaRepository;
        this.eligibilityRepository = eligibilityRepository;
        this.resultRepository = resultRepository;
    }

    public StaffDashboardResponse getDashboard() {

        List<StudentAcademicProfile> profiles =
                profileRepository.findAllByOrderByIdAsc();

        long totalStudents = profiles.size();

        Map<Long, Map<Integer, BigDecimal>> gpaByStudent =
                buildGpaMap();

        Map<Long, Map<Integer, StudentEligibilityRecord>>
                eligibilityByStudent =
                buildEligibilityMap();

        Map<Long, Map<String, StudentResult>> resultsByStudent =
                buildResultMap();

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

            StudentEligibilityRecord eligibilityRecord =
                    eligibilityByStudent
                            .getOrDefault(user.getId(), Map.of())
                            .get(currentSemester);

            Map<String, StudentResult> studentResults =
                    resultsByStudent.getOrDefault(
                            user.getId(),
                            Map.of()
                    );

            String status =
                    calculateEligibilityStatus(
                            profile,
                            eligibilityRecord,
                            studentResults
                    );

            switch (status) {

                case "ELIGIBLE" ->
                        eligibleStudents++;

                case "CONDITIONALLY_ELIGIBLE" ->
                        conditionallyEligibleStudents++;

                case "NOT_ELIGIBLE" ->
                        notEligibleStudents++;
            }

            if (!"ELIGIBLE".equals(status)) {

                BigDecimal currentSgpa =
                        gpaByStudent
                                .getOrDefault(user.getId(), Map.of())
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
                                profile,
                                eligibilityRecord,
                                studentResults
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

    private Map<Long, Map<Integer, StudentEligibilityRecord>>
    buildEligibilityMap() {

        Map<Long, Map<Integer, StudentEligibilityRecord>>
                result =
                new HashMap<>();

        List<StudentEligibilityRecord> records =
                eligibilityRepository
                        .findAllByOrderBySemesterAsc();

        for (StudentEligibilityRecord record : records) {

            if (record.getUser() == null
                    || record.getSemester() == null) {
                continue;
            }

            result
                    .computeIfAbsent(
                            record.getUser().getId(),
                            ignored -> new HashMap<>()
                    )
                    .put(
                            record.getSemester(),
                            record
                    );
        }

        return result;
    }

    private Map<Long, Map<String, StudentResult>>
    buildResultMap() {

        Map<Long, Map<String, StudentResult>> result =
                new HashMap<>();

        List<StudentResult> records =
                resultRepository.findAllByOrderBySemesterAscCourseCodeAsc();

        for (StudentResult studentResult : records) {

            if (studentResult.getUser() == null
                    || studentResult.getCourseCode() == null) {
                continue;
            }

            result
                    .computeIfAbsent(
                            studentResult.getUser().getId(),
                            ignored -> new HashMap<>()
                    )
                    .put(
                            studentResult.getCourseCode(),
                            studentResult
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

            if (record.getSgpa().compareTo(BigDecimal.ZERO) < 0
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

        BigDecimal total = BigDecimal.ZERO;
        long count = 0;

        for (StudentSemesterGpa record : records) {

            if (record.getSgpa() == null) {
                continue;
            }

            if (record.getSgpa().compareTo(BigDecimal.ZERO) < 0
                    || record.getSgpa().compareTo(
                    new BigDecimal("4.00")
            ) > 0) {
                continue;
            }

            total = total.add(record.getSgpa());
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

    private String calculateEligibilityStatus(
            StudentAcademicProfile profile,
            StudentEligibilityRecord record,
            Map<String, StudentResult> results
    ) {

        if (profile == null) {
            return "NOT_ELIGIBLE";
        }

        Integer semester =
                profile.getCurrentSemester();

        if (record == null) {
            return "CONDITIONALLY_ELIGIBLE";
        }

        boolean attendancePassed =
                record.getAttendancePercentage() != null
                        && record
                        .getAttendancePercentage()
                        .compareTo(MIN_ATTENDANCE) >= 0;

        boolean feePassed =
                Boolean.TRUE.equals(
                        record.getFeePaid()
                );

        boolean previousModulesPassed =
                checkPreviousModules(
                        profile,
                        semester,
                        results
                );

        if (attendancePassed
                && feePassed
                && previousModulesPassed) {

            return "ELIGIBLE";
        }

        if (!attendancePassed || !feePassed) {
            return "NOT_ELIGIBLE";
        }

        return "CONDITIONALLY_ELIGIBLE";
    }

    private boolean checkPreviousModules(
            StudentAcademicProfile profile,
            Integer currentSemester,
            Map<String, StudentResult> results
    ) {

        if (currentSemester == null
                || currentSemester <= 1) {
            return true;
        }

        return true;
    }

    private String buildAttentionReason(
            StudentAcademicProfile profile,
            StudentEligibilityRecord record,
            Map<String, StudentResult> results
    ) {

        List<String> reasons =
                new ArrayList<>();

        if (record == null) {

            reasons.add(
                    "Attendance and fee information is missing"
            );

        } else {

            if (record.getAttendancePercentage() == null) {

                reasons.add(
                        "Attendance information is missing"
                );

            } else if (
                    record.getAttendancePercentage()
                            .compareTo(MIN_ATTENDANCE) < 0
            ) {

                reasons.add(
                        "Attendance below 80%"
                );
            }

            if (!Boolean.TRUE.equals(
                    record.getFeePaid()
            )) {

                reasons.add(
                        "Semester fee not paid"
                );
            }
        }

        if (reasons.isEmpty()) {

            reasons.add(
                    "Academic eligibility requires review"
            );
        }

        return String.join(
                " • ",
                reasons
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
}