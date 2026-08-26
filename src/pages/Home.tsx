import { useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import './Home.css'

const NAVBAR_OFFSET = 80

function Home() {
  const location = useLocation()
  const navigate = useNavigate()
  

  useEffect(() => {
    if (!location.hash) return

    const id = decodeURIComponent(location.hash.substring(1))

    const timer = window.setTimeout(() => {
      const element = document.getElementById(id)

      if (!element) return

      const top =
        element.getBoundingClientRect().top +
        window.scrollY -
        NAVBAR_OFFSET

      window.scrollTo({
        top: Math.max(top, 0),
        behavior: 'smooth',
      })
    }, 100)

    return () => window.clearTimeout(timer)
  }, [location.hash])

  /* =========================================================
     SECTION NAVIGATION
     ========================================================= */

  const scrollToSection = (
    event: React.MouseEvent<HTMLAnchorElement>,
    id: string,
  ) => {
    event.preventDefault()

    const element = document.getElementById(id)

    if (!element) return

    const top =
      element.getBoundingClientRect().top +
      window.scrollY -
      NAVBAR_OFFSET

    window.scrollTo({
      top: Math.max(top, 0),
      behavior: 'smooth',
    })

    navigate(
      {
        pathname: '/',
        hash: `#${id}`,
      },
      {
        replace: true,
      },
    )
  }

  return (
    <main className="home-page">

      {/* =====================================================
          HERO
          ===================================================== */}

      <section
        className="hero-section"
        id="home"
        aria-labelledby="hero-title"
      >

        <div
          className="hero-glow hero-glow-one"
          aria-hidden="true"
        />

        <div
          className="hero-glow hero-glow-two"
          aria-hidden="true"
        />

        <div
          className="hero-grid"
          aria-hidden="true"
        />

        <div
          className="hero-particles"
          aria-hidden="true"
        >
          <span />
          <span />
          <span />
          <span />
          <span />
        </div>

        <div className="home-container hero-container">

          {/* HERO CONTENT */}

          <div className="hero-content">

            <div
              className="hero-eyebrow"
              aria-label="KDU Academic Intelligence"
            >
              <span
                className="eyebrow-dot"
                aria-hidden="true"
              />

              KDU ACADEMIC INTELLIGENCE
            </div>

            <h1 id="hero-title">
              Turn academic data into
              <span> smarter decisions.</span>
            </h1>

            <p className="hero-description">
              Use AI-powered insights to understand your
              academic performance, predict future outcomes,
              and make better decisions about your studies.
            </p>

            <div className="hero-actions">

              <Link
                to="/register"
                className="hero-primary-button"
              >
                Get Started

                <span
                  className="button-arrow"
                  aria-hidden="true"
                >
                  →
                </span>
              </Link>

              <a
                href="/#services"
                className="hero-secondary-button"
                onClick={(event) =>
                  scrollToSection(event, 'services')
                }
              >
                Explore Platform
              </a>

            </div>

            <div
              className="hero-trust"
              aria-label="Platform benefits"
            >

              <div className="trust-item">
                <span
                  className="trust-check"
                  aria-hidden="true"
                >
                  ✓
                </span>

                <span>AI-powered</span>
              </div>

              <div className="trust-item">
                <span
                  className="trust-check"
                  aria-hidden="true"
                >
                  ✓
                </span>

                <span>Personalized</span>
              </div>

              <div className="trust-item">
                <span
                  className="trust-check"
                  aria-hidden="true"
                >
                  ✓
                </span>

                <span>Data-driven</span>
              </div>

            </div>

          </div>


          {/* =================================================
              HERO VISUAL
              ================================================= */}

          <div
            className="hero-visual"
            aria-label="Academic intelligence dashboard preview"
            role="img"
          >

            <div
              className="visual-orbit orbit-one"
              aria-hidden="true"
            />

            <div
              className="visual-orbit orbit-two"
              aria-hidden="true"
            />

            <div
              className="visual-orbit orbit-three"
              aria-hidden="true"
            />


            {/* =================================================
                DASHBOARD
                ================================================= */}

            <div className="dashboard-3d-wrapper">

              <div
                className="dashboard-reflection"
                aria-hidden="true"
              />

              <div className="dashboard-preview">

                {/* HEADER */}

                <div className="preview-header">

                  <div className="preview-heading">

                    <span className="preview-label">
                      ACADEMIC OVERVIEW
                    </span>

                    <h3>
                      Performance Intelligence
                    </h3>

                  </div>

                  <div
                    className="preview-status"
                    aria-label="AI Active"
                  >
                    <span aria-hidden="true" />
                    AI Active
                  </div>

                </div>


                {/* SCORE */}

                <div className="preview-main-score">

                  <div className="score-information">

                    <span className="score-label">
                      Current SGPA
                    </span>

                    <strong>
                      3.62
                    </strong>

                    <div className="score-change">
                      <span aria-hidden="true">
                        ↗
                      </span>

                      +0.28
                    </div>

                  </div>


                  <div
                    className="score-ring"
                    aria-label="86 percent progress"
                  >

                    <div className="score-ring-inner">
                      <strong>86%</strong>
                      <span>Progress</span>
                    </div>

                  </div>

                </div>


                {/* CHART */}

                <div className="preview-chart">

                  <div className="chart-header">
                    <span>Performance</span>
                    <span>6 Semesters</span>
                  </div>

                  <div className="chart-area">

                    <div
                      className="chart-lines"
                      aria-hidden="true"
                    >
                      <span />
                      <span />
                      <span />
                      <span />
                    </div>

                    <svg
                      className="performance-chart"
                      viewBox="0 0 500 150"
                      preserveAspectRatio="none"
                      aria-hidden="true"
                    >

                      <defs>

                        <linearGradient
                          id="homeAreaGradient"
                          x1="0"
                          x2="0"
                          y1="0"
                          y2="1"
                        >

                          <stop
                            offset="0%"
                            stopOpacity="0.30"
                          />

                          <stop
                            offset="100%"
                            stopOpacity="0"
                          />

                        </linearGradient>

                        <filter
                          id="homeChartGlow"
                          x="-50%"
                          y="-50%"
                          width="200%"
                          height="200%"
                        >

                          <feGaussianBlur
                            stdDeviation="3"
                            result="blur"
                          />

                          <feMerge>

                            <feMergeNode in="blur" />

                            <feMergeNode
                              in="SourceGraphic"
                            />

                          </feMerge>

                        </filter>

                      </defs>


                      <path
                        className="chart-area-fill"
                        d="
                          M0 125
                          L65 105
                          L130 112
                          L195 82
                          L260 91
                          L325 61
                          L390 70
                          L455 35
                          L500 45
                          L500 150
                          L0 150
                          Z
                        "
                      />


                      <path
                        className="chart-line"
                        d="
                          M0 125
                          L65 105
                          L130 112
                          L195 82
                          L260 91
                          L325 61
                          L390 70
                          L455 35
                          L500 45
                        "
                        filter="url(#homeChartGlow)"
                      />

                      <circle
                        className="chart-point"
                        cx="455"
                        cy="35"
                        r="5"
                      />

                    </svg>

                  </div>

                  <div className="chart-labels">
                    <span>S1</span>
                    <span>S2</span>
                    <span>S3</span>
                    <span>S4</span>
                    <span>S5</span>
                    <span>S6</span>
                  </div>

                </div>


                {/* INSIGHTS */}

                <div className="preview-insights">

                  <div className="insight-card">

                    <span
                      className="insight-icon blue"
                      aria-hidden="true"
                    >
                      ✦
                    </span>

                    <div>
                      <span>Prediction</span>
                      <strong>
                        3.78 SGPA
                      </strong>
                    </div>

                  </div>


                  <div className="insight-card">

                    <span
                      className="insight-icon gold"
                      aria-hidden="true"
                    >
                      ◈
                    </span>

                    <div>
                      <span>Risk</span>

                      <strong className="low-risk">
                        Low Risk
                      </strong>

                    </div>

                  </div>

                </div>

              </div>

            </div>


            {/* =================================================
                FLOATING AI CARD
                ================================================= */}

            <div
              className="floating-ai-card"
              aria-hidden="true"
            >

              <div className="ai-card-icon">
                ✦
              </div>

              <div>

                <span>
                  AI Recommendation
                </span>

                <strong>
                  Focus on 2 modules
                </strong>

              </div>

              <span className="ai-card-arrow">
                →
              </span>

            </div>


            {/* =================================================
                FLOATING DATA BADGE
                ================================================= */}

            <div
              className="floating-data-badge"
              aria-hidden="true"
            >

              <span className="data-badge-pulse" />

              <div>
                <strong>+12.4%</strong>
                <span>
                  Performance trend
                </span>
              </div>

            </div>

          </div>

        </div>


        <div
          className="hero-bottom-fade"
          aria-hidden="true"
        />

      </section>


      {/* =====================================================
          ABOUT / INTELLIGENCE
          ===================================================== */}

      <section
        className="intelligence-section"
        id="about"
        aria-labelledby="intelligence-title"
      >

        <div
          className="intelligence-pattern"
          aria-hidden="true"
        />

        <div className="home-container">

          <div className="intelligence-card">

            <div className="intelligence-copy">

              <span className="section-kicker">
                ABOUT THE PLATFORM
              </span>

              <h2 id="intelligence-title">
                Your academics.
                <span> Made intelligent.</span>
              </h2>

              <p>
                KDU Academic Intelligence combines
                academic data, predictive analytics,
                and AI-powered reasoning to help students
                understand performance and make better
                academic decisions.
              </p>

              <div className="intelligence-points">

                <div>
                  <span>01</span>
                  <p>
                    Predict future performance
                  </p>
                </div>

                <div>
                  <span>02</span>
                  <p>
                    Identify academic risk early
                  </p>
                </div>

                <div>
                  <span>03</span>
                  <p>
                    Receive personalized guidance
                  </p>
                </div>

              </div>

            </div>


            <div
              className="intelligence-visual"
              aria-hidden="true"
            >

              <div
                className="intelligence-circle circle-one"
              />

              <div
                className="intelligence-circle circle-two"
              />

              <div
                className="intelligence-circle circle-three"
              />

              <div className="central-ai">

                <span>✦</span>

                <strong>AI</strong>

                <small>
                  INTELLIGENCE
                </small>

              </div>

              <div className="orbit-node node-one">
                <span>GPA</span>
              </div>

              <div className="orbit-node node-two">
                <span>Risk</span>
              </div>

              <div className="orbit-node node-three">
                <span>Plan</span>
              </div>

              <div className="orbit-node node-four">
                <span>Results</span>
              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          SERVICES
          ===================================================== */}

      <section
        className="platform-section"
        id="services"
        aria-labelledby="services-title"
      >

        <div className="home-container">

          <div className="section-heading centered">

            <span className="section-kicker">
              INTELLIGENT FEATURES
            </span>

            <h2 id="services-title">
              Everything you need.
              <span>
                {' '}One intelligent platform.
              </span>
            </h2>

            <p>
              Transform academic information into
              predictions, personalized plans, and
              actionable decisions.
            </p>

          </div>


          <div className="feature-grid">

            {/* SERVICE 01 */}

            <article
              className="feature-card feature-card-primary"
            >

              <div
                className="feature-glow"
                aria-hidden="true"
              />

              <div className="feature-top">

                <div
                  className="feature-icon"
                  aria-hidden="true"
                >
                  ✦
                </div>

                <span className="feature-number">
                  01
                </span>

              </div>

              <div className="feature-mini-label">
                PREDICTIVE AI
              </div>

              <h3>
                Performance Prediction
              </h3>

              <p>
                Predict future academic performance
                using intelligent analysis of your
                academic data and performance trends.
              </p>

            </article>


            {/* SERVICE 02 */}

            <article className="feature-card">

              <div
                className="feature-glow"
                aria-hidden="true"
              />

              <div className="feature-top">

                <div
                  className="feature-icon"
                  aria-hidden="true"
                >
                  ◈
                </div>

                <span className="feature-number">
                  02
                </span>

              </div>

              <div className="feature-mini-label">
                PERSONALIZED AI
              </div>

              <h3>
                Smart Study Planning
              </h3>

              <p>
                Build personalized study plans
                based on your academic goals,
                performance, and learning priorities.
              </p>

            </article>


            {/* SERVICE 03 */}

            <article className="feature-card">

              <div
                className="feature-glow"
                aria-hidden="true"
              />

              <div className="feature-top">

                <div
                  className="feature-icon"
                  aria-hidden="true"
                >
                  ✓
                </div>

                <span className="feature-number">
                  03
                </span>

              </div>

              <div className="feature-mini-label">
                RULE-BASED AI
              </div>

              <h3>
                Academic Eligibility
              </h3>

              <p>
                Check academic requirements,
                identify eligibility conditions,
                and make informed decisions.
              </p>

            </article>

          </div>

        </div>

      </section>


      {/* =====================================================
          HOW IT WORKS
          ===================================================== */}

      <section
        className="process-section"
        aria-labelledby="process-title"
      >

        <div className="home-container">

          <div className="process-layout">

            <div
              className="section-heading process-heading"
            >

              <span className="section-kicker">
                HOW IT WORKS
              </span>

              <h2 id="process-title">
                Data in.
                <span> Decisions out.</span>
              </h2>

              <p>
                A simple three-step journey from
                academic data to useful,
                AI-powered guidance.
              </p>

              <a
                href="/#about"
                className="text-link"
                onClick={(event) =>
                  scrollToSection(event, 'about')
                }
              >
                Discover the platform

                <span aria-hidden="true">
                  →
                </span>
              </a>

            </div>


            <div className="process-list">

              <div className="process-item">

                <div
                  className="process-number"
                  aria-hidden="true"
                >
                  01
                </div>

                <div className="process-content">

                  <span className="process-label">
                    INPUT
                  </span>

                  <h3>
                    Understand
                  </h3>

                  <p>
                    Your academic information comes
                    together in one intelligent view.
                  </p>

                </div>

              </div>


              <div
                className="process-connector"
                aria-hidden="true"
              />


              <div className="process-item">

                <div
                  className="process-number"
                  aria-hidden="true"
                >
                  02
                </div>

                <div className="process-content">

                  <span className="process-label">
                    ANALYSIS
                  </span>

                  <h3>
                    Analyze
                  </h3>

                  <p>
                    AI identifies performance trends,
                    academic risks, and opportunities.
                  </p>

                </div>

              </div>


              <div
                className="process-connector"
                aria-hidden="true"
              />


              <div className="process-item">

                <div
                  className="process-number"
                  aria-hidden="true"
                >
                  03
                </div>

                <div className="process-content">

                  <span className="process-label">
                    ACTION
                  </span>

                  <h3>
                    Act
                  </h3>

                  <p>
                    Receive clear recommendations
                    for your next academic step.
                  </p>

                </div>

              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          CTA
          ===================================================== */}

      <section
        className="cta-section"
        id="contact"
        aria-labelledby="cta-title"
      >

        <div className="home-container">

          <div className="cta-card">

            <div
              className="cta-decoration cta-decoration-one"
              aria-hidden="true"
            />

            <div
              className="cta-decoration cta-decoration-two"
              aria-hidden="true"
            />

            <div className="cta-content">

              <span className="section-kicker">
                GET STARTED
              </span>

              <h2 id="cta-title">
                Make your next academic decision
                <span> a smarter one.</span>
              </h2>

              <p>
                Turn your academic data into
                meaningful insights, predictions,
                and personalized guidance.
              </p>

              <div className="cta-actions">

                <Link
                  to="/register"
                  className="cta-primary"
                >
                  Get Started

                  <span aria-hidden="true">
                    →
                  </span>
                </Link>

                <a
                    href="mailto:navindithisara214@gmail.com"
                    className="cta-secondary"
                    >
                    Contact Us
                </a>

              </div>

            </div>

          </div>

        </div>

      </section>

    </main>
  )
}

export default Home