import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import PublicLayout from './layouts/PublicLayout'
import DashboardLayout from './layouts/DashboardLayout'

import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'

import StudentDashboard from './pages/StudentDashboard'
import StaffDashboard from './pages/StaffDashboard'

import Dashboard from './pages/Dashboard'
import Prediction from './pages/Prediction'

import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* =====================================================
            PUBLIC WEBSITE
            ===================================================== */}

        <Route element={<PublicLayout />}>

          <Route
            path="/"
            element={<Home />}
          />

          <Route
            path="/login"
            element={<Login />}
          />

          <Route
            path="/register"
            element={<Register />}
          />

          <Route
            path="/forgot-password"
            element={<ForgotPassword />}
          />

          {/* Legacy section URLs */}

          <Route
            path="/about"
            element={
              <Navigate
                to="/#about"
                replace
              />
            }
          />

          <Route
            path="/services"
            element={
              <Navigate
                to="/#services"
                replace
              />
            }
          />

          <Route
            path="/contact"
            element={
              <Navigate
                to="/#contact"
                replace
              />
            }
          />

        </Route>


        {/* =====================================================
            APPLICATION
            ===================================================== */}

        <Route element={<DashboardLayout />}>

          <Route
            path="/student-dashboard"
            element={<StudentDashboard />}
          />

          <Route
            path="/staff-dashboard"
            element={<StaffDashboard />}
          />

          {/* Existing dashboard */}

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/prediction"
            element={<Prediction />}
          />

        </Route>


        {/* =====================================================
            FALLBACK
            ===================================================== */}

        <Route
          path="*"
          element={
            <Navigate
              to="/"
              replace
            />
          }
        />

      </Routes>
    </BrowserRouter>
  )
}

export default App