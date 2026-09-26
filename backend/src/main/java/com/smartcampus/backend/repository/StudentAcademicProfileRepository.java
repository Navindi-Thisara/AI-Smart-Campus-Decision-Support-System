package com.smartcampus.backend.repository;

import com.smartcampus.backend.entity.StudentAcademicProfile;
import com.smartcampus.backend.entity.User;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface StudentAcademicProfileRepository
        extends JpaRepository<StudentAcademicProfile, Long> {

    Optional<StudentAcademicProfile> findByUser(User user);

    @EntityGraph(attributePaths = {"user"})
    List<StudentAcademicProfile> findAllByOrderByIdAsc();
}
