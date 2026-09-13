import { useEffect, useState } from 'react'
import './Prediction.css'

const API_URL = 'http://127.0.0.1:8000'

const BACKEND_URL = 'http://localhost:8080'
const STUDENT_ID = 'KDU/BSE/25/0001'

interface PredictionForm {
  Previous_SGPA: string
  Current_SGPA: string
  Repeated_Courses: string
  Current_Year: string
  Current_Semester: string
}

function Prediction() {
  const [form, setForm] = useState<PredictionForm>({
    Previous_SGPA: '',
    Current_SGPA: '',
    Repeated_Courses: '',
    Current_Year: '',
    Current_Semester: '',
  })

  useEffect(() => {
  const loadStudentData = async () => {
    try {
      setError('')

      const response = await fetch(
        `${BACKEND_URL}/api/students/dashboard?studentId=${encodeURIComponent(STUDENT_ID)}`
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : 'Failed to load student data.'
        )
      }

      console.log('Student data:', data)

      const records = data.semesterRecords || []

      if (records.length === 0) {
        throw new Error(
          'No saved SGPA records found.'
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
    }
  }

  loadStudentData()
}, [])

  const [prediction, setPrediction] = useState<number | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    })
  }

  const handleSGPAChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const { name, value } = e.target

    if (value === '') {
      setForm({
        ...form,
        [name]: '',
      })
      return
    }

    const sgpaPattern = /^\d{0,1}(\.\d{0,4})?$/

    if (!sgpaPattern.test(value)) {
      return
    }

    const numericValue = Number(value)

    if (numericValue > 4) {
      return
    }

    setForm({
      ...form,
      [name]: value,
    })
  }

  const predictSGPA = async (e: React.FormEvent) => {
    e.preventDefault()

    setLoading(true)
    setPrediction(null)
    setError('')

    try {
      const response = await fetch(
        `${API_URL}/predict-next-sgpa`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            Previous_SGPA: Number(form.Previous_SGPA),
            Current_SGPA: Number(form.Current_SGPA),
            Repeated_Courses: Number(form.Repeated_Courses),
            Current_Year: Number(form.Current_Year),
            Current_Semester: Number(form.Current_Semester),
          }),
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Prediction failed.'
        )
      }

      setPrediction(data.Predicted_Next_SGPA)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to connect to the prediction service.'
      )
    } finally {
      setLoading(false)
    }
  }

  const getPerformanceLevel = (gpa: number) => {
    if (gpa >= 3.5) return 'Excellent'
    if (gpa >= 3.0) return 'Good'
    if (gpa >= 2.0) return 'Satisfactory'

    return 'Needs Improvement'
  }

  return (
    <main className="prediction-page">

      {/* HEADER */}

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
            <strong>Neural Network</strong>
            <small>Prediction Engine</small>
          </div>
        </div>

      </section>

      {/* MAIN GRID */}

      <section className="prediction-grid">

        {/* INPUT CARD */}

        <div className="prediction-card">

          <div className="prediction-card-header">

            <div className="step-number">
              01
            </div>

            <div>
              <h2>Academic Information</h2>

              <p>
                Enter your current academic details.
              </p>
            </div>

          </div>

          <form onSubmit={predictSGPA}>

            <div className="prediction-form-grid">

              {/* Previous SGPA */}

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
                  required
                />

                <small>
                  Range: 0.0000 – 4.0000
                </small>

              </div>

              {/* Current SGPA */}

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
                  required
                />

                <small>
                  Range: 0.0000 – 4.0000
                </small>

              </div>

              {/* Repeated Courses */}

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
                  required
                />

                <small>
                  Number of repeated courses
                </small>

              </div>

              {/* Academic Year */}

              <div className="prediction-field">

                <label htmlFor="Current_Year">
                  Academic Year
                </label>

                <select
                  id="Current_Year"
                  name="Current_Year"
                  value={form.Current_Year}
                  onChange={handleChange}
                >
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

              {/* Semester */}

              <div className="prediction-field">

                <label htmlFor="Current_Semester">
                  Current Semester
                </label>

                <select
                  id="Current_Semester"
                  name="Current_Semester"
                  value={form.Current_Semester}
                  onChange={handleChange}
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

              </div>

            </div>

            <button
              type="submit"
              className="prediction-submit"
              disabled={loading}
            >
              {loading
                ? 'Running Prediction...'
                : 'Predict Next Semester SGPA'}

              {!loading && (
                <span>→</span>
              )}
            </button>

          </form>

          {error && (
            <div className="prediction-error">
              <strong>Prediction unavailable</strong>

              <span>
                {error}
              </span>
            </div>
          )}

        </div>

        {/* RESULT CARD */}

        <div className="prediction-card result-panel">

          <div className="prediction-card-header">

            <div className="step-number result-step">
              02
            </div>

            <div>
              <h2>Prediction Result</h2>

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
                {getPerformanceLevel(prediction)}
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
                      Number(form.Current_SGPA)
                        ? 'positive'
                        : 'negative'
                    }
                  >
                    {prediction >=
                    Number(form.Current_SGPA)
                      ? '+'
                      : ''}

                    {(
                      prediction -
                      Number(form.Current_SGPA)
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

      {/* MODEL INFORMATION */}

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

          <span>Previous SGPA</span>
          <span>Current SGPA</span>
          <span>Repeated Courses</span>
          <span>Academic Year</span>
          <span>Semester</span>

        </div>

      </section>

    </main>
  )
}

export default Prediction