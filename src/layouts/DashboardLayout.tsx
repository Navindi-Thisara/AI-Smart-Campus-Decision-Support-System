import { Outlet, useLocation } from 'react-router-dom'

import Navbar from '../components/Navbar'
import Sidebar from '../components/Sidebar'
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
        {!isStudentDashboard && <Sidebar />}

        <main
          className={`dashboard-main ${
            isStudentDashboard ? 'student-dashboard-main' : ''
          }`}
        >
          <Outlet />
        </main>
      </div>

      {/* Footer should appear on ALL dashboard pages */}
      <Footer />
    </div>
  )
}

export default DashboardLayout