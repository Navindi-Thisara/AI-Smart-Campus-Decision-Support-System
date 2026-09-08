package com.smartcampus.backend.controller;

import com.smartcampus.backend.entity.StudentSemesterGpa;
import com.smartcampus.backend.entity.User;
import com.smartcampus.backend.repository.StudentSemesterGpaRepository;
import com.smartcampus.backend.repository.UserRepository;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/sgpa")
@CrossOrigin(origins = "http://localhost:5173")
public class StudentSemesterGpaController {

    private final StudentSemesterGpaRepository gpaRepository;
    private final UserRepository userRepository;

    public StudentSemesterGpaController(
            StudentSemesterGpaRepository gpaRepository,
            UserRepository userRepository
    ) {
        this.gpaRepository = gpaRepository;
        this.userRepository = userRepository;
    }

    // =========================================================
    // GET ALL SAVED SEMESTER GPAs
    //
    // GET /api/sgpa/{userId}
    // =========================================================

    @GetMapping("/{userId}")
    public ResponseEntity<?> getStudentGpas(
            @PathVariable Long userId
    ) {

        // -----------------------------------------------------
        // FIND USER
        // -----------------------------------------------------

        User user =
                userRepository
                        .findById(userId)
                        .orElse(null);

        if (user == null) {
            return ResponseEntity.notFound().build();
        }

        // -----------------------------------------------------
        // GET GPA RECORDS
        // -----------------------------------------------------

        List<StudentSemesterGpa> records =
                gpaRepository
                        .findByUserOrderBySemesterAsc(user);

        // -----------------------------------------------------
        // BUILD RESPONSE
        // -----------------------------------------------------

        List<Map<String, Object>> response =
                records.stream()
                        .map(record -> {

                            Map<String, Object> item =
                                    new LinkedHashMap<>();

                            item.put(
                                    "id",
                                    record.getId()
                            );

                            item.put(
                                    "semester",
                                    record.getSemester()
                            );

                            item.put(
                                    "sgpa",
                                    record.getSgpa()
                            );

                            return item;
                        })
                        .toList();

        return ResponseEntity.ok(response);
    }


    // =========================================================
    // SAVE / UPDATE ONE SEMESTER GPA
    //
    // PUT /api/sgpa/{userId}/{semester}
    //
    // Example:
    //
    // PUT /api/sgpa/1/4
    //
    // Body:
    //
    // {
    //     "sgpa": 3.7500
    // }
    // =========================================================

    @PutMapping("/{userId}/{semester}")
    public ResponseEntity<?> saveSemesterGpa(
            @PathVariable Long userId,
            @PathVariable Integer semester,
            @RequestBody Map<String, Object> request
    ) {

        // =====================================================
        // VALIDATE SEMESTER
        // =====================================================

        if (semester == null ||
                semester < 1 ||
                semester > 8) {

            return ResponseEntity.badRequest()
                    .body(Map.of(
                            "message",
                            "Semester must be between 1 and 8."
                    ));
        }

        // =====================================================
        // FIND USER
        // =====================================================

        User user =
                userRepository
                        .findById(userId)
                        .orElse(null);

        if (user == null) {

            return ResponseEntity.notFound().build();
        }

        try {

            // =================================================
            // READ SGPA
            // =================================================

            Object sgpaValue =
                    request.get("sgpa");

            if (sgpaValue == null) {

                return ResponseEntity.badRequest()
                        .body(Map.of(
                                "message",
                                "SGPA is required."
                        ));
            }

            // =================================================
            // PARSE SGPA
            // =================================================

            BigDecimal sgpa =
                    new BigDecimal(
                            sgpaValue.toString().trim()
                    );

            // =================================================
            // VALIDATE SGPA
            // =================================================

            if (sgpa.compareTo(BigDecimal.ZERO) < 0 ||
                    sgpa.compareTo(
                            new BigDecimal("4.0000")
                    ) > 0) {

                return ResponseEntity.badRequest()
                        .body(Map.of(
                                "message",
                                "SGPA must be between 0.0000 and 4.0000."
                        ));
            }

            // =================================================
            // STORE EXACTLY 4 DECIMAL PLACES
            // =================================================

            sgpa =
                    sgpa.setScale(
                            4,
                            RoundingMode.HALF_UP
                    );

            // =================================================
            // FIND EXISTING RECORD
            //
            // One student can have only one GPA record for
            // each semester.
            // =================================================

            StudentSemesterGpa record =
                    gpaRepository
                            .findByUserAndSemester(
                                    user,
                                    semester
                            )
                            .orElseGet(() -> {

                                StudentSemesterGpa newRecord =
                                        new StudentSemesterGpa();

                                newRecord.setUser(user);
                                newRecord.setSemester(semester);

                                return newRecord;
                            });

            // =================================================
            // UPDATE SGPA
            // =================================================

            record.setSgpa(sgpa);

            // =================================================
            // SAVE
            // =================================================

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
                    .body(Map.of(
                            "message",
                            "Invalid SGPA value."
                    ));

        } catch (Exception exception) {

            exception.printStackTrace();

            return ResponseEntity.internalServerError()
                    .body(Map.of(
                            "message",
                            "Unable to save SGPA."
                    ));
        }
    }


    // =========================================================
    // DELETE ONE SEMESTER GPA
    //
    // DELETE /api/sgpa/{userId}/{semester}
    // =========================================================

    @DeleteMapping("/{userId}/{semester}")
    public ResponseEntity<?> deleteSemesterGpa(
            @PathVariable Long userId,
            @PathVariable Integer semester
    ) {

        // =====================================================
        // VALIDATE SEMESTER
        // =====================================================

        if (semester == null ||
                semester < 1 ||
                semester > 8) {

            return ResponseEntity.badRequest()
                    .body(Map.of(
                            "message",
                            "Semester must be between 1 and 8."
                    ));
        }

        // =====================================================
        // FIND USER
        // =====================================================

        User user =
                userRepository
                        .findById(userId)
                        .orElse(null);

        if (user == null) {

            return ResponseEntity.notFound().build();
        }

        // =====================================================
        // FIND AND DELETE GPA
        // =====================================================

        gpaRepository
                .findByUserAndSemester(
                        user,
                        semester
                )
                .ifPresent(
                        gpaRepository::delete
                );

        // =====================================================
        // RESPONSE
        // =====================================================

        return ResponseEntity.ok(
                Map.of(
                        "message",
                        "Semester GPA deleted successfully."
                )
        );
    }
}