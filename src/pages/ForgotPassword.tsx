import {
  useState,
} from 'react'

import type {
  FormEvent,
} from 'react'

import {
  Link,
} from 'react-router-dom'

import './ForgotPassword.css'


function ForgotPassword() {
  const [email, setEmail] =
    useState('')

  const [loading, setLoading] =
    useState(false)

  const [error, setError] =
    useState('')

  const [success, setSuccess] =
    useState('')

  const handleSubmit = (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    setError('')
    setSuccess('')


    const cleanEmail =
      email.trim().toLowerCase()


    if (!cleanEmail) {
      setError(
        'Please enter your KDU university email address.',
      )

      return
    }


    if (
      !/^[A-Za-z0-9._%+-]+@kdu\.ac\.lk$/i.test(
        cleanEmail,
      )
    ) {
      setError(
        'Please use a valid KDU university email address.',
      )

      return
    }


    setLoading(true)

    setTimeout(() => {

      setLoading(false)

      setSuccess(
        'If an account exists for this email, password reset instructions will be sent shortly.',
      )

    }, 900)
  }


  return (
    <main className="forgot-page">

      <div className="forgot-container">

        <section className="forgot-intro">

          <div className="forgot-intro-badge">
            KDU Academic Intelligence
          </div>


          <h1>
            Reset your
            <span> password.</span>
          </h1>


          <p>
            No worries. Enter your registered KDU
            university email and we'll help you
            regain access to your account.
          </p>


          <div className="forgot-info">

            <div className="forgot-info-icon">

              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M12 3a9 9 0 1 0 9 9"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />

                <path
                  d="M12 7v5l3 2"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>

            </div>

            <div>

              <strong>
                Secure account recovery
              </strong>

              <span>
                We'll only use your registered
                university email for the recovery
                process.
              </span>

            </div>

          </div>

        </section>

        <section className="forgot-card">

          <div className="forgot-card-header">

            <div className="forgot-card-icon">

              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <rect
                  x="4"
                  y="10"
                  width="16"
                  height="11"
                  rx="2"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                />

                <path
                  d="M8 10V7a4 4 0 0 1 8 0v3"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />

                <circle
                  cx="12"
                  cy="15"
                  r="1"
                  fill="currentColor"
                />

                <path
                  d="M12 16v2"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              </svg>

            </div>


            <h2>
              Forgot password?
            </h2>

            <p>
              Enter your university email to
              receive password reset instructions.
            </p>

          </div>


          <form
            className="forgot-form"
            onSubmit={handleSubmit}
          >

            {/* EMAIL */}

            <div className="forgot-field">

              <label htmlFor="forgot-email">
                University email
              </label>

              <input
                id="forgot-email"
                type="email"
                value={email}
                onChange={(event) => {
                  setEmail(event.target.value)

                  setError('')
                  setSuccess('')
                }}
                placeholder="name@kdu.ac.lk"
                autoComplete="email"
                disabled={loading}
              />

            </div>


            <p className="forgot-hint">
              Use the email address associated with
              your KDU account.
            </p>


            {/* ERROR */}

            {error && (

              <div
                className="forgot-message forgot-error"
                role="alert"
              >

                <span>!</span>

                <p>
                  {error}
                </p>

              </div>

            )}

            {success && (

              <div
                className="forgot-message forgot-success"
                role="status"
              >

                <span>✓</span>

                <p>
                  {success}
                </p>

              </div>

            )}

            <button
              type="submit"
              className="forgot-submit"
              disabled={loading}
            >

              {loading ? (

                <>
                  <span className="forgot-spinner" />
                  Sending...
                </>

              ) : (

                <>
                  Send reset instructions

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

            <Link
              to="/login"
              className="forgot-back"
            >

              <svg
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  d="M19 12H5M11 18l-6-6 6-6"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>

              Back to sign in

            </Link>

          </form>

        </section>

      </div>

    </main>
  )
}

export default ForgotPassword