import { FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import './Register.css'

type UserRole = 'STUDENT' | 'STAFF'

interface RegisterForm {
  fullName: string
  email: string
  studentId: string
  password: string
  confirmPassword: string
  role: UserRole
}

function Register() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState<RegisterForm>({
    fullName: '',
    email: '',
    studentId: '',
    password: '',
    confirmPassword: '',
    role: 'STUDENT',
  })

  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] =
    useState(false)

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const handleChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const { name, value } = event.target

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }))

    setError('')
  }

  const handleRoleChange = (role: UserRole) => {
    setFormData((previous) => ({
      ...previous,
      role,
      studentId: role === 'STAFF' ? '' : previous.studentId,
    }))

    setError('')
  }

  const validateForm = () => {
    if (
      !formData.fullName.trim() ||
      !formData.email.trim() ||
      !formData.password ||
      !formData.confirmPassword
    ) {
      return 'Please complete all required fields.'
    }

    if (formData.fullName.trim().length < 2) {
      return 'Please enter your full name.'
    }

    if (!formData.email.includes('@')) {
      return 'Please enter a valid email address.'
    }

    if (!formData.studentId.trim()) {
      return formData.role === 'STUDENT'
        ? 'Student ID is required for student accounts.'
        : 'Staff ID is required for staff accounts.'
    }

    if (formData.password.length < 8) {
      return 'Password must contain at least 8 characters.'
    }

    if (!/[A-Z]/.test(formData.password)) {
      return 'Password must contain at least one uppercase letter.'
    }

    if (!/[a-z]/.test(formData.password)) {
      return 'Password must contain at least one lowercase letter.'
    }

    if (!/\d/.test(formData.password)) {
      return 'Password must contain at least one number.'
    }

    if (formData.password !== formData.confirmPassword) {
      return 'Passwords do not match.'
    }

    return ''
  }

  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    setError('')
    setSuccess('')

    const validationError = validateForm()

    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        'http://localhost:8080/api/auth/register',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            fullName: formData.fullName.trim(),
            email: formData.email.trim(),
            studentId: formData.studentId.trim(),
            password: formData.password,
            confirmPassword: formData.confirmPassword,
            role: formData.role,
          }),
        },
      )

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        if (data?.errors) {
          const messages = Object.values(data.errors) as string[]

          throw new Error(messages.join(' '))
        }

        throw new Error(
          data?.message ||
            'Registration failed. Please try again.',
        )
      }

      setSuccess(
        'Your account has been created successfully.',
      )

      setFormData({
        fullName: '',
        email: '',
        studentId: '',
        password: '',
        confirmPassword: '',
        role: 'STUDENT',
      })

      setTimeout(() => {
        navigate('/login')
      }, 1200)
    } catch (err) {
      if (err instanceof TypeError) {
        setError(
          'Unable to connect to the server. Please make sure the Spring Boot backend is running.',
        )
      } else if (err instanceof Error) {
        setError(err.message)
      } else {
        setError(
          'Registration failed. Please try again.',
        )
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="register-page">
      <div className="register-container">

        {/* =====================================================
            LEFT SIDE
            ===================================================== */}

        <section className="register-intro">

          <div className="register-intro-badge">
            KDU Academic Intelligence
          </div>

          <h1>
            Start your academic
            <span> intelligence journey.</span>
          </h1>

          <p>
            Create your account to access personalized
            academic insights, performance predictions,
            and intelligent student services.
          </p>

          <div className="register-benefits">

            <div className="register-benefit">
              <div className="register-benefit-icon">
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="M5 12.5l4 4L19 6.5"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>

              <div>
                <strong>
                  Personalized academic insights
                </strong>

                <span>
                  Understand your academic performance
                  with intelligent analytics.
                </span>
              </div>
            </div>

            <div className="register-benefit">
              <div className="register-benefit-icon">
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="M5 12.5l4 4L19 6.5"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>

              <div>
                <strong>
                  AI-powered predictions
                </strong>

                <span>
                  Get data-driven predictions to support
                  your academic decisions.
                </span>
              </div>
            </div>

            <div className="register-benefit">
              <div className="register-benefit-icon">
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="M5 12.5l4 4L19 6.5"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>

              <div>
                <strong>
                  Smart student services
                </strong>

                <span>
                  Access academic support designed for
                  the KDU community.
                </span>
              </div>
            </div>

          </div>
        </section>


        {/* =====================================================
            REGISTER CARD
            ===================================================== */}

        <section className="register-card">

          <div className="register-card-header">
            <h2>Create your account</h2>

            <p>
              Select your account type and enter your details.
            </p>
          </div>


          <form
            className="register-form"
            onSubmit={handleSubmit}
          >

            {/* =================================================
                ROLE
                ================================================= */}

            <div className="register-role-section">

              <label className="register-role-label">
                Account type
              </label>

              <div className="register-role-options">

                <button
                  type="button"
                  className={`role-option ${
                    formData.role === 'STUDENT'
                      ? 'active'
                      : ''
                  }`}
                  onClick={() =>
                    handleRoleChange('STUDENT')
                  }
                  disabled={loading}
                >
                  <span className="role-icon">

                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />

                      <path
                        d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />
                    </svg>

                  </span>

                  <span className="role-content">
                    <strong>Student</strong>
                    <small>Academic services</small>
                  </span>

                  <span className="role-radio">
                    {formData.role === 'STUDENT' && (
                      <span />
                    )}
                  </span>
                </button>


                <button
                  type="button"
                  className={`role-option ${
                    formData.role === 'STAFF'
                      ? 'active'
                      : ''
                  }`}
                  onClick={() =>
                    handleRoleChange('STAFF')
                  }
                  disabled={loading}
                >
                  <span className="role-icon">

                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        d="M4 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />

                      <circle
                        cx="10"
                        cy="7"
                        r="3"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />

                      <path
                        d="M16 4.5a3 3 0 0 1 0 5.8M19 21v-2a4 4 0 0 0-2.5-3.7"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />
                    </svg>

                  </span>

                  <span className="role-content">
                    <strong>Staff</strong>
                    <small>Staff services</small>
                  </span>

                  <span className="role-radio">
                    {formData.role === 'STAFF' && (
                      <span />
                    )}
                  </span>
                </button>

              </div>
            </div>


            {/* =================================================
                FULL NAME
                ================================================= */}

            <div className="register-field">

              <label htmlFor="fullName">
                Full name
              </label>

              <input
                id="fullName"
                name="fullName"
                type="text"
                value={formData.fullName}
                onChange={handleChange}
                placeholder="Enter your full name"
                autoComplete="name"
                disabled={loading}
              />

            </div>


            {/* =================================================
                EMAIL
                ================================================= */}

            <div className="register-field">

              <label htmlFor="email">
                University email
              </label>

              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="name@kdu.ac.lk"
                autoComplete="email"
                disabled={loading}
              />

            </div>


            {/* =================================================
                STUDENT ID
                ================================================= */}

            {formData.role === 'STUDENT' && (
              <div className="register-field">

                <label htmlFor="studentId">
                  Student ID
                </label>

                <input
                  id="studentId"
                  name="studentId"
                  type="text"
                  value={formData.studentId}
                  onChange={handleChange}
                  placeholder="e.g. KDU/COE/42/0001"
                  autoComplete="username"
                  disabled={loading}
                />

              </div>
            )}


            {/* =================================================
                STAFF ID
                ================================================= */}

            {formData.role === 'STAFF' && (
              <div className="register-field">

                <label htmlFor="studentId">
                  Staff ID
                </label>

                <input
                  id="studentId"
                  name="studentId"
                  type="text"
                  value={formData.studentId}
                  onChange={handleChange}
                  placeholder="Enter your staff ID"
                  autoComplete="username"
                  disabled={loading}
                />

              </div>
            )}


            {/* =================================================
                PASSWORD
                ================================================= */}

            <div className="register-field">

              <label htmlFor="password">
                Password
              </label>

              <div className="register-password-wrapper">

                <input
                  id="password"
                  name="password"
                  type={
                    showPassword
                      ? 'text'
                      : 'password'
                  }
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Create a password"
                  autoComplete="new-password"
                  disabled={loading}
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword(
                      (previous) => !previous,
                    )
                  }
                  disabled={loading}
                  aria-label={
                    showPassword
                      ? 'Hide password'
                      : 'Show password'
                  }
                >
                  {showPassword ? (
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        d="M3 3l18 18"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />

                      <path
                        d="M10.6 10.6a2 2 0 0 0 2.8 2.8"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />

                      <path
                        d="M9.9 4.3A10.8 10.8 0 0 1 12 4c5.2 0 8.5 4 9.8 6.1a3.5 3.5 0 0 1 0 .8 15.4 15.4 0 0 1-3.1 3.8M6.2 6.2C4.2 7.5 2.8 9.3 2.2 10.1a3.5 3.5 0 0 0 0 .8C3.5 13 6.8 17 12 17c1.1 0 2.1-.2 3-.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />
                    </svg>
                  ) : (
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        d="M2.2 12.1C3.5 10 6.8 6 12 6s8.5 4 9.8 6.1a1.5 1.5 0 0 1 0 .8C20.5 15 17.2 19 12 19s-8.5-4-9.8-6.1a1.5 1.5 0 0 1 0-.8Z"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />

                      <circle
                        cx="12"
                        cy="12.5"
                        r="2.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />
                    </svg>
                  )}
                </button>

              </div>
            </div>


            {/* =================================================
                CONFIRM PASSWORD
                ================================================= */}

            <div className="register-field">

              <label htmlFor="confirmPassword">
                Confirm password
              </label>

              <div className="register-password-wrapper">

                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={
                    showConfirmPassword
                      ? 'text'
                      : 'password'
                  }
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Confirm your password"
                  autoComplete="new-password"
                  disabled={loading}
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowConfirmPassword(
                      (previous) => !previous,
                    )
                  }
                  disabled={loading}
                  aria-label={
                    showConfirmPassword
                      ? 'Hide password'
                      : 'Show password'
                  }
                >
                  {showConfirmPassword ? (
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        d="M3 3l18 18"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />

                      <path
                        d="M10.6 10.6a2 2 0 0 0 2.8 2.8"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />

                      <path
                        d="M9.9 4.3A10.8 10.8 0 0 1 12 4c5.2 0 8.5 4 9.8 6.1M6.2 6.2C4.2 7.5 2.8 9.3 2.2 10.1a3.5 3.5 0 0 0 0 .8C3.5 13 6.8 17 12 17c1.1 0 2.1-.2 3-.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                        strokeLinecap="round"
                      />
                    </svg>
                  ) : (
                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        d="M2.2 12.1C3.5 10 6.8 6 12 6s8.5 4 9.8 6.1a1.5 1.5 0 0 1 0 .8C20.5 15 17.2 19 12 19s-8.5-4-9.8-6.1a1.5 1.5 0 0 1 0-.8Z"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />

                      <circle
                        cx="12"
                        cy="12.5"
                        r="2.5"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="1.8"
                      />
                    </svg>
                  )}
                </button>

              </div>
            </div>


            <p className="password-hint">
              Use at least 8 characters with uppercase,
              lowercase, and a number.
            </p>


            {/* =================================================
                ERROR
                ================================================= */}

            {error && (
              <div
                className="register-message register-error"
                role="alert"
              >
                <span>!</span>
                <p>{error}</p>
              </div>
            )}


            {/* =================================================
                SUCCESS
                ================================================= */}

            {success && (
              <div
                className="register-message register-success"
                role="status"
              >
                <span>✓</span>
                <p>{success}</p>
              </div>
            )}


            {/* =================================================
                SUBMIT
                ================================================= */}

            <button
              type="submit"
              className="register-submit"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="register-spinner" />
                  Creating account...
                </>
              ) : (
                <>
                  Create account
                  <svg
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      d="M5 12h14M13 6l6 6-6 6"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </>
              )}
            </button>


            {/* =================================================
                LOGIN
                ================================================= */}

            <p className="register-login">
              Already have an account?
              <Link to="/login">
                Sign in
              </Link>
            </p>

          </form>
        </section>
      </div>
    </main>
  )
}

export default Register