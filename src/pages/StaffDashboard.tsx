import { useEffect, useMemo, useState } from 'react'
import './StaffDashboard.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

interface SemesterPerformance {
  semester: number
  averageSgpa: number | null
}

interface AttentionStudent {
  studentId: string
  fullName: string
  currentSemester: number | null
  currentSgpa: number | null
  attendancePercentage: number | null
  eligibilityStatus: string | null
  attentionReason: string | null
}

interface StaffDashboardData {
  totalStudents: number
  eligibleStudents: number
  conditionallyEligibleStudents: number
  notEligibleStudents: number
  overallAverageSgpa: number | null
  semesterPerformance: SemesterPerformance[]
  studentsRequiringAttention: AttentionStudent[]
}

function StaffDashboard() {
  const [dashboard, setDashboard] =
    useState<StaffDashboardData | null>(null)

  const [loading, setLoading] =
    useState<boolean>(true)

  const [error, setError] =
    useState<string>('')

  const [showAllAttention, setShowAllAttention] =
    useState<boolean>(false)

  /*
   * Staff eligibility update form
   */
  const [studentId, setStudentId] =
    useState<string>('')

  const [semester, setSemester] =
    useState<string>('')

  const [attendancePercentage, setAttendancePercentage] =
    useState<string>('')

  const [feePaid, setFeePaid] =
    useState<boolean>(false)

  const [updatingEligibility, setUpdatingEligibility] =
    useState<boolean>(false)

  const [updateMessage, setUpdateMessage] =
    useState<string>('')

  const [updateError, setUpdateError] =
    useState<string>('')

  const loadDashboard = async (): Promise<void> => {
    try {
      setLoading(true)
      setError('')

      const response = await fetch(
        `${API_BASE_URL}/api/staff/dashboard`
      )

      if (!response.ok) {
        throw new Error(
          `Failed to load dashboard (${response.status})`
        )
      }

      const data: StaffDashboardData =
        await response.json()

      setDashboard(data)
      setShowAllAttention(false)
    } catch (err) {
      console.error(
        'Staff dashboard error:',
        err
      )

      setError(
        'Unable to load dashboard data. Please make sure the backend is running.'
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadDashboard()
  }, [])

  /*
   * Update student eligibility information
   */
  const handleUpdateEligibility = async (
    event: React.FormEvent<HTMLFormElement>
  ): Promise<void> => {
    event.preventDefault()

    setUpdateMessage('')
    setUpdateError('')

    if (!studentId.trim()) {
      setUpdateError(
        'Student ID is required.'
      )
      return
    }

    const semesterNumber =
      Number(semester)

    if (
      !semester ||
      Number.isNaN(semesterNumber) ||
      semesterNumber < 1
    ) {
      setUpdateError(
        'Please enter a valid semester.'
      )
      return
    }

    const attendanceNumber =
      Number(attendancePercentage)

    if (
      attendancePercentage === '' ||
      Number.isNaN(attendanceNumber) ||
      attendanceNumber < 0 ||
      attendanceNumber > 100
    ) {
      setUpdateError(
        'Attendance must be between 0 and 100.'
      )
      return
    }

    try {
      setUpdatingEligibility(true)

      const response = await fetch(
        `${API_BASE_URL}/api/staff/eligibility`,
        {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            studentId: studentId.trim(),
            semester: semesterNumber,
            attendancePercentage: attendanceNumber,
            feePaid
          })
        }
      )

      if (!response.ok) {
        let errorMessage =
          'Failed to update eligibility information.'

        try {
          const errorText =
            await response.text()

          if (errorText) {
            errorMessage = errorText
          }
        } catch {
          // Keep default error message.
        }

        throw new Error(errorMessage)
      }

      setUpdateMessage(
        'Eligibility information updated successfully.'
      )

      /*
       * Clear the form after successful update.
       */
      setStudentId('')
      setSemester('')
      setAttendancePercentage('')
      setFeePaid(false)

      /*
       * Reload dashboard so all statistics and
       * eligibility information are updated.
       */
      await loadDashboard()
    } catch (err) {
      console.error(
        'Eligibility update error:',
        err
      )

      setUpdateError(
        err instanceof Error
          ? err.message
          : 'Unable to update eligibility information.'
      )
    } finally {
      setUpdatingEligibility(false)
    }
  }

  const totalStudents =
    dashboard?.totalStudents ?? 0

  const eligibleStudents =
    dashboard?.eligibleStudents ?? 0

  const conditionalStudents =
    dashboard?.conditionallyEligibleStudents ?? 0

  const notEligibleStudents =
    dashboard?.notEligibleStudents ?? 0

  const eligiblePercentage = useMemo(() => {
    if (!totalStudents) return 0

    return Math.round(
      (eligibleStudents / totalStudents) * 100
    )
  }, [
    eligibleStudents,
    totalStudents
  ])

  const conditionalPercentage = useMemo(() => {
    if (!totalStudents) return 0

    return Math.round(
      (conditionalStudents / totalStudents) * 100
    )
  }, [
    conditionalStudents,
    totalStudents
  ])

  const notEligiblePercentage = useMemo(() => {
    if (!totalStudents) return 0

    return Math.round(
      (notEligibleStudents / totalStudents) * 100
    )
  }, [
    notEligibleStudents,
    totalStudents
  ])

  const semesterData =
    dashboard?.semesterPerformance ?? []

  const attentionStudents =
    dashboard?.studentsRequiringAttention ?? []

  const visibleAttentionStudents =
    showAllAttention
      ? attentionStudents
      : attentionStudents.slice(0, 5)

  const maxSgpa = 4

  const getInitials = (
    name: string | null | undefined
  ): string => {
    if (!name) return 'ST'

    return name
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((part) =>
        part.charAt(0)
      )
      .join('')
      .toUpperCase()
  }

  const formatSgpa = (
    value:
      | number
      | string
      | null
      | undefined
  ): string => {
    if (
      value === null ||
      value === undefined
    ) {
      return '—'
    }

    const numericValue =
      Number(value)

    if (Number.isNaN(numericValue)) {
      return '—'
    }

    return numericValue.toFixed(2)
  }

  const getStatusLabel = (
    status:
      | string
      | null
      | undefined
  ): string => {
    switch (status) {
      case 'ELIGIBLE':
        return 'Eligible'

      case 'CONDITIONALLY_ELIGIBLE':
        return 'Conditional'

      case 'NOT_ELIGIBLE':
        return 'Not eligible'

      default:
        return status || 'Review'
    }
  }

  const getStatusClass = (
    status:
      | string
      | null
      | undefined
  ): string => {
    switch (status) {
      case 'ELIGIBLE':
        return 'eligible'

      case 'CONDITIONALLY_ELIGIBLE':
        return 'conditional'

      case 'NOT_ELIGIBLE':
        return 'not-eligible'

      default:
        return 'conditional'
    }
  }

  const handleViewAllAttention = (): void => {
    setShowAllAttention(
      (previous) => !previous
    )
  }

  if (loading) {
    return (
      <main className="staff-dashboard">
        <section className="staff-loading">

          <div className="staff-spinner" />

          <h2>
            Loading academic overview
          </h2>

          <p>
            Fetching the latest information from the
            campus database.
          </p>

        </section>
      </main>
    )
  }

  if (error) {
    return (
      <main className="staff-dashboard">

        <section className="staff-error">

          <div className="staff-error-icon">
            !
          </div>

          <div>

            <h2>
              Dashboard unavailable
            </h2>

            <p>
              {error}
            </p>

            <button
              type="button"
              className="staff-retry-button"
              onClick={loadDashboard}
            >
              Try again
            </button>

          </div>

        </section>

      </main>
    )
  }

  return (
    <main className="staff-dashboard">

      {/* =====================================================
          HEADER
      ====================================================== */}

      <section className="staff-dashboard-header">

        <div className="staff-header-copy">

          <span className="staff-page-label">
            STAFF DASHBOARD
          </span>

          <h1>
            Academic intelligence overview
          </h1>

          <p>
            Monitor student performance and academic
            eligibility across the campus.
          </p>

        </div>

        <div className="staff-header-actions">

          <div className="staff-live-status">

            <span className="staff-live-dot" />

            <span>
              Database connected
            </span>

          </div>

          <button
            type="button"
            className="staff-refresh-button"
            onClick={loadDashboard}
            aria-label="Refresh dashboard"
          >

            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
            >

              <path
                d="M20 11a8.1 8.1 0 0 0-14.9-4L3 10"
              />

              <path d="M3 4v6h6" />

              <path
                d="M4 13a8.1 8.1 0 0 0 14.9 4L21 14"
              />

              <path d="M21 20v-6h-6" />

            </svg>

            Refresh

          </button>

        </div>

      </section>


      {/* =====================================================
          STATISTICS
      ====================================================== */}

      <section className="staff-stat-grid">

        <article className="staff-stat-card">

          <div className="staff-stat-top">

            <span>
              Total students
            </span>

            <div className="staff-stat-icon blue">

              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >

                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />

                <circle
                  cx="9"
                  cy="7"
                  r="4"
                />

                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />

                <path d="M16 3.13a4 4 0 0 1 0 7.75" />

              </svg>

            </div>

          </div>

          <strong className="staff-stat-value">
            {totalStudents.toLocaleString()}
          </strong>

          <span className="staff-stat-meta">
            Registered student profiles
          </span>

        </article>


        <article className="staff-stat-card">

          <div className="staff-stat-top">

            <span>
              Eligible
            </span>

            <div className="staff-stat-icon green">

              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >

                <path d="m5 12 4 4L19 6" />

              </svg>

            </div>

          </div>

          <strong className="staff-stat-value">
            {eligibleStudents.toLocaleString()}
          </strong>

          <span className="staff-stat-meta positive">
            {eligiblePercentage}% of students
          </span>

        </article>


        <article className="staff-stat-card">

          <div className="staff-stat-top">

            <span>
              Conditional
            </span>

            <div className="staff-stat-icon amber">

              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >

                <path d="M12 9v4" />

                <path d="M12 17h.01" />

                <path d="M10.3 3.7 2.7 17a2 2 0 0 0 1.75 3h15.1a2 2 0 0 0 1.75-3L13.7 3.7a2 2 0 0 0-3.4 0Z" />

              </svg>

            </div>

          </div>

          <strong className="staff-stat-value">
            {conditionalStudents.toLocaleString()}
          </strong>

          <span className="staff-stat-meta warning">
            {conditionalPercentage}% require review
          </span>

        </article>


        <article className="staff-stat-card">

          <div className="staff-stat-top">

            <span>
              Not eligible
            </span>

            <div className="staff-stat-icon red">

              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.8"
              >

                <circle
                  cx="12"
                  cy="12"
                  r="9"
                />

                <path d="m9 9 6 6" />

                <path d="m15 9-6 6" />

              </svg>

            </div>

          </div>

          <strong className="staff-stat-value">
            {notEligibleStudents.toLocaleString()}
          </strong>

          <span className="staff-stat-meta danger">
            {notEligiblePercentage}% need attention
          </span>

        </article>

      </section>


      {/* =====================================================
          STAFF ELIGIBILITY UPDATE
      ====================================================== */}

      <section className="staff-panel staff-update-panel">

        <div className="staff-panel-header">

          <div>

            <span className="staff-section-label">
              STUDENT DATA MANAGEMENT
            </span>

            <h2>
              Update eligibility information
            </h2>

            <p>
              Update attendance and fee payment details
              for a student's academic record.
            </p>

          </div>

        </div>


        <form
          className="staff-update-form"
          onSubmit={handleUpdateEligibility}
        >

          <div className="staff-form-group">

            <label htmlFor="studentId">
              Student ID
            </label>

            <input
              id="studentId"
              type="text"
              value={studentId}
              onChange={(event) =>
                setStudentId(
                  event.target.value
                )
              }
              placeholder="e.g. KDU/COE/25/0001"
              disabled={updatingEligibility}
            />

          </div>


          <div className="staff-form-group">

            <label htmlFor="semester">
              Semester
            </label>

            <input
              id="semester"
              type="number"
              min="1"
              max="8"
              value={semester}
              onChange={(event) =>
                setSemester(
                  event.target.value
                )
              }
              placeholder="e.g. 4"
              disabled={updatingEligibility}
            />

          </div>


          <div className="staff-form-group">

            <label htmlFor="attendance">
              Attendance (%)
            </label>

            <input
              id="attendance"
              type="number"
              min="0"
              max="100"
              step="0.01"
              value={attendancePercentage}
              onChange={(event) =>
                setAttendancePercentage(
                  event.target.value
                )
              }
              placeholder="e.g. 85"
              disabled={updatingEligibility}
            />

          </div>


          <div className="staff-form-group staff-fee-group">

            <label>
              Fee payment
            </label>

            <label className="staff-checkbox-label">

              <input
                type="checkbox"
                checked={feePaid}
                onChange={(event) =>
                  setFeePaid(
                    event.target.checked
                  )
                }
                disabled={
                  updatingEligibility
                }
              />

              <span>
                Fee paid
              </span>

            </label>

          </div>


          <button
            type="submit"
            className="staff-update-button"
            disabled={updatingEligibility}
          >

            {updatingEligibility ? (
              <>
                <span className="staff-button-spinner" />
                Updating...
              </>
            ) : (
              <>
                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >
                  <path d="M5 12h14" />
                  <path d="M12 5v14" />
                </svg>

                Update eligibility
              </>
            )}

          </button>

        </form>


        {updateMessage && (
          <div className="staff-update-success">
            <span>✓</span>
            {updateMessage}
          </div>
        )}


        {updateError && (
          <div className="staff-update-error">
            <span>!</span>
            {updateError}
          </div>
        )}

      </section>


      {/* =====================================================
          PERFORMANCE + ELIGIBILITY
      ====================================================== */}

      <section className="staff-main-grid">

        <article className="staff-panel staff-performance-panel">

          <div className="staff-panel-header">

            <div>

              <span className="staff-section-label">
                PERFORMANCE
              </span>

              <h2>
                Student performance
              </h2>

              <p>
                Average SGPA across recorded semesters
              </p>

            </div>

            <div className="staff-average-box">

              <span>
                Overall average
              </span>

              <strong>
                {formatSgpa(
                  dashboard?.overallAverageSgpa
                )}
              </strong>

              <small>
                / 4.00
              </small>

            </div>

          </div>


          <div className="staff-chart">

            <div className="staff-chart-y">

              <span>4.0</span>
              <span>3.0</span>
              <span>2.0</span>
              <span>1.0</span>
              <span>0</span>

            </div>


            <div className="staff-chart-content">

              <div className="staff-grid-lines">

                <span />
                <span />
                <span />
                <span />
                <span />

              </div>


              <div className="staff-chart-bars">

                {semesterData.length === 0 ? (

                  <div className="staff-chart-empty">
                    No semester SGPA data available.
                  </div>

                ) : (

                  semesterData.map(
                    (
                      item: SemesterPerformance
                    ) => {

                      const sgpa =
                        Number(
                          item.averageSgpa
                        ) || 0

                      const height =
                        Math.min(
                          100,
                          Math.max(
                            0,
                            (sgpa / maxSgpa) * 100
                          )
                        )

                      return (
                        <div
                          className="staff-chart-column"
                          key={item.semester}
                        >

                          <div className="staff-bar-value">
                            {sgpa.toFixed(2)}
                          </div>

                          <div className="staff-bar-track">

                            <div
                              className="staff-chart-bar"
                              style={{
                                height:
                                  `${height}%`
                              }}
                            />

                          </div>

                          <label>
                            Sem {item.semester}
                          </label>

                        </div>
                      )
                    }
                  )

                )}

              </div>

            </div>

          </div>

        </article>


        <article className="staff-panel staff-eligibility-panel">

          <div className="staff-panel-header">

            <div>

              <span className="staff-section-label">
                ELIGIBILITY
              </span>

              <h2>
                Academic status
              </h2>

              <p>
                Current student eligibility distribution
              </p>

            </div>

          </div>


          <div className="staff-donut-wrapper">

            <div
              className="staff-donut"
              style={{
                '--eligible':
                  `${eligiblePercentage}%`,
                '--conditional':
                  `${conditionalPercentage}%`,
                '--noteligible':
                  `${notEligiblePercentage}%`
              } as React.CSSProperties}
            >

              <div className="staff-donut-center">

                <strong>
                  {eligiblePercentage}%
                </strong>

                <span>
                  Eligible
                </span>

              </div>

            </div>

          </div>


          <div className="staff-status-list">

            <div className="staff-status-row">

              <div className="staff-status-name">

                <span className="status-dot eligible" />

                <span>
                  Eligible
                </span>

              </div>

              <strong>
                {eligibleStudents.toLocaleString()}
              </strong>

            </div>


            <div className="staff-status-row">

              <div className="staff-status-name">

                <span className="status-dot conditional" />

                <span>
                  Conditional
                </span>

              </div>

              <strong>
                {conditionalStudents.toLocaleString()}
              </strong>

            </div>


            <div className="staff-status-row">

              <div className="staff-status-name">

                <span className="status-dot not-eligible" />

                <span>
                  Not eligible
                </span>

              </div>

              <strong>
                {notEligibleStudents.toLocaleString()}
              </strong>

            </div>

          </div>

        </article>

      </section>


      {/* =====================================================
          ATTENTION + SUMMARY
      ====================================================== */}

      <section className="staff-bottom-grid">

        <article className="staff-panel staff-attention-panel">

          <div className="staff-panel-header">

            <div>

              <span className="staff-section-label">
                ATTENTION REQUIRED
              </span>

              <h2>
                Students requiring attention
              </h2>

              <p>
                Students whose current academic eligibility
                requires review
              </p>

            </div>

            {attentionStudents.length > 5 && (

              <button
                type="button"
                className="staff-panel-action"
                onClick={
                  handleViewAllAttention
                }
                aria-expanded={
                  showAllAttention
                }
              >

                {showAllAttention
                  ? 'Show less'
                  : 'View all'}

                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  style={{
                    transform:
                      showAllAttention
                        ? 'rotate(-90deg)'
                        : 'rotate(0deg)',
                    transition:
                      'transform 0.2s ease'
                  }}
                >

                  <path d="M5 12h14" />

                  <path d="m13 6 6 6-6 6" />

                </svg>

              </button>

            )}

          </div>


          {attentionStudents.length === 0 ? (

            <div className="staff-empty-state">

              <div className="staff-empty-icon">

                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >

                  <path d="m5 12 4 4L19 6" />

                </svg>

              </div>

              <strong>
                No students currently require attention
              </strong>

              <span>
                All available eligibility records are
                currently satisfied.
              </span>

            </div>

          ) : (

            <div className="staff-student-list">

              {visibleAttentionStudents.map(
                (
                  student: AttentionStudent
                ) => (

                  <div
                    className="staff-student-row"
                    key={student.studentId}
                  >

                    <div className="staff-student-avatar">

                      {getInitials(
                        student.fullName
                      )}

                    </div>


                    <div className="staff-student-info">

                      <strong>
                        {student.fullName}
                      </strong>

                      <span>
                        {student.studentId}
                      </span>

                    </div>


                    <div className="staff-student-academic">

                      <span>
                        Sem {
                          student.currentSemester ??
                          '—'
                        }
                      </span>

                      <strong>
                        {formatSgpa(
                          student.currentSgpa
                        )}
                      </strong>

                    </div>


                    <div className="staff-student-attendance">

                      <span>
                        Attendance
                      </span>

                      <strong
                        className={
                          student.attendancePercentage !==
                            null &&
                          student.attendancePercentage !==
                            undefined &&
                          Number(
                            student.attendancePercentage
                          ) < 80
                            ? 'attendance-low'
                            : ''
                        }
                      >

                        {student.attendancePercentage !==
                          null &&
                        student.attendancePercentage !==
                          undefined
                          ? `${Number(
                              student.attendancePercentage
                            ).toFixed(1)}%`
                          : '—'}

                      </strong>

                    </div>


                    <span
                      className={`staff-status-badge ${getStatusClass(
                        student.eligibilityStatus
                      )}`}
                    >

                      {getStatusLabel(
                        student.eligibilityStatus
                      )}

                    </span>


                    <div
                      className="staff-attention-reason"
                      title={
                        student.attentionReason ??
                        ''
                      }
                    >

                      {student.attentionReason ||
                        'Requires academic review'}

                    </div>

                  </div>

                )
              )}

            </div>

          )}

        </article>


        <article className="staff-panel staff-summary-panel">

          <div className="staff-panel-header">

            <div>

              <span className="staff-section-label">
                SYSTEM SUMMARY
              </span>

              <h2>
                Academic overview
              </h2>

              <p>
                Current database statistics
              </p>

            </div>

          </div>


          <div className="staff-summary-list">

            <div className="staff-summary-item">

              <div className="staff-summary-icon blue">

                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >

                  <path d="M4 19V5" />

                  <path d="M4 19h16" />

                  <path d="m7 15 3-4 3 2 5-7" />

                </svg>

              </div>

              <div>

                <strong>
                  SGPA tracking
                </strong>

                <span>
                  {semesterData.length} semester
                  {semesterData.length === 1
                    ? ''
                    : 's'} recorded
                </span>

              </div>

            </div>


            <div className="staff-summary-item">

              <div className="staff-summary-icon green">

                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >

                  <path d="m5 12 4 4L19 6" />

                </svg>

              </div>

              <div>

                <strong>
                  Eligibility
                </strong>

                <span>
                  {eligiblePercentage}%
                  currently eligible
                </span>

              </div>

            </div>


            <div className="staff-summary-item">

              <div className="staff-summary-icon amber">

                <svg
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                >

                  <path d="M12 9v4" />

                  <path d="M12 17h.01" />

                  <path d="M10.3 3.7 2.7 17a2 2 0 0 0 1.75 3h15.1a2 2 0 0 0 1.75-3L13.7 3.7a2 2 0 0 0-3.4 0Z" />

                </svg>

              </div>

              <div>

                <strong>
                  Requires review
                </strong>

                <span>
                  {(
                    conditionalStudents +
                    notEligibleStudents
                  ).toLocaleString()}{' '}
                  students
                </span>

              </div>

            </div>

          </div>


          <div className="staff-summary-footer">

            <span>
              Data source
            </span>

            <strong>
              Smart Campus database
            </strong>

          </div>

        </article>

      </section>

    </main>
  )
}

export default StaffDashboard
