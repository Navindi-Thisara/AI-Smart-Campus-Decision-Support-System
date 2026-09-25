import { useEffect, useState } from 'react'

import './Eligibility.css'

const BACKEND_URL = 'http://localhost:8080'

interface LoggedInUser {
  studentId?: string
  registrationNo?: string
  name?: string
  role?: string
}

interface StudentDashboardResponse {
  currentSemester?: number

  studentProfile?: {
    currentSemester?: number
  }

  profile?: {
    currentSemester?: number
  }

  academicProfile?: {
    currentSemester?: number
  }

  [key: string]: unknown
}

interface EligibilityResponse {
  studentId: string
  semester: number
  status:
    | 'ELIGIBLE'
    | 'NOT_ELIGIBLE'
    | 'CONDITIONALLY_ELIGIBLE'
  eligible: boolean
  explanations: string[]
}

type RuleStatus =
  | 'passed'
  | 'failed'
  | 'warning'
  | 'pending'

function Eligibility() {
  const [studentId, setStudentId] = useState('')

  /*
   * Semester sent to the eligibility backend.
   *
   * It is automatically initialized from the student's
   * actual current semester stored in the database.
   */
  const [semester, setSemester] = useState('')

  const [currentSemester, setCurrentSemester] =
    useState<number | null>(null)

  const [result, setResult] =
    useState<EligibilityResponse | null>(null)

  const [loading, setLoading] = useState(false)

  const [loadingUser, setLoadingUser] = useState(true)

  const [error, setError] = useState('')

  // ============================================================
  // GET CURRENT SEMESTER FROM BACKEND
  // ============================================================

  const loadStudentInformation = async (
    loggedStudentId: string
  ) => {
    try {
      /*
       * Load the student's actual current semester
       * from the backend database.
       *
       * Example:
       *
       * Current Semester = 2
       *
       * The eligibility page will therefore evaluate
       * Semester 2.
       *
       * This allows the semester sent to the eligibility
       * service to match the student's database record.
       */
      const response = await fetch(
        `${BACKEND_URL}/api/students/dashboard?studentId=${encodeURIComponent(
          loggedStudentId
        )}`
      )

      if (!response.ok) {
        throw new Error(
          'Unable to load the student academic information.'
        )
      }

      const data: StudentDashboardResponse =
        await response.json()

      /*
       * Support the possible locations of currentSemester
       * in the dashboard response.
       *
       * The first valid semester value is used.
       */
      const possibleCurrentSemesters = [
        data.currentSemester,
        data.studentProfile?.currentSemester,
        data.profile?.currentSemester,
        data.academicProfile?.currentSemester,
      ]

      const foundCurrentSemester =
        possibleCurrentSemesters.find(
          (value) =>
            typeof value === 'number' &&
            Number.isInteger(value) &&
            value >= 1 &&
            value <= 8
        )

      if (
        typeof foundCurrentSemester !== 'number'
      ) {
        throw new Error(
          'Current semester is not available for the logged-in student.'
        )
      }

      setCurrentSemester(foundCurrentSemester)

      /*
       * IMPORTANT:
       *
       * Evaluate the student's CURRENT semester.
       *
       * Do NOT add +1 here.
       *
       * Example:
       *
       * Current Semester = 2
       * Eligibility Record = Semester 2
       * Attendance = 85%
       * Fee Paid = true
       *
       * Result → ELIGIBLE
       */
      setSemester(String(foundCurrentSemester))
    } catch (err) {
      console.error(
        'Failed to load student information:',
        err
      )

      throw err
    }
  }

  // ============================================================
  // LOAD LOGGED-IN USER
  // ============================================================

  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedUser =
          localStorage.getItem('user')

        if (!storedUser) {
          setError(
            'No logged-in student was found. Please log in again.'
          )
          return
        }

        const user: LoggedInUser =
          JSON.parse(storedUser)

        if (!user.studentId) {
          setError(
            'Student ID is not available for the logged-in user.'
          )
          return
        }

        setStudentId(user.studentId)

        /*
         * Do not use localStorage.currentSemester.
         *
         * Load the actual current semester from the
         * student dashboard backend.
         */
        await loadStudentInformation(
          user.studentId
        )
      } catch (err) {
        console.error(
          'Failed to load logged-in student:',
          err
        )

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load the logged-in student information.'
        )
      } finally {
        setLoadingUser(false)
      }
    }

    loadUser()
  }, [])

  // ============================================================
  // CHECK ELIGIBILITY
  // ============================================================

  const checkEligibility = async (
    e: React.FormEvent
  ) => {
    e.preventDefault()

    if (!studentId) {
      setError(
        'Student ID is not available. Please log in again.'
      )
      return
    }

    if (!semester) {
      setError(
        'Student semester information is not available.'
      )
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(
        `${BACKEND_URL}/api/eligibility?studentId=${encodeURIComponent(
          studentId
        )}&semester=${semester}`
      )

      let data: EligibilityResponse & {
        message?: string
        error?: string
      }

      try {
        data = await response.json()
      } catch {
        throw new Error(
          'The eligibility service returned an invalid response.'
        )
      }

      if (!response.ok) {
        throw new Error(
          data.message ||
            data.error ||
            'Eligibility check failed.'
        )
      }

      setResult(data)
    } catch (err) {
      console.error(
        'Eligibility check failed:',
        err
      )

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to connect to the eligibility service.'
      )
    } finally {
      setLoading(false)
    }
  }

  // ============================================================
  // FINAL ELIGIBILITY STATUS
  // ============================================================

  const getStatusTitle = () => {
    if (!result) return ''

    switch (result.status) {
      case 'ELIGIBLE':
        return 'Eligible'

      case 'NOT_ELIGIBLE':
        return 'Not Eligible'

      case 'CONDITIONALLY_ELIGIBLE':
        return 'Conditionally Eligible'

      default:
        return 'Unknown Status'
    }
  }

  const getStatusDescription = () => {
    if (!result) return ''

    switch (result.status) {
      case 'ELIGIBLE':
        return 'You have satisfied all evaluated academic eligibility requirements.'

      case 'NOT_ELIGIBLE':
        return 'One or more mandatory eligibility requirements have not been satisfied.'

      case 'CONDITIONALLY_ELIGIBLE':
        return 'Some requirements are satisfied, but additional academic information or requirements remain incomplete.'

      default:
        return ''
    }
  }

  const getStatusClass = () => {
    if (!result) return ''

    switch (result.status) {
      case 'ELIGIBLE':
        return 'eligible'

      case 'NOT_ELIGIBLE':
        return 'not-eligible'

      case 'CONDITIONALLY_ELIGIBLE':
        return 'conditional'

      default:
        return ''
    }
  }

  // ============================================================
  // RULE STATUS
  // ============================================================

  const getRuleStatus = (
    rule:
      | 'profile'
      | 'attendance'
      | 'fee'
      | 'modules'
  ): RuleStatus => {
    if (!result) return 'pending'

    const explanations =
      result.explanations.map(
        (item) => item.toLowerCase()
      )

    switch (rule) {
      // --------------------------------------------------------
      // RULE 01 - ACADEMIC PROFILE
      // --------------------------------------------------------

      case 'profile':
        if (
          explanations.some((item) =>
            item.includes(
              'academic profile exists'
            )
          )
        ) {
          return 'passed'
        }

        if (
          explanations.some((item) =>
            item.includes(
              'academic profile not found'
            )
          )
        ) {
          return 'failed'
        }

        return 'pending'

      // --------------------------------------------------------
      // RULE 02 - ATTENDANCE
      // --------------------------------------------------------

      case 'attendance':
        if (
          explanations.some((item) =>
            item.includes(
              'attendance requirement satisfied'
            )
          )
        ) {
          return 'passed'
        }

        if (
          explanations.some((item) =>
            item.includes(
              'attendance requirement not satisfied'
            )
          )
        ) {
          return 'failed'
        }

        if (
          explanations.some((item) =>
            item.includes(
              'attendance information is not available'
            )
          )
        ) {
          return 'pending'
        }

        return 'pending'

      // --------------------------------------------------------
      // RULE 03 - FEE PAYMENT
      // --------------------------------------------------------

      case 'fee':
        if (
          explanations.some((item) =>
            item.includes(
              'semester fee payment requirement satisfied'
            )
          )
        ) {
          return 'passed'
        }

        if (
          explanations.some((item) =>
            item.includes(
              'semester fee has not been paid'
            )
          )
        ) {
          return 'failed'
        }

        if (
          explanations.some((item) =>
            item.includes(
              'semester fee payment information is not available'
            )
          )
        ) {
          return 'pending'
        }

        return 'pending'

      // --------------------------------------------------------
      // RULE 04 - PREVIOUS REQUIRED MODULES
      // --------------------------------------------------------

      case 'modules':
        if (
          explanations.some((item) =>
            item.includes(
              'all required modules from previous semesters'
            )
          )
        ) {
          return 'passed'
        }

        if (
          explanations.some((item) =>
            item.includes(
              'no previous required modules exist'
            )
          )
        ) {
          return 'passed'
        }

        if (
          explanations.some((item) =>
            item.includes(
              'previous required module not completed'
            )
          ) ||
          explanations.some((item) =>
            item.includes(
              'previous required module not passed'
            )
          )
        ) {
          return 'failed'
        }

        return 'pending'

      default:
        return 'pending'
    }
  }

  // ============================================================
  // RULE STATUS LABEL
  // ============================================================

  const getRuleStatusLabel = (
    status: RuleStatus
  ) => {
    switch (status) {
      case 'passed':
        return 'Satisfied'

      case 'failed':
        return 'Not Satisfied'

      case 'warning':
        return 'Incomplete'

      case 'pending':
        return 'Not Evaluated'

      default:
        return 'Not Evaluated'
    }
  }

  // ============================================================
  // RULE STATUS ICON
  // ============================================================

  const getRuleStatusIcon = (
    status: RuleStatus
  ) => {
    switch (status) {
      case 'passed':
        return '✓'

      case 'failed':
        return '!'

      case 'warning':
        return '!'

      case 'pending':
        return '•'

      default:
        return '•'
    }
  }

  // ============================================================
  // EXPLANATION STATUS
  // ============================================================

  const getExplanationStatus = (
    explanation: string
  ): 'passed' | 'warning' | 'pending' => {
    const lowerExplanation =
      explanation.toLowerCase()

    // ----------------------------------------------------------
    // POSITIVE EXPLANATIONS
    // ----------------------------------------------------------

    const passed =
      lowerExplanation.includes(
        'attendance requirement satisfied'
      ) ||
      lowerExplanation.includes(
        'semester fee payment requirement satisfied'
      ) ||
      lowerExplanation.includes(
        'successfully completed'
      ) ||
      lowerExplanation.includes(
        'academic profile exists'
      )

    if (passed) {
      return 'passed'
    }

    // ----------------------------------------------------------
    // FAILED / INCOMPLETE EXPLANATIONS
    // ----------------------------------------------------------

    const warning =
      lowerExplanation.includes(
        'not completed'
      ) ||
      lowerExplanation.includes(
        'not passed'
      ) ||
      lowerExplanation.includes(
        'not satisfied'
      ) ||
      lowerExplanation.includes(
        'has not been paid'
      ) ||
      lowerExplanation.includes(
        'not found'
      )

    if (warning) {
      return 'warning'
    }

    // ----------------------------------------------------------
    // MISSING INFORMATION
    // ----------------------------------------------------------

    const pending =
      lowerExplanation.includes(
        'not available'
      ) ||
      lowerExplanation.includes(
        'not evaluated'
      ) ||
      lowerExplanation.includes(
        'missing'
      ) ||
      lowerExplanation.includes(
        'no previous required modules'
      )

    if (pending) {
      return 'pending'
    }

    return 'pending'
  }

  return (
    <main className="eligibility-page">

      {/* ======================================================
          HEADER
          ====================================================== */}

      <section className="eligibility-header">

        <div>

          <span className="eligibility-eyebrow">
            RULE-BASED EXPERT SYSTEM
          </span>

          <h1>
            Academic
            <span> Eligibility</span>
          </h1>

          <p>
            Evaluate your academic eligibility using
            predefined university rules for attendance,
            fee payment, academic records, and previous
            required modules.
          </p>

        </div>

        <div className="eligibility-ai-badge">

          <span>ES</span>

          <div>

            <strong>
              Expert System
            </strong>

            <small>
              Academic Eligibility Engine
            </small>

          </div>

        </div>

      </section>


      {/* ======================================================
          MAIN GRID
          ====================================================== */}

      <section className="eligibility-grid">

        {/* ====================================================
            ELIGIBILITY CHECK
            ==================================================== */}

        <div className="eligibility-card">

          <div className="eligibility-card-header">

            <div className="eligibility-step-number">
              01
            </div>

            <div>

              <h2>
                Eligibility Check
              </h2>

              <p>
                Select the semester you want to evaluate.
              </p>

            </div>

          </div>

          <form onSubmit={checkEligibility}>

            <div className="eligibility-form">

              {/* STUDENT ID */}

              <div className="eligibility-field">

                <label htmlFor="studentId">
                  Student ID
                </label>

                <input
                  id="studentId"
                  type="text"
                  value={
                    loadingUser
                      ? 'Loading...'
                      : studentId
                  }
                  disabled
                  readOnly
                />

                <small>
                  Currently logged-in student
                </small>

              </div>


              {/* SEMESTER */}

              <div className="eligibility-field">

                <label htmlFor="semester">
                  Semester
                </label>

                <select
                  id="semester"
                  value={semester}
                  onChange={(e) =>
                    setSemester(
                      e.target.value
                    )
                  }
                  disabled={
                    loadingUser ||
                    loading
                  }
                >

                  {Array.from(
                    { length: 8 },
                    (_, index) => (
                      <option
                        key={index + 1}
                        value={String(index + 1)}
                      >
                        Semester {index + 1}
                      </option>
                    )
                  )}

                </select>

                <small>
                  Automatically selected from your current semester
                </small>

              </div>

            </div>


            {/* CURRENT / ELIGIBILITY SEMESTER INFORMATION */}

            {currentSemester !== null && (
              <div
                style={{
                  marginTop: '10px',
                  fontSize: '13px',
                  opacity: 0.7,
                }}
              >
                Current Semester: {currentSemester}
                {' • '}
                Eligibility Semester: {semester}
              </div>
            )}


            {/* SUBMIT BUTTON */}

            <button
              type="submit"
              className="eligibility-submit"
              disabled={
                loading ||
                loadingUser ||
                !studentId ||
                !semester
              }
            >

              {loading
                ? 'Checking Eligibility...'
                : 'Check Academic Eligibility'}

              {!loading && (
                <span>
                  →
                </span>
              )}

            </button>

          </form>


          {/* ERROR */}

          {error && (
            <div className="eligibility-error">

              <strong>
                Eligibility check unavailable
              </strong>

              <span>
                {error}
              </span>

            </div>
          )}

        </div>


        {/* ====================================================
            RESULT PANEL
            ==================================================== */}

        <div className="eligibility-card result-panel">

          <div className="eligibility-card-header">

            <div className="eligibility-step-number result-step">
              02
            </div>

            <div>

              <h2>
                Eligibility Result
              </h2>

              <p>
                Rule-based academic decision.
              </p>

            </div>

          </div>


          {!result ? (

            /* ==================================================
               EMPTY RESULT
               ================================================== */

            <div className="eligibility-empty">

              <div className="eligibility-empty-icon">
                ✓
              </div>

              <h3>
                Ready for evaluation
              </h3>

              <p>
                Select a semester and run the expert
                system to evaluate your academic
                eligibility.
              </p>

              <div className="eligibility-empty-line" />

              <span>
                Powered by predefined academic rules
              </span>

            </div>

          ) : (

            /* ==================================================
               RESULT
               ================================================== */

            <div className="eligibility-result">

              {/* STATUS */}

              <div
                className={`eligibility-status ${getStatusClass()}`}
              >

                <div className="eligibility-status-icon">

                  {result.status === 'ELIGIBLE'
                    ? '✓'
                    : '!'}

                </div>

                <div>

                  <span>
                    Academic Status
                  </span>

                  <strong>
                    {getStatusTitle()}
                  </strong>

                </div>

              </div>


              {/* DESCRIPTION */}

              <p className="eligibility-description">
                {getStatusDescription()}
              </p>


              {/* SUMMARY */}

              <div className="eligibility-summary">

                <div>

                  <span>
                    Student ID
                  </span>

                  <strong>
                    {result.studentId}
                  </strong>

                </div>

                <div>

                  <span>
                    Semester
                  </span>

                  <strong>
                    {result.semester}
                  </strong>

                </div>

                <div>

                  <span>
                    Decision
                  </span>

                  <strong>
                    {result.eligible
                      ? 'Approved'
                      : 'Review Required'}
                  </strong>

                </div>

              </div>


              {/* =================================================
                  EVALUATION DETAILS
                  ================================================= */}

              <div className="eligibility-explanations">

                <div className="evaluation-heading">

                  <div>

                    <h3>
                      Evaluation Details
                    </h3>

                    <p>
                      Each academic rule is evaluated
                      independently.
                    </p>

                  </div>

                  <span className="evaluation-engine">
                    RULE ENGINE
                  </span>

                </div>


                {/* =================================================
                    RULE GRID
                    ================================================= */}

                <div className="eligibility-rule-grid">

                  {/* RULE 01 */}

                  <div
                    className={`eligibility-rule-card rule-${getRuleStatus(
                      'profile'
                    )}`}
                  >

                    <div className="rule-card-icon">

                      {getRuleStatusIcon(
                        getRuleStatus('profile')
                      )}

                    </div>

                    <div className="rule-card-content">

                      <span className="rule-card-label">
                        RULE 01
                      </span>

                      <strong>
                        Academic Profile
                      </strong>

                      <p>
                        Student academic profile
                        must exist.
                      </p>

                    </div>

                    <span className="rule-card-status">

                      {getRuleStatusLabel(
                        getRuleStatus('profile')
                      )}

                    </span>

                  </div>


                  {/* RULE 02 */}

                  <div
                    className={`eligibility-rule-card rule-${getRuleStatus(
                      'attendance'
                    )}`}
                  >

                    <div className="rule-card-icon">

                      {getRuleStatusIcon(
                        getRuleStatus('attendance')
                      )}

                    </div>

                    <div className="rule-card-content">

                      <span className="rule-card-label">
                        RULE 02
                      </span>

                      <strong>
                        Attendance Requirement
                      </strong>

                      <p>
                        Minimum attendance must
                        be 80%.
                      </p>

                    </div>

                    <span className="rule-card-status">

                      {getRuleStatusLabel(
                        getRuleStatus('attendance')
                      )}

                    </span>

                  </div>


                  {/* RULE 03 */}

                  <div
                    className={`eligibility-rule-card rule-${getRuleStatus(
                      'fee'
                    )}`}
                  >

                    <div className="rule-card-icon">

                      {getRuleStatusIcon(
                        getRuleStatus('fee')
                      )}

                    </div>

                    <div className="rule-card-content">

                      <span className="rule-card-label">
                        RULE 03
                      </span>

                      <strong>
                        Semester Fee Payment
                      </strong>

                      <p>
                        Required semester fee
                        must be paid.
                      </p>

                    </div>

                    <span className="rule-card-status">

                      {getRuleStatusLabel(
                        getRuleStatus('fee')
                      )}

                    </span>

                  </div>


                  {/* RULE 04 */}

                  <div
                    className={`eligibility-rule-card rule-${getRuleStatus(
                      'modules'
                    )}`}
                  >

                    <div className="rule-card-icon">

                      {getRuleStatusIcon(
                        getRuleStatus('modules')
                      )}

                    </div>

                    <div className="rule-card-content">

                      <span className="rule-card-label">
                        RULE 04
                      </span>

                      <strong>
                        Previous Required Modules
                      </strong>

                      <p>
                        Previous required modules
                        must be successfully
                        completed.
                      </p>

                    </div>

                    <span className="rule-card-status">

                      {getRuleStatusLabel(
                        getRuleStatus('modules')
                      )}

                    </span>

                  </div>

                </div>


                {/* =================================================
                    DECISION EXPLANATION
                    ================================================= */}

                <div className="eligibility-explanation-details">

                  <div className="explanation-details-header">

                    <span>
                      Decision Explanation
                    </span>

                    <small>
                      {result.explanations.length}{' '}
                      rule evaluation
                      {result.explanations.length !==
                      1
                        ? 's'
                        : ''}
                    </small>

                  </div>


                  <div className="eligibility-rules">

                    {result.explanations.map(
                      (
                        explanation,
                        index
                      ) => {

                        const explanationStatus =
                          getExplanationStatus(
                            explanation
                          )

                        return (
                          <div
                            key={index}
                            className={`eligibility-rule ${
                              explanationStatus ===
                              'passed'
                                ? 'rule-passed'
                                : explanationStatus ===
                                    'warning'
                                  ? 'rule-warning'
                                  : ''
                            }`}
                          >

                            <span className="rule-icon">

                              {explanationStatus ===
                              'passed'
                                ? '✓'
                                : explanationStatus ===
                                    'warning'
                                  ? '!'
                                  : '•'}

                            </span>

                            <span>
                              {explanation}
                            </span>

                          </div>
                        )
                      }
                    )}

                  </div>

                </div>

              </div>

            </div>

          )}

        </div>

      </section>


      {/* ========================================================
          INFORMATION SECTION
          ======================================================== */}

      <section className="eligibility-information">

        <div className="eligibility-information-main">

          <div className="eligibility-engine-icon">
            ES
          </div>

          <div>

            <strong>
              Academic Eligibility Expert System
            </strong>

            <p>
              The system evaluates predefined academic
              rules and provides an eligibility decision
              together with an explanation of each rule.
            </p>

          </div>

        </div>


        <div className="eligibility-features">

          <span>
            Attendance ≥ 80%
          </span>

          <span>
            Fee Payment
          </span>

          <span>
            Academic Profile
          </span>

          <span>
            Previous Modules
          </span>

          <span>
            Explainable Decision
          </span>

        </div>

      </section>

    </main>
  )
}

export default Eligibility
