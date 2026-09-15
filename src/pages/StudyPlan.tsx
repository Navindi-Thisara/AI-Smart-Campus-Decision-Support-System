import { useState } from 'react'
import './StudyPlan.css'

const API_URL = 'http://127.0.0.1:8001'

interface LoggedInUser {
  id: number
  fullName: string
  email: string
  studentId: string
  role: 'STUDENT' | 'STAFF'
}

interface StudyPlanModule {
  course_code: string
  module_name: string
  credits: number
  module_type: string
  historical_grade_point: number | null
  performance_basis: string
  priority: number
  recommended_hours: number
}

interface StudyPlanResponse {
  student_id: string
  registration_no: string
  student_name: string
  degree_id: string
  current_year: number
  current_semester: number
  target_semester: number
  academic_risk: string
  current_sgpa: number | null
  previous_sgpa: number | null
  available_hours: number
  total_allocated_hours: number
  fitness: number
  study_plan: StudyPlanModule[]
}

function getLoggedInUser(): LoggedInUser | null {
  const storedUser = localStorage.getItem('user')

  if (!storedUser) {
    return null
  }

  try {
    const user: LoggedInUser = JSON.parse(storedUser)

    if (!user.studentId) {
      return null
    }

    return user
  } catch {
    return null
  }
}

function StudyPlan() {
  const [availableHours, setAvailableHours] =
    useState<number>(20)

  const [result, setResult] =
    useState<StudyPlanResponse | null>(null)

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState('')

  const generateStudyPlan = async () => {
    setLoading(true)
    setError('')
    setResult(null)

    try {

      const loggedInUser = getLoggedInUser()

      if (!loggedInUser) {
        throw new Error(
          'Unable to identify the logged-in student. Please log in again.'
        )
      }

      const response = await fetch(
        `${API_URL}/generate-study-plan`,
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },

          body: JSON.stringify({
            student_id: loggedInUser.studentId,
            available_hours: availableHours,
            random_seed: 42,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            'Failed to generate study plan.'
        )
      }

      setResult(data)
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError(
          'Unable to connect to the Study Plan API.'
        )
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="study-plan-page">

      {/* =====================================================
          PAGE HEADER
          ===================================================== */}

      <header className="study-plan-header">

        <div>

          <div className="study-plan-eyebrow">
            AI-POWERED ACADEMIC PLANNING
          </div>

          <h1>
            Personalized <span>Study Plan</span>
          </h1>

          <p>
            Generate an optimized weekly study schedule based on
            your academic performance, course priorities, academic
            risk, and available study time.
          </p>

        </div>

        <div className="study-plan-ai-badge">

          <span>AI</span>

          <div>
            <strong>
              Genetic Algorithm
            </strong>

            <small>
              Personalized Study Optimization
            </small>
          </div>

        </div>

      </header>


      {/* =====================================================
          MAIN GRID
          ===================================================== */}

      <section className="study-plan-grid">

        {/* ===================================================
            CONFIGURATION CARD
            =================================================== */}

        <div className="study-plan-card">

          <div className="study-plan-card-header">

            <div className="study-plan-step-number">
              01
            </div>

            <div>

              <h2>
                Study Plan Configuration
              </h2>

              <p>
                Define your available weekly study time.
              </p>

            </div>

          </div>


          <div className="study-plan-form">

            <div className="study-plan-field">

              <label htmlFor="available-hours">
                Available Study Hours Per Week
              </label>

              <input
                id="available-hours"
                type="number"
                min="1"
                max="168"
                value={availableHours}
                onChange={(event) => {
                  const value =
                    Number(event.target.value)

                  setAvailableHours(
                    Math.min(
                      168,
                      Math.max(1, value)
                    )
                  )
                }}
              />

              <small>
                Enter the number of hours you can dedicate
                to self-study each week.
              </small>

            </div>


            <button
              className="study-plan-submit"
              onClick={generateStudyPlan}
              disabled={loading}
            >

              <span>
                {loading
                  ? 'Optimizing Study Plan...'
                  : 'Generate Study Plan'}
              </span>

              <span>
                →
              </span>

            </button>

          </div>


          {error && (

            <div
              className="study-plan-error"
              role="alert"
            >

              <strong>
                Unable to generate study plan
              </strong>

              <span>
                {error}
              </span>

            </div>

          )}

        </div>


        {/* ===================================================
            RESULT PREVIEW / RESULT CARD
            =================================================== */}

        <div className="study-plan-card study-plan-result-panel">

          {!result ? (

            <div className="study-plan-empty">

              <div className="study-plan-empty-icon">
                AI
              </div>

              <h3>
                Your Study Plan
              </h3>

              <p>
                Generate your personalized study plan to see
                how the AI optimizer distributes your weekly
                study hours across upcoming modules.
              </p>

              <div className="study-plan-empty-line" />

              <span>
                Based on your academic performance
              </span>

            </div>

          ) : (

            <div className="study-plan-result">

              <div className="study-plan-card-header">

                <div className="study-plan-step-number study-plan-result-step">
                  02
                </div>

                <div>

                  <h2>
                    Optimization Result
                  </h2>

                  <p>
                    Personalized allocation for your
                    upcoming semester.
                  </p>

                </div>

              </div>


              <div className="study-plan-result-header">

                <div className="study-plan-result-title">

                  <strong>
                    {result.student_name}
                  </strong>

                  <p>
                    {result.registration_no}
                  </p>

                </div>

                <span className="study-plan-risk">
                  {result.academic_risk}
                </span>

              </div>


              <div className="study-plan-stat-grid">

                <div>

                  <span>
                    Current SGPA
                  </span>

                  <strong>
                    {result.current_sgpa !== null
                      ? result.current_sgpa.toFixed(4)
                      : 'N/A'}
                  </strong>

                </div>


                <div>

                  <span>
                    Target Semester
                  </span>

                  <strong>
                    Semester {result.target_semester}
                  </strong>

                </div>


                <div>

                  <span>
                    Available Hours
                  </span>

                  <strong>
                    {result.available_hours} hrs
                  </strong>

                </div>


                <div>

                  <span>
                    Allocated Hours
                  </span>

                  <strong className="positive">
                    {result.total_allocated_hours} hrs
                  </strong>

                </div>

              </div>


              <div className="study-plan-message">

                The Genetic Algorithm has generated a weekly
                allocation across {result.study_plan.length}
                {' '}
                target modules based on your academic
                profile and course priorities.

              </div>

            </div>

          )}

        </div>

      </section>


      {/* =====================================================
          GENERATED RESULTS
          ===================================================== */}

      {result && (

        <section className="study-plan-results">

          <div className="study-plan-results-header">

            <div>

              <h2>
                Your Personalized Plan
              </h2>

              <p>
                Optimized for your academic profile and
                upcoming semester.
              </p>

            </div>

          </div>


          {/* =================================================
              STUDENT SUMMARY
              ================================================= */}

          <div className="student-summary-card">

            <div className="student-summary-main">

              <div className="student-avatar">
                {result.student_name
                  .charAt(0)
                  .toUpperCase()}
              </div>

              <div>

                <span className="summary-label">
                  STUDENT
                </span>

                <h3>
                  {result.student_name}
                </h3>

                <p>
                  {result.registration_no}
                </p>

              </div>

            </div>


            <div className="summary-items">

              <div>

                <span>
                  CURRENT SGPA
                </span>

                <strong>
                  {result.current_sgpa !== null
                    ? result.current_sgpa.toFixed(4)
                    : 'N/A'}
                </strong>

              </div>


              <div>

                <span>
                  RISK LEVEL
                </span>

                <strong className="risk-value">
                  {result.academic_risk}
                </strong>

              </div>


              <div>

                <span>
                  TARGET SEMESTER
                </span>

                <strong>
                  Semester {result.target_semester}
                </strong>

              </div>


              <div>

                <span>
                  WEEKLY HOURS
                </span>

                <strong>
                  {result.total_allocated_hours} hrs
                </strong>

              </div>

            </div>

          </div>


          {/* =================================================
              OPTIMIZATION SUMMARY
              ================================================= */}

          <div className="optimization-summary">

            <div className="optimization-card">

              <span>
                AVAILABLE HOURS
              </span>

              <strong>
                {result.available_hours}
              </strong>

              <small>
                hours / week
              </small>

            </div>


            <div className="optimization-card">

              <span>
                ALLOCATED HOURS
              </span>

              <strong>
                {result.total_allocated_hours}
              </strong>

              <small>
                hours / week
              </small>

            </div>


            <div className="optimization-card">

              <span>
                MODULES
              </span>

              <strong>
                {result.study_plan.length}
              </strong>

              <small>
                target modules
              </small>

            </div>


            <div className="optimization-card">

              <span>
                GA FITNESS
              </span>

              <strong>
                {result.fitness.toFixed(4)}
              </strong>

              <small>
                optimization score
              </small>

            </div>

          </div>


          {/* =================================================
              COURSE PLAN
              ================================================= */}

          <div className="course-plan-card">

            <div className="course-plan-header">

              <div>

                <span className="summary-label">
                  OPTIMIZED ALLOCATION
                </span>

                <h3>
                  Weekly Study Distribution
                </h3>

                <p>
                  Recommended weekly hours by target module.
                </p>

              </div>


              <div className="hours-badge">
                {result.total_allocated_hours} hrs / week
              </div>

            </div>


            <div className="course-table-wrapper">

              <table className="course-table">

                <thead>

                  <tr>
                    <th>Course</th>
                    <th>Module</th>
                    <th>Credits</th>
                    <th>Performance</th>
                    <th>Priority</th>
                    <th>Study Hours</th>
                  </tr>

                </thead>


                <tbody>

                  {result.study_plan.map((module) => (

                    <tr key={module.course_code}>

                      <td>

                        <span className="course-code">
                          {module.course_code}
                        </span>

                      </td>


                      <td>

                        <div className="module-name">

                          {module.module_name}

                          <span>
                            {module.module_type}
                          </span>

                        </div>

                      </td>


                      <td>
                        {module.credits}
                      </td>


                      <td>

                        {module.historical_grade_point !== null ? (

                          <div className="performance-cell">

                            <strong>
                              {module.historical_grade_point.toFixed(2)}
                            </strong>

                            <span>
                              {module.performance_basis}
                            </span>

                          </div>

                        ) : (

                          <span className="not-available">
                            No history
                          </span>

                        )}

                      </td>


                      <td>

                        <span className="priority-value">
                          {module.priority.toFixed(3)}
                        </span>

                      </td>


                      <td>

                        <div className="hours-cell">

                          <strong>
                            {module.recommended_hours}
                          </strong>

                          <span>
                            hrs
                          </span>

                        </div>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          </div>


          {/* =================================================
              EXPLANATION
              ================================================= */}

          <div className="study-plan-explanation">

            <div className="explanation-icon">
              AI
            </div>

            <div>

              <strong>
                How your plan was personalized
              </strong>

              <p>
                The Genetic Algorithm considers historical
                course-family performance, academic risk,
                module credits, module type, and repeated
                courses when determining study priorities.
                Higher-priority modules receive greater
                consideration during optimization.
              </p>

            </div>

          </div>

        </section>

      )}

    </main>
  )
}

export default StudyPlan