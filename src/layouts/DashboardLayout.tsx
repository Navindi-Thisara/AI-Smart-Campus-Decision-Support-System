import { Outlet, useLocation } from 'react-router-dom'

import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

import './DashboardLayout.css'

function DashboardLayout() {
  const location = useLocation()

  const isStudentDashboard =
    location.pathname === '/student-dashboard' ||
    location.pathname.startsWith('/student-dashboard/')

  return (
    <div
      className={`dashboard-layout ${
        isStudentDashboard ? 'student-dashboard-layout' : ''
      }`}
    >
      <Navbar />

      <div
        className={`dashboard-body ${
          isStudentDashboard ? 'student-dashboard-body' : ''
        }`}
      >
        <main
          className={`dashboard-main ${
            isStudentDashboard ? 'student-dashboard-main' : ''
          }`}
        >
          <Outlet />
        </main>
      </div>

      <Footer />
    </div>
  )
}

export default DashboardLayout