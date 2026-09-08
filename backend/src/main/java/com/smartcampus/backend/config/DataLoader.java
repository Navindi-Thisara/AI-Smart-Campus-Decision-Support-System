package com.smartcampus.backend.config;

import com.smartcampus.backend.entity.CourseModule;
import com.smartcampus.backend.entity.Degree;
import com.smartcampus.backend.entity.DegreeModule;
import com.smartcampus.backend.entity.Faculty;
import com.smartcampus.backend.repository.CourseModuleRepository;
import com.smartcampus.backend.repository.DegreeModuleRepository;
import com.smartcampus.backend.repository.DegreeRepository;
import com.smartcampus.backend.repository.FacultyRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

@Component
public class DataLoader implements CommandLineRunner {

    private final FacultyRepository facultyRepository;
    private final DegreeRepository degreeRepository;
    private final CourseModuleRepository courseModuleRepository;
    private final DegreeModuleRepository degreeModuleRepository;

    public DataLoader(
            FacultyRepository facultyRepository,
            DegreeRepository degreeRepository,
            CourseModuleRepository courseModuleRepository,
            DegreeModuleRepository degreeModuleRepository
    ) {
        this.facultyRepository = facultyRepository;
        this.degreeRepository = degreeRepository;
        this.courseModuleRepository = courseModuleRepository;
        this.degreeModuleRepository = degreeModuleRepository;
    }

    @Override
    public void run(String... args) {
        try {
            loadFaculties();
            loadDegrees();
            loadCourseModules();
            loadDegreeModules();

            System.out.println("==========================================");
            System.out.println("CSV DATA LOADING COMPLETED");
            System.out.println("Faculties      : " + facultyRepository.count());
            System.out.println("Degrees        : " + degreeRepository.count());
            System.out.println("Course Modules : " + courseModuleRepository.count());
            System.out.println("Degree Modules : " + degreeModuleRepository.count());
            System.out.println("==========================================");

        } catch (Exception e) {
            System.err.println("==========================================");
            System.err.println("CSV DATA LOADING FAILED");
            System.err.println(e.getMessage());
            System.err.println("==========================================");

            throw new RuntimeException(
                    "Failed to load CSV data",
                    e
            );
        }
    }

    private void loadFaculties() throws IOException {

        Path path = Path.of("../data/faculties.csv");

        if (!Files.exists(path)) {
            throw new IOException(
                    "File not found: " + path.toAbsolutePath()
            );
        }

        try (BufferedReader reader = Files.newBufferedReader(path)) {

            String line;

            // Skip header
            reader.readLine();

            while ((line = reader.readLine()) != null) {

                if (line.isBlank()) {
                    continue;
                }

                String[] values = line.split(",", -1);

                if (values.length < 2) {
                    continue;
                }

                String facultyId = values[0].trim();
                String facultyName = values[1].trim();

                if (!facultyRepository.existsById(facultyId)) {

                    Faculty faculty = new Faculty(
                            facultyId,
                            facultyName
                    );

                    facultyRepository.save(faculty);
                }
            }
        }

        System.out.println("Faculties loaded successfully.");
    }

    private void loadDegrees() throws IOException {

        Path path = Path.of("../data/degrees.csv");

        if (!Files.exists(path)) {
            throw new IOException(
                    "File not found: " + path.toAbsolutePath()
            );
        }

        try (BufferedReader reader = Files.newBufferedReader(path)) {

            String line;

            // Skip header
            reader.readLine();

            while ((line = reader.readLine()) != null) {

                if (line.isBlank()) {
                    continue;
                }

                String[] values = line.split(",", -1);

                if (values.length < 5) {
                    continue;
                }

                String degreeId = values[0].trim();
                String degreeName = values[1].trim();
                String facultyId = values[2].trim();
                String department = values[3].trim();

                Integer durationYears = Integer.parseInt(
                        values[4].trim()
                );

                if (!degreeRepository.existsById(degreeId)) {

                    Degree degree = new Degree(
                            degreeId,
                            degreeName,
                            facultyId,
                            department,
                            durationYears
                    );

                    degreeRepository.save(degree);
                }
            }
        }

        System.out.println("Degrees loaded successfully.");
    }

    private void loadCourseModules() throws IOException {

        Path path = Path.of("../data/course_modules.csv");

        if (!Files.exists(path)) {
            throw new IOException(
                    "File not found: " + path.toAbsolutePath()
            );
        }

        try (BufferedReader reader = Files.newBufferedReader(path)) {

            String line;

            // Skip header
            reader.readLine();

            while ((line = reader.readLine()) != null) {

                if (line.isBlank()) {
                    continue;
                }

                String[] values = line.split(",", -1);

                if (values.length < 6) {
                    continue;
                }

                String courseCode = values[0].trim();
                String moduleName = values[1].trim();

                Integer year = Integer.parseInt(
                        values[2].trim()
                );

                Integer semester = Integer.parseInt(
                        values[3].trim()
                );

                Integer credits = Integer.parseInt(
                        values[4].trim()
                );

                String moduleCategory = values[5].trim();

                if (!courseModuleRepository.existsById(courseCode)) {

                    CourseModule courseModule = new CourseModule(
                            courseCode,
                            moduleName,
                            year,
                            semester,
                            credits,
                            moduleCategory
                    );

                    courseModuleRepository.save(courseModule);
                }
            }
        }

        System.out.println("Course modules loaded successfully.");
    }

    private void loadDegreeModules() throws IOException {

        Path path = Path.of("../data/degree_modules.csv");

        if (!Files.exists(path)) {
            throw new IOException(
                    "File not found: " + path.toAbsolutePath()
            );
        }

        try (BufferedReader reader = Files.newBufferedReader(path)) {

            String line;

            // Skip header
            reader.readLine();

            while ((line = reader.readLine()) != null) {

                if (line.isBlank()) {
                    continue;
                }

                String[] values = line.split(",", -1);

                if (values.length < 4) {
                    continue;
                }

                String degreeModuleId = values[0].trim();
                String degreeId = values[1].trim();
                String courseCode = values[2].trim();
                String moduleType = values[3].trim();

                if (!degreeModuleRepository.existsById(
                        degreeModuleId
                )) {

                    DegreeModule degreeModule = new DegreeModule(
                            degreeModuleId,
                            degreeId,
                            courseCode,
                            moduleType
                    );

                    degreeModuleRepository.save(degreeModule);
                }
            }
        }

        System.out.println("Degree modules loaded successfully.");
    }
}