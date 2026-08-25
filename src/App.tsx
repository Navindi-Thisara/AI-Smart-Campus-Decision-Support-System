import { useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'

function App() {
  const [form, setForm] = useState({
    Previous_SGPA: '3.2000',
    Current_SGPA: '3.4500',
    Repeated_Courses: '0',
    Current_Year: '2',
    Current_Semester: '4',
  })

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

    // Allow empty value
    if (value === '') {
      setForm({
        ...form,
        [name]: '',
      })
      return
    }

    // Allow only numbers with up to 4 decimal places
    const sgpaPattern = /^\d{0,1}(\.\d{0,4})?$/

    if (!sgpaPattern.test(value)) {
      return
    }

    // Maximum SGPA is 4.0000
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
      const response = await fetch(`${API_URL}/predict-next-sgpa`, {
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
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Prediction failed.')
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

  const getPerformanceDescription = (gpa: number) => {
    if (gpa >= 3.5) {
      return 'The predicted performance is excellent. Keep maintaining your current academic habits.'
    }

    if (gpa >= 3.0) {
      return 'The predicted performance is good. Continue your current study approach and focus on consistency.'
    }

    if (gpa >= 2.0) {
      return 'The predicted performance is satisfactory. Additional study effort could help improve the next semester.'
    }

    return 'The predicted performance indicates that additional academic support may be beneficial.'
  }

  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">SC</div>

          <div>
            <strong>Smart Campus</strong>
            <span>AI Decision Support System</span>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI Service Online
        </div>
      </header>

      <main>
        <section className="hero">
          <div className="hero-badge">
            AI-POWERED STUDENT SERVICES
          </div>

          <h1>
            Predict Your
            <span> Next Semester SGPA</span>
          </h1>

          <p>
            Use your academic history and current performance to estimate
            your next semester GPA with our trained Neural Network model.
          </p>
        </section>

        <section className="dashboard">

          {/* STUDENT INFORMATION CARD */}
          <div className="card form-card">
            <div className="card-heading">
              <div className="heading-icon">01</div>

              <div>
                <h2>Student Information</h2>
                <p>Enter your current academic information.</p>
              </div>
            </div>

            <form onSubmit={predictSGPA}>
              <div className="form-grid">

                {/* PREVIOUS SGPA */}
                <div className="field">
                  <label htmlFor="Previous_SGPA">
                    Previous SGPA
                  </label>

                  <input
                    id="Previous_SGPA"
                    name="Previous_SGPA"
                    type="text"
                    inputMode="decimal"
                    placeholder="0.0000"
                    value={form.Previous_SGPA}
                    onChange={handleSGPAChange}
                    required
                  />

                  <small>0.0000 – 4.0000</small>
                </div>

                {/* CURRENT SGPA */}
                <div className="field">
                  <label htmlFor="Current_SGPA">
                    Current SGPA
                  </label>

                  <input
                    id="Current_SGPA"
                    name="Current_SGPA"
                    type="text"
                    inputMode="decimal"
                    placeholder="0.0000"
                    value={form.Current_SGPA}
                    onChange={handleSGPAChange}
                    required
                  />

                  <small>0.0000 – 4.0000</small>
                </div>

                {/* REPEATED COURSES */}
                <div className="field">
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

                {/* CURRENT YEAR */}
                <div className="field">
                  <label htmlFor="Current_Year">
                    Current Year
                  </label>

                  <select
                    id="Current_Year"
                    name="Current_Year"
                    value={form.Current_Year}
                    onChange={handleChange}
                  >
                    <option value="1">Year 1</option>
                    <option value="2">Year 2</option>
                    <option value="3">Year 3</option>
                    <option value="4">Year 4</option>
                  </select>
                </div>

                {/* CURRENT SEMESTER */}
                <div className="field">
                  <label htmlFor="Current_Semester">
                    Current Semester
                  </label>

                  <select
                    id="Current_Semester"
                    name="Current_Semester"
                    value={form.Current_Semester}
                    onChange={handleChange}
                  >
                    <option value="1">Semester 1</option>
                    <option value="2">Semester 2</option>
                    <option value="3">Semester 3</option>
                    <option value="4">Semester 4</option>
                    <option value="5">Semester 5</option>
                    <option value="6">Semester 6</option>
                    <option value="7">Semester 7</option>
                    <option value="8">Semester 8</option>
                  </select>
                </div>

              </div>

              <button
                className="predict-button"
                type="submit"
                disabled={loading}
              >
                {loading
                  ? 'Predicting...'
                  : 'Predict Next Semester SGPA'}

                {!loading && <span>→</span>}
              </button>
            </form>

            {error && (
              <div className="error-message">
                <strong>Prediction Error</strong>
                <span>{error}</span>
              </div>
            )}
          </div>

          {/* RESULT CARD */}
          <div
            className={`card result-card ${
              prediction !== null ? 'has-result' : ''
            }`}
          >
            <div className="card-heading">
              <div className="heading-icon result-icon">
                02
              </div>

              <div>
                <h2>Prediction Result</h2>
                <p>AI-generated next semester prediction.</p>
              </div>
            </div>

            {prediction === null ? (

              <div className="empty-result">
                <div className="empty-icon">✦</div>

                <h3>Ready to predict</h3>

                <p>
                  Enter your academic information and click the
                  prediction button to generate your estimated
                  next semester SGPA.
                </p>
              </div>

            ) : (

              <div className="prediction">

                <span className="prediction-label">
                  Predicted Next Semester SGPA
                </span>

                <div className="gpa-value">
                  {prediction.toFixed(4)}
                </div>

                <div className="performance-badge">
                  {getPerformanceLevel(prediction)}
                </div>

                <p className="prediction-description">
                  {getPerformanceDescription(prediction)}
                </p>

                <div className="prediction-details">

                  {/* CURRENT SGPA */}
                  <div>
                    <span>Current SGPA</span>

                    <strong>
                      {Number(form.Current_SGPA).toFixed(4)}
                    </strong>
                  </div>

                  {/* PREDICTED CHANGE */}
                  <div>
                    <span>Predicted Change</span>

                    <strong
                      className={
                        prediction >= Number(form.Current_SGPA)
                          ? 'positive'
                          : 'negative'
                      }
                    >
                      {prediction >= Number(form.Current_SGPA)
                        ? '+'
                        : ''}

                      {(
                        prediction -
                        Number(form.Current_SGPA)
                      ).toFixed(4)}
                    </strong>
                  </div>

                </div>
              </div>
            )}
          </div>
        </section>

        {/* MODEL INFORMATION */}
        <section className="model-info">
          <div>
            <span className="model-icon">AI</span>

            <div>
              <strong>Neural Network Prediction</strong>

              <p>
                Trained and validated on the Smart Campus
                academic dataset.
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

      <footer>
        <p>AI-Based Smart Campus Decision Support System</p>
        <span>Student Performance Prediction Module</span>
      </footer>
    </div>
  )
}

export default App