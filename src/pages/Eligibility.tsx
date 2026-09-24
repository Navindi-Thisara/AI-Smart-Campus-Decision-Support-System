import { useEffect, useState } from 'react'

import './Eligibility.css'

const BACKEND_URL = 'http://localhost:8080'

interface LoggedInUser {
  studentId?: string
  registrationNo?: string
  name?: string
  role?: string
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

function Eligibility() {
  const [studentId, setStudentId] = useState('')

  const [semester, setSemester] = useState('2')

  const [result, setResult] =
    useState<EligibilityResponse | null>(null)

  const [loading, setLoading] = useState(false)

  const [loadingUser, setLoadingUser] = useState(true)

  const [error, setError] = useState('')

  useEffect(() => {
    try {
      const storedUser = localStorage.getItem('user')

      if (!storedUser) {
        setError(
          'No logged-in student was found. Please log in again.'
        )
        return
      }

      const user: LoggedInUser = JSON.parse(storedUser)

      if (!user.studentId) {
        setError(
          'Student ID is not available for the logged-in user.'
        )
        return
      }

      setStudentId(user.studentId)
    } catch (err) {
      console.error(
        'Failed to load logged-in user:',
        err
      )

      setError(
        'Unable to load the logged-in student information.'
      )
    } finally {
      setLoadingUser(false)
    }
  }, [])

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
        return 'Some requirements are satisfied, but additional academic requirements remain incomplete.'

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

  const getRuleStatus = (
    rule:
      | 'profile'
      | 'attendance'
      | 'fee'
      | 'modules'
  ) => {
    if (!result) return 'pending'

    const explanations = result.explanations.map(
      (item) => item.toLowerCase()
    )

    switch (rule) {
      case 'profile':
        return explanations.some((item) =>
          item.includes('academic profile exists')
        )
          ? 'passed'
          : 'failed'

      case 'attendance':
        return explanations.some((item) =>
          item.includes(
            'attendance requirement satisfied'
          )
        )
          ? 'passed'
          : 'failed'

      case 'fee':
        return explanations.some((item) =>
          item.includes(
            'semester fee payment requirement satisfied'
          )
        )
          ? 'passed'
          : 'failed'

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
              'previous required module'
            )
          )
        ) {
          return 'warning'
        }

        return 'pending'

      default:
        return 'pending'
    }
  }

  return (
    <main className="eligibility-page">

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

      <section className="eligibility-grid">

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
                    setSemester(e.target.value)
                  }
                  disabled={loadingUser || loading}
                >

                  {Array.from(
                    { length: 8 },
                    (_, index) => (
                      <option
                        key={index + 1}
                        value={index + 1}
                      >
                        Semester {index + 1}
                      </option>
                    )
                  )}

                </select>

                <small>
                  Academic semester to evaluate
                </small>

              </div>

            </div>

            {/* SUBMIT BUTTON */}

            <button
              type="submit"
              className="eligibility-submit"
              disabled={
                loading ||
                loadingUser ||
                !studentId
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

            <div className="eligibility-result">

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

              <p className="eligibility-description">
                {getStatusDescription()}
              </p>

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

                <div className="eligibility-rule-grid">

                  {/* RULE 01 - PROFILE */}

                  <div
                    className={`eligibility-rule-card rule-${getRuleStatus(
                      'profile'
                    )}`}
                  >

                    <div className="rule-card-icon">

                      {getRuleStatus('profile') ===
                      'passed'
                        ? '✓'
                        : '!'}

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

                      {getRuleStatus('profile') ===
                      'passed'
                        ? 'Satisfied'
                        : 'Failed'}

                    </span>

                  </div>

                  {/* RULE 02 - ATTENDANCE */}

                  <div
                    className={`eligibility-rule-card rule-${getRuleStatus(
                      'attendance'
                    )}`}
                  >

                    <div className="rule-card-icon">

                      {getRuleStatus('attendance') ===
                      'passed'
                        ? '✓'
                        : '!'}

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

                      {getRuleStatus('attendance') ===
                      'passed'
                        ? 'Satisfied'
                        : 'Not Satisfied'}

                    </span>

                  </div>

                  {/* RULE 03 - FEE */}

                  <div
                    className={`eligibility-rule-card rule-${getRuleStatus(
                      'fee'
                    )}`}
                  >

                    <div className="rule-card-icon">

                      {getRuleStatus('fee') ===
                      'passed'
                        ? '✓'
                        : '!'}

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

                      {getRuleStatus('fee') ===
                      'passed'
                        ? 'Satisfied'
                        : 'Not Satisfied'}

                    </span>

                  </div>

                  {/* RULE 04 - PREVIOUS MODULES */}

                  <div
                    className={`eligibility-rule-card rule-${getRuleStatus(
                      'modules'
                    )}`}
                  >

                    <div className="rule-card-icon">

                      {getRuleStatus('modules') ===
                      'passed'
                        ? '✓'
                        : '!'}

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

                      {getRuleStatus('modules') ===
                      'passed'
                        ? 'Satisfied'
                        : getRuleStatus('modules') ===
                            'warning'
                          ? 'Incomplete'
                          : 'Not Evaluated'}

                    </span>

                  </div>

                </div>

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
                      (explanation, index) => {

                        const lowerExplanation =
                          explanation.toLowerCase()

                        const passed =
                          lowerExplanation.includes(
                            'satisfied'
                          ) ||
                          lowerExplanation.includes(
                            'successfully completed'
                          ) ||
                          lowerExplanation.includes(
                            'exists'
                          )

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
                            'missing'
                          )

                        return (
                          <div
                            key={index}
                            className={`eligibility-rule ${
                              passed
                                ? 'rule-passed'
                                : warning
                                  ? 'rule-warning'
                                  : ''
                            }`}
                          >

                            <span className="rule-icon">

                              {passed
                                ? '✓'
                                : warning
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