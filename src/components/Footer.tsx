import { Link } from 'react-router-dom'
import './Footer.css'

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">

        {/* Brand */}
        <div className="footer-brand">
          <Link
            to="/"
            className="footer-brand-link"
            aria-label="KDU Academic Intelligence Home"
          >
            <div className="footer-logo">
              <img
                src="/kdu-logo.png"
                alt="KDU"
              />
            </div>

            <div className="footer-brand-content">
              <strong>KDU Academic Intelligence</strong>

              <p>
                AI-powered academic decision support
                for the KDU community.
              </p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav
          className="footer-nav"
          aria-label="Footer navigation"
        >
          <Link to="/#home">Home</Link>
          <Link to="/#about">About</Link>
          <Link to="/#services">Services</Link>
          <Link to="/#contact">Contact</Link>
          <Link to="/login">Login</Link>
          <Link to="/register">Get Started</Link>
        </nav>

      </div>

      {/* Bottom */}
      <div className="footer-bottom">
        <span>
          © 2026 KDU Academic Intelligence
        </span>

        <span>
          AI-Based Smart Campus Decision Support System
        </span>
      </div>
    </footer>
  )
}

export default Footer