import {
  FormEvent,
  useState,
} from 'react'

import {
  Link,
  useNavigate,
} from 'react-router-dom'

import './Login.css'


interface LoginForm {
  email: string
  password: string
}


interface LoginResponse {
  message?: string

  user?: {
    id: number
    fullName: string
    email: string
    studentId: string
    role: 'STUDENT' | 'STAFF'
  }
}


function Login() {
  const navigate = useNavigate()

  const [formData, setFormData] =
    useState<LoginForm>({
      email: '',
      password: '',
    })

  const [showPassword, setShowPassword] =
    useState(false)

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState('')

  const [success, setSuccess] =
    useState('')


  // =========================================================
  // HANDLE INPUT CHANGE
  // =========================================================

  const handleChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const {
      name,
      value,
    } = event.target

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }))

    setError('')
    setSuccess('')
  }

  // VALIDATION
  const validateForm = () => {
    const email =
      formData.email.trim()

    if (!email || !formData.password) {
      return 'Please enter your university email and password.'
    }

    if (
      !/^[A-Za-z0-9._%+-]+@kdu\.ac\.lk$/i.test(email)
    ) {
      return 'Please use a valid KDU university email address.'
    }

    if (formData.password.length < 8) {
      return 'Password must contain at least 8 characters.'
    }

    return ''
  }

  // HANDLE LOGIN
  const handleSubmit = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    setError('')
    setSuccess('')

    const validationError =
      validateForm()

    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        'http://localhost:8080/api/auth/login',
        {
          method: 'POST',

          headers: {
            'Content-Type': 'application/json',
          },

          body: JSON.stringify({
            email:
              formData.email
                .trim()
                .toLowerCase(),

            password:
              formData.password,
          }),
        },
      )

      const data: LoginResponse | null =
        await response
          .json()
          .catch(() => null)


      if (!response.ok) {
        throw new Error(
          data?.message ||
          'Invalid email or password.',
        )
      }


      if (!data?.user) {
        throw new Error(
          'Login was successful, but user information was not returned.',
        )
      }

      // STORE USER SESSION
      localStorage.setItem(
        'user',
        JSON.stringify(data.user),
      )

      localStorage.setItem(
        'isAuthenticated',
        'true',
      )


      setSuccess(
        'Login successful. Redirecting...',
      )

      // ROLE-BASED REDIRECTION
      const destination =
        data.user.role === 'STAFF'
          ? '/staff-dashboard'
          : '/student-dashboard'


      setTimeout(() => {
        navigate(destination)
      }, 500)

    } catch (err) {

      if (err instanceof TypeError) {

        setError(
          'Unable to connect to the server. Please make sure the Spring Boot backend is running.',
        )

      } else if (err instanceof Error) {

        setError(err.message)

      } else {

        setError(
          'Login failed. Please try again.',
        )
      }

    } finally {

      setLoading(false)
    }
  }

  // FORGOT PASSWORD
  const handleForgotPassword = () => {
    navigate('/forgot-password')
  }


  return (
    <main className="login-page">

      <div className="login-container">

        {/* ===================================================
            LEFT SIDE
            =================================================== */}

        <section className="login-intro">

          <div className="login-intro-badge">
            KDU Academic Intelligence
          </div>


          <h1>
            Welcome
            <span> back.</span>
          </h1>


          <p>
            Sign in to access personalized academic
            insights, performance predictions, and
            intelligent student services.
          </p>


          <div className="login-benefits">

            <div className="login-benefit">

              <div className="login-benefit-icon">
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="m5 12 4 4L19 6"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.4"
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


            <div className="login-benefit">

              <div className="login-benefit-icon">
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="m5 12 4 4L19 6"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.4"
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
                  Get data-driven predictions to
                  support your academic decisions.
                </span>
              </div>

            </div>


            <div className="login-benefit">

              <div className="login-benefit-icon">
                <svg
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <path
                    d="m5 12 4 4L19 6"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.4"
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
                  Access academic support designed
                  for the KDU community.
                </span>
              </div>

            </div>

          </div>

        </section>


        {/* ===================================================
            LOGIN CARD
            =================================================== */}

        <section className="login-card">

          <div className="login-card-header">

            <h2>
              Sign in to your account
            </h2>

            <p>
              Enter your KDU credentials to continue.
            </p>

          </div>


          <form
            className="login-form"
            onSubmit={handleSubmit}
          >

            {/* EMAIL */}

            <div className="login-field">

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


            {/* PASSWORD */}

            <div className="login-field">

              <div className="login-password-label-row">

                <label htmlFor="password">
                  Password
                </label>

                <button
                  type="button"
                  className="forgot-password"
                  onClick={handleForgotPassword}
                  disabled={loading}
                >
                  Forgot password?
                </button>

              </div>


              <div className="login-password-wrapper">

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
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  disabled={loading}
                />


                <button
                  type="button"
                  className="login-password-toggle"
                  onClick={() =>
                    setShowPassword(
                      (previous) =>
                        !previous,
                    )
                  }
                  disabled={loading}
                  aria-label={
                    showPassword
                      ? 'Hide password'
                      : 'Show password'
                  }
                  title={
                    showPassword
                      ? 'Hide password'
                      : 'Show password'
                  }
                >

                  {showPassword ? (

                    /* EYE OFF */

                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        d="M3 3l18 18"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />

                      <path
                        d="M10.6 10.6a2 2 0 0 0 2.8 2.8"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />

                      <path
                        d="M9.9 4.2A10.8 10.8 0 0 1 12 4c5 0 8.5 4 10 8-0.6 1.6-1.6 3-2.9 4.2"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />

                      <path
                        d="M6.6 6.6C4.9 7.8 3.7 9.5 2 12c1.5 4 5 8 10 8 1.2 0 2.3-.2 3.3-.6"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>

                  ) : (

                    /* EYE */

                    <svg
                      viewBox="0 0 24 24"
                      aria-hidden="true"
                    >
                      <path
                        d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />

                      <circle
                        cx="12"
                        cy="12"
                        r="3"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                      />
                    </svg>

                  )}

                </button>

              </div>

            </div>


            <p className="login-password-hint">
              Use your registered KDU university
              email and password.
            </p>


            {/* ERROR */}

            {error && (

              <div
                className="login-message login-error"
                role="alert"
              >

                <span>!</span>

                <p>
                  {error}
                </p>

              </div>

            )}


            {/* SUCCESS */}

            {success && (

              <div
                className="login-message login-success"
                role="status"
              >

                <span>✓</span>

                <p>
                  {success}
                </p>

              </div>

            )}


            {/* SUBMIT */}

            <button
              type="submit"
              className="login-submit"
              disabled={loading}
            >

              {loading ? (

                <>
                  <span className="login-spinner" />
                  Signing in...
                </>

              ) : (

                <>
                  Sign in

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


            {/* REGISTER */}

            <p className="login-register">

              Don't have an account?

              <Link to="/register">
                Create an account
              </Link>

            </p>

          </form>

        </section>

      </div>

    </main>
  )
}

export default Login