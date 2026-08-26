import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import './Navbar.css'

const NAV_ITEMS = [
  { id: 'home', label: 'Home' },
  { id: 'about', label: 'About' },
  { id: 'services', label: 'Services' },
  { id: 'contact', label: 'Contact' },
]

const NAVBAR_OFFSET = 80

function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const [activeSection, setActiveSection] = useState('home')

  const location = useLocation()
  const navigate = useNavigate()

  const [darkMode, setDarkMode] = useState(
    () => localStorage.getItem('kdu-theme') === 'dark',
  )

  useEffect(() => {
    const savedTheme = localStorage.getItem('kdu-theme')

    const theme =
      savedTheme === 'dark'
        ? 'dark'
        : 'light'

    document.documentElement.setAttribute(
      'data-theme',
      theme,
    )

    setDarkMode(theme === 'dark')
  }, [])


  const toggleTheme = () => {
    const nextTheme =
      darkMode
        ? 'light'
        : 'dark'

    document.documentElement.setAttribute(
      'data-theme',
      nextTheme,
    )

    localStorage.setItem(
      'kdu-theme',
      nextTheme,
    )

    setDarkMode(nextTheme === 'dark')
  }

  // MOBILE MENU
  const closeMobileMenu = () => {
    setMobileMenuOpen(false)
  }


  useEffect(() => {
    document.body.style.overflow =
      mobileMenuOpen
        ? 'hidden'
        : ''

    return () => {
      document.body.style.overflow = ''
    }
  }, [mobileMenuOpen])


  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        closeMobileMenu()
      }
    }

    document.addEventListener(
      'keydown',
      handleEscape,
    )

    return () => {
      document.removeEventListener(
        'keydown',
        handleEscape,
      )
    }
  }, [])

  useEffect(() => {

    if (location.pathname !== '/') {
      setActiveSection('')
      return
    }

    const updateActiveSection = () => {
      const scrollPosition =
        window.scrollY + NAVBAR_OFFSET + 120

      const sections = NAV_ITEMS
        .map((item) => {
          const element =
            document.getElementById(item.id)

          if (!element) {
            return null
          }

          return {
            id: item.id,
            top: element.offsetTop,
          }
        })
        .filter(
          (
            section,
          ): section is {
            id: string
            top: number
          } => section !== null,
        )

      if (!sections.length) {
        setActiveSection('home')
        return
      }

      let currentSection = sections[0].id

      for (const section of sections) {
        if (
          scrollPosition >= section.top
        ) {
          currentSection = section.id
        } else {
          break
        }
      }

      setActiveSection(currentSection)
    }

    updateActiveSection()

    window.addEventListener(
      'scroll',
      updateActiveSection,
      { passive: true },
    )

    window.addEventListener(
      'resize',
      updateActiveSection,
    )

    return () => {
      window.removeEventListener(
        'scroll',
        updateActiveSection,
      )

      window.removeEventListener(
        'resize',
        updateActiveSection,
      )
    }
  }, [location.pathname])

  useEffect(() => {
    if (location.pathname !== '/') {
      return
    }

    if (!location.hash) {
      return
    }

    const id =
      location.hash.substring(1)

    const timer =
      window.setTimeout(() => {
        const element =
          document.getElementById(id)

        if (!element) {
          return
        }

        const top =
          element.getBoundingClientRect().top +
          window.scrollY -
          NAVBAR_OFFSET

        window.scrollTo({
          top: Math.max(top, 0),
          behavior: 'smooth',
        })

        setActiveSection(id)
      }, 100)

    return () => {
      window.clearTimeout(timer)
    }
  }, [
    location.pathname,
    location.hash,
  ])

  // NAVIGATION

  const handleNavClick = (
    event: React.MouseEvent<HTMLAnchorElement>,
    id: string,
  ) => {
    closeMobileMenu()

    if (location.pathname !== '/') {
      return
    }

    const element =
      document.getElementById(id)

    if (!element) {
      return
    }

    event.preventDefault()

    const top =
      element.getBoundingClientRect().top +
      window.scrollY -
      NAVBAR_OFFSET

    window.scrollTo({
      top: Math.max(top, 0),
      behavior: 'smooth',
    })

    setActiveSection(id)

    navigate(`/#${id}`, {
      replace: true,
    })
  }

  const handleBrandClick = () => {
    closeMobileMenu()

    if (location.pathname === '/') {
      window.scrollTo({
        top: 0,
        behavior: 'smooth',
      })

      setActiveSection('home')
      return
    }

    setActiveSection('')
  }

  const getNavLinkClass = (id: string) => {
    const isActive =
      location.pathname === '/' &&
      activeSection === id

    return `navbar-link ${
      isActive
        ? 'active'
        : ''
    }`
  }


  const getMobileNavLinkClass = (id: string) => {
    const isActive =
      location.pathname === '/' &&
      activeSection === id

    return `mobile-nav-link ${
      isActive
        ? 'active'
        : ''
    }`
  }

  return (
    <header className="navbar">

      <div className="navbar-container">

        {/* =================================================
            BRAND
            ================================================= */}

        <Link
          to="/"
          className="navbar-brand"
          onClick={handleBrandClick}
          aria-label="KDU Academic Intelligence Home"
        >

          <div className="navbar-logo-wrapper">

            <img
              src="/kdu-logo.png"
              alt="General Sir John Kotelawala Defence University"
              className="navbar-logo"
            />

          </div>

          <div className="navbar-brand-text">

            <strong>
              KDU Academic Intelligence
            </strong>

            <span>
              AI-Powered Academic Decision Support
            </span>

          </div>

        </Link>


        {/* =================================================
            DESKTOP NAVIGATION
            ================================================= */}

        <nav
          className="navbar-links"
          aria-label="Primary navigation"
        >

          {NAV_ITEMS.map((item) => (

            <a
              key={item.id}
              href={`/#${item.id}`}
              className={getNavLinkClass(item.id)}
              onClick={(event) =>
                handleNavClick(
                  event,
                  item.id,
                )
              }
            >
              {item.label}
            </a>

          ))}

        </nav>


        {/* =================================================
            DESKTOP ACTIONS
            ================================================= */}

        <div className="navbar-actions">

          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={
              darkMode
                ? 'Switch to light mode'
                : 'Switch to dark mode'
            }
            title={
              darkMode
                ? 'Switch to light mode'
                : 'Switch to dark mode'
            }
          >

            <span
              className="theme-icon"
              aria-hidden="true"
            >
              {darkMode ? '☀' : '☾'}
            </span>

            <span className="theme-label">
              {darkMode
                ? 'Light'
                : 'Dark'}
            </span>

          </button>


          <Link
            to="/login"
            className="navbar-login"
          >
            Login
          </Link>


          <Link
            to="/register"
            className="navbar-register"
          >
            Get Started
          </Link>

        </div>


        {/* =================================================
            MOBILE ACTIONS
            ================================================= */}

        <div className="mobile-actions">

          <button
            type="button"
            className="theme-toggle"
            onClick={toggleTheme}
            aria-label={
              darkMode
                ? 'Switch to light mode'
                : 'Switch to dark mode'
            }
          >

            <span
              className="theme-icon"
              aria-hidden="true"
            >
              {darkMode ? '☀' : '☾'}
            </span>

          </button>


          <button
            type="button"
            className={`menu-button ${
              mobileMenuOpen
                ? 'open'
                : ''
            }`}
            onClick={() =>
              setMobileMenuOpen(
                (previous) =>
                  !previous,
              )
            }
            aria-label={
              mobileMenuOpen
                ? 'Close navigation menu'
                : 'Open navigation menu'
            }
            aria-expanded={
              mobileMenuOpen
            }
            aria-controls="mobile-menu"
          >

            <span />
            <span />
            <span />

          </button>

        </div>

      </div>


      {/* =====================================================
          MOBILE MENU
          ===================================================== */}

      <div
        id="mobile-menu"
        className={`mobile-menu ${
          mobileMenuOpen
            ? 'mobile-menu-open'
            : ''
        }`}
      >

        <nav
          className="mobile-nav"
          aria-label="Mobile navigation"
        >

          {NAV_ITEMS.map((item) => (

            <a
              key={item.id}
              href={`/#${item.id}`}
              className={getMobileNavLinkClass(item.id)}
              onClick={(event) =>
                handleNavClick(
                  event,
                  item.id,
                )
              }
            >
              {item.label}
            </a>

          ))}


          <div className="mobile-menu-divider" />


          <Link
            to="/login"
            className="mobile-login"
            onClick={closeMobileMenu}
          >
            Login
          </Link>


          <Link
            to="/register"
            className="mobile-register"
            onClick={closeMobileMenu}
          >
            Get Started
          </Link>

        </nav>

      </div>

    </header>
  )
}

export default Navbar