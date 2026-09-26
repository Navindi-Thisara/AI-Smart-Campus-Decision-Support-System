import { useEffect, useState } from 'react'

import './Prediction.css'

const API_URL = 'https://truthful-recreation-production-641e.up.railway.app'
const BACKEND_URL = import.meta.env.VITE_API_BASE_URL;

interface LoggedInUser {
  id: number
  fullName: string
  email: string
  studentId: string
  role: 'STUDENT' | 'STAFF'
}

interface PredictionForm {
  Previous_SGPA: string
  Current_SGPA: string
  Repeated_Courses: string
  Current_Year: string
  Current_Semester: string
}

interface SemesterRecord {
  semester: number
  sgpa: number
}

interface StudentProfile {
  currentYear: number
  currentSemester: number
}

interface StudentDashboardResponse {
  profile: StudentProfile
  semesterRecords: SemesterRecord[]
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

function Prediction() {
  const [form, setForm] = useState<PredictionForm>({
    Previous_SGPA: '',
    Current_SGPA: '',
    Repeated_Courses: '',
    Current_Year: '',
    Current_Semester: '',
  })

  const [prediction, setPrediction] = useState<number | null>(null)

  const [loading, setLoading] = useState(false)

  const [error, setError] = useState('')

  const [loadingStudentData, setLoadingStudentData] =
    useState(true)

  useEffect(() => {
    const loadStudentData = async () => {
      setLoadingStudentData(true)
      setError('')

      try {
        const loggedInUser = getLoggedInUser()

        if (!loggedInUser) {
          throw new Error(
            'Unable to identify the logged-in student. Please log in again.'
          )
        }

        const response = await fetch(
          `${BACKEND_URL}/api/students/dashboard?studentId=${encodeURIComponent(
            loggedInUser.studentId
          )}`
        )

        const data: StudentDashboardResponse & {
          detail?: string
          message?: string
        } = await response.json()

        if (!response.ok) {
          throw new Error(
            data.detail ||
              data.message ||
              'Failed to load student data.'
          )
        }

        console.log('Student data:', data)

        const records = data.semesterRecords || []

        if (records.length === 0) {
          throw new Error(
            'No saved SGPA records found for this student.'
          )
        }

        if (!data.profile) {
          throw new Error(
            'Student academic profile could not be loaded.'
          )
        }

        const sortedRecords = [...records].sort(
          (a, b) => a.semester - b.semester
        )

        const latest =
          sortedRecords[sortedRecords.length - 1]

        const previous =
          sortedRecords.length > 1
            ? sortedRecords[sortedRecords.length - 2]
            : null

        setForm((previousForm) => ({
          ...previousForm,

          Previous_SGPA: previous
            ? Number(previous.sgpa).toFixed(4)
            : Number(latest.sgpa).toFixed(4),

          Current_SGPA: Number(latest.sgpa).toFixed(4),

          Current_Year: String(
            data.profile.currentYear
          ),

          Current_Semester: String(
            data.profile.currentSemester
          ),

          Repeated_Courses: '0',
        }))
      } catch (err) {
        console.error(
          'Failed to load student data:',
          err
        )

        setError(
          err instanceof Error
            ? err.message
            : 'Unable to load student data.'
        )
      } finally {
        setLoadingStudentData(false)
      }
    }

    loadStudentData()
  }, [])

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target

    setForm((previousForm) => ({
      ...previousForm,
      [name]: value,
    }))
  }

  const handleSGPAChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const { name, value } = e.target

    if (value === '') {
      setForm((previousForm) => ({
        ...previousForm,
        [name]: '',
      }))

      return
    }

    const sgpaPattern =
      /^\d{0,1}(\.\d{0,4})?$/

    if (!sgpaPattern.test(value)) {
      return
    }

    const numericValue = Number(value)

    if (numericValue > 4) {
      return
    }

    setForm((previousForm) => ({
      ...previousForm,
      [name]: value,
    }))
  }

  const predictSGPA = async (
    e: React.FormEvent
  ) => {
    e.preventDefault()

    setPrediction(null)
    setError('')

    if (loadingStudentData) {
      setError(
        'Student academic information is still loading. Please wait.'
      )

      return
    }

    const previousSGPA = Number(
      form.Previous_SGPA
    )

    const currentSGPA = Number(
      form.Current_SGPA
    )

    const repeatedCourses = Number(
      form.Repeated_Courses
    )

    const currentYear = Number(
      form.Current_Year
    )

    const currentSemester = Number(
      form.Current_Semester
    )

    if (
      Number.isNaN(previousSGPA) ||
      Number.isNaN(currentSGPA) ||
      Number.isNaN(repeatedCourses) ||
      Number.isNaN(currentYear) ||
      Number.isNaN(currentSemester)
    ) {
      setError(
        'Please provide valid academic information.'
      )

      return
    }

    if (
      previousSGPA < 0 ||
      previousSGPA > 4 ||
      currentSGPA < 0 ||
      currentSGPA > 4
    ) {
      setError(
        'SGPA values must be between 0.0000 and 4.0000.'
      )

      return
    }

    if (repeatedCourses < 0) {
      setError(
        'Repeated courses cannot be negative.'
      )

      return
    }

    if (
      currentYear < 1 ||
      currentYear > 4
    ) {
      setError(
        'Academic year must be between Year 1 and Year 4.'
      )

      return
    }

    if (
      currentSemester < 1 ||
      currentSemester > 8
    ) {
      setError(
        'Semester must be between Semester 1 and Semester 8.'
      )

      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        `${API_URL}/predict-next-sgpa`,
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json',
            Accept: 'application/json',
          },

          body: JSON.stringify({
            Previous_SGPA: previousSGPA,
            Current_SGPA: currentSGPA,
            Repeated_Courses: repeatedCourses,
            Current_Year: currentYear,
            Current_Semester: currentSemester,
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : typeof data.message === 'string'
              ? data.message
              : 'Prediction failed.'
        )
      }

      const predictedSGPA = Number(
        data.Predicted_Next_SGPA
      )

      if (Number.isNaN(predictedSGPA)) {
        throw new Error(
          'The prediction service returned an invalid SGPA value.'
        )
      }

      /*
       * Keep the prediction within the valid SGPA range.
       */
      const safePrediction = Math.min(
        4,
        Math.max(0, predictedSGPA)
      )

      setPrediction(safePrediction)
    } catch (err) {
      console.error(
        'Prediction failed:',
        err
      )

      setError(
        err instanceof Error
          ? err.message
          : 'Unable to connect to the prediction service.'
      )
    } finally {
      setLoading(false)
    }
  }

  /*
   * =========================================================
   * PERFORMANCE LEVEL
   * =========================================================
   */
  const getPerformanceLevel = (
    gpa: number
  ) => {
    if (gpa >= 3.5) {
      return 'Excellent'
    }

    if (gpa >= 3.0) {
      return 'Good'
    }

    if (gpa >= 2.0) {
      return 'Satisfactory'
    }

    return 'Needs Improvement'
  }

  return (
    <main className="prediction-page">

      <section className="prediction-header">

        <div>

          <span className="prediction-eyebrow">
            AI PERFORMANCE ANALYTICS
          </span>

          <h1>
            Neural Network
            <span> Prediction</span>
          </h1>

          <p>
            Estimate your next semester SGPA using
            academic performance data and our trained
            neural network model.
          </p>

        </div>

        <div className="prediction-ai-badge">

          <span>AI</span>

          <div>

            <strong>
              Neural Network
            </strong>

            <small>
              Prediction Engine
            </small>

          </div>

        </div>

      </section>

      <section className="prediction-grid">

        <div className="prediction-card">

          <div className="prediction-card-header">

            <div className="step-number">
              01
            </div>

            <div>

              <h2>
                Academic Information
              </h2>

              <p>
                Enter your current academic details.
              </p>

            </div>

          </div>


          <form onSubmit={predictSGPA}>

            <div className="prediction-form-grid">

              <div className="prediction-field">

                <label htmlFor="Previous_SGPA">
                  Previous SGPA
                </label>

                <input
                  id="Previous_SGPA"
                  name="Previous_SGPA"
                  type="text"
                  inputMode="decimal"
                  placeholder="3.2000"
                  value={form.Previous_SGPA}
                  onChange={handleSGPAChange}
                  disabled={loadingStudentData}
                  required
                />

                <small>
                  Range: 0.0000 – 4.0000
                </small>

              </div>

              <div className="prediction-field">

                <label htmlFor="Current_SGPA">
                  Current SGPA
                </label>

                <input
                  id="Current_SGPA"
                  name="Current_SGPA"
                  type="text"
                  inputMode="decimal"
                  placeholder="3.4500"
                  value={form.Current_SGPA}
                  onChange={handleSGPAChange}
                  disabled={loadingStudentData}
                  required
                />

                <small>
                  Range: 0.0000 – 4.0000
                </small>

              </div>

              <div className="prediction-field">

                <label htmlFor="Repeated_Courses">
                  Repeated Courses
                </label>

                <input
                  id="Repeated_Courses"
                  name="Repeated_Courses"
                  type="number"
                  min="0"
                  step="1"
                  value={form.Repeated_Courses}
                  onChange={handleChange}
                  disabled={loadingStudentData}
                  required
                />

                <small>
                  Number of repeated courses
                </small>

              </div>

              <div className="prediction-field">

                <label htmlFor="Current_Year">
                  Academic Year
                </label>

                <select
                  id="Current_Year"
                  name="Current_Year"
                  value={form.Current_Year}
                  onChange={handleChange}
                  disabled={loadingStudentData}
                  required
                >

                  <option value="">
                    Select Year
                  </option>

                  <option value="1">
                    Year 1
                  </option>

                  <option value="2">
                    Year 2
                  </option>

                  <option value="3">
                    Year 3
                  </option>

                  <option value="4">
                    Year 4
                  </option>

                </select>

              </div>

              <div className="prediction-field">

                <label htmlFor="Current_Semester">
                  Current Semester
                </label>

                <select
                  id="Current_Semester"
                  name="Current_Semester"
                  value={form.Current_Semester}
                  onChange={handleChange}
                  disabled={loadingStudentData}
                  required
                >

                  <option value="">
                    Select Semester
                  </option>

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

              </div>

            </div>


            <button
              type="submit"
              className="prediction-submit"
              disabled={
                loading ||
                loadingStudentData
              }
            >

              {loadingStudentData
                ? 'Loading Academic Data...'
                : loading
                  ? 'Running Prediction...'
                  : 'Predict Next Semester SGPA'}

              {!loading &&
                !loadingStudentData && (
                  <span>→</span>
                )}

            </button>

          </form>

          {error && (

            <div
              className="prediction-error"
              role="alert"
            >

              <strong>
                Prediction unavailable
              </strong>

              <span>
                {error}
              </span>

            </div>

          )}

        </div>

        <div className="prediction-card result-panel">

          <div className="prediction-card-header">

            <div className="step-number result-step">
              02
            </div>

            <div>

              <h2>
                Prediction Result
              </h2>

              <p>
                AI-generated academic forecast.
              </p>

            </div>

          </div>


          {prediction === null ? (

            <div className="prediction-empty">

              <div className="prediction-empty-icon">
                ✦
              </div>

              <h3>
                Ready for prediction
              </h3>

              <p>
                Enter your academic information and
                run the neural network to generate
                your estimated next semester SGPA.
              </p>

              <div className="prediction-empty-line" />

              <span>
                Powered by your trained AI model
              </span>

            </div>

          ) : (

            <div className="prediction-result">

              <span className="result-label">
                Predicted Next Semester SGPA
              </span>

              <div className="gpa-number">
                {prediction.toFixed(4)}
              </div>

              <div className="performance-level">
                {getPerformanceLevel(
                  prediction
                )}
              </div>


              <div className="result-stat-grid">

                <div>

                  <span>
                    Current SGPA
                  </span>

                  <strong>
                    {Number(
                      form.Current_SGPA
                    ).toFixed(4)}
                  </strong>

                </div>


                <div>

                  <span>
                    Predicted Change
                  </span>

                  <strong
                    className={
                      prediction >=
                      Number(
                        form.Current_SGPA
                      )
                        ? 'positive'
                        : 'negative'
                    }
                  >

                    {prediction >=
                    Number(
                      form.Current_SGPA
                    )
                      ? '+'
                      : ''}

                    {(
                      prediction -
                      Number(
                        form.Current_SGPA
                      )
                    ).toFixed(4)}

                  </strong>

                </div>

              </div>


              <div className="prediction-message">

                {prediction >= 3.5
                  ? 'Excellent predicted performance. Continue maintaining your current academic habits.'
                  : prediction >= 3
                    ? 'Good predicted performance. Focus on consistency and continued improvement.'
                    : prediction >= 2
                      ? 'Satisfactory predicted performance. Additional study effort may improve your next semester.'
                      : 'Additional academic support and focused study may be beneficial.'}

              </div>

            </div>

          )}

        </div>

      </section>

      <section className="model-information">

        <div className="model-information-main">

          <div className="model-ai-icon">
            NN
          </div>

          <div>

            <strong>
              Neural Network Prediction Engine
            </strong>

            <p>
              This prediction is generated using
              the trained Smart Campus academic
              performance model.
            </p>

          </div>

        </div>


        <div className="model-features">

          <span>
            Previous SGPA
          </span>

          <span>
            Current SGPA
          </span>

          <span>
            Repeated Courses
          </span>

          <span>
            Academic Year
          </span>

          <span>
            Semester
          </span>

        </div>

      </section>

    </main>
  )
}

export default Prediction

