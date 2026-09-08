import {
  FormEvent,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from 'react'

import { Link } from 'react-router-dom'

import './StudentDashboard.css'

interface StoredUser {
  id: number
  fullName: string
  email: string
  studentId: string
  role: 'STUDENT' | 'STAFF'
}

interface Faculty {
  facultyId: string
  facultyName: string
}

interface Degree {
  degreeId: string
  degreeName: string
  facultyId: string
  facultyName?: string
  department: string
  durationYears: number
}

interface CourseModule {
  courseCode: string
  moduleName: string
  year: number
  semester: number
  credits: number
  moduleCategory: 'GPA' | 'NON_GPA'
  moduleType?: 'Core' | 'Elective'
}

interface StudentProfile {
  studentId: string
  intake: number | null
  facultyId: string | null
  degreeId: string | null
  currentYear: number | null
  currentSemester: number | null
}

interface GradeEntry {
  courseCode: string
  grade: string
  gradePoint: number | null
}

interface SemesterRecord {
  semester: number
  sgpa: number
  credits?: number
}

interface DashboardData {
  userId?: number
  profile: StudentProfile | null
  semesterRecords: SemesterRecord[]
  grades: Record<number, GradeEntry[]>
}

const API_BASE = (
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8080'
).replace(/\/$/, '')

const GRADE_OPTIONS = [
  { grade: 'A+', point: 4.0 },
  { grade: 'A', point: 4.0 },
  { grade: 'A-', point: 3.7 },
  { grade: 'B+', point: 3.3 },
  { grade: 'B', point: 3.0 },
  { grade: 'B-', point: 2.7 },
  { grade: 'C+', point: 2.3 },
  { grade: 'C', point: 2.0 },
  { grade: 'C-', point: 1.7 },
  { grade: 'D+', point: 1.3 },
  { grade: 'F', point: 0.0 },
  { grade: 'N/A', point: null },
]

const INTAKES = [39, 40, 41, 42]

const YEARS = [1, 2, 3, 4]

const SEMESTERS = [1, 2, 3, 4, 5, 6, 7, 8]

const semesterBelongsToYear = (
  semester: number,
  year: number,
): boolean => {
  return Math.ceil(semester / 2) === year
}

function getGradePoint(
  grade: string,
): number | null {
  const option = GRADE_OPTIONS.find(
    item => item.grade === grade,
  )

  return option?.point ?? null
}

function getInitials(
  name: string,
): string {
  const parts = name
    .trim()
    .split(/\s+/)
    .filter(Boolean)

  if (parts.length === 0) {
    return 'ST'
  }

  if (parts.length === 1) {
    return parts[0]
      .slice(0, 2)
      .toUpperCase()
  }

  return (
    parts[0].charAt(0) +
    parts[parts.length - 1].charAt(0)
  ).toUpperCase()
}

function formatGPA(
  value: number | null | undefined,
): string {
  if (
    value === null ||
    value === undefined ||
    Number.isNaN(value)
  ) {
    return '—'
  }

  return Number(value).toFixed(4)
}

function isValidSemester(
  semester: number,
): boolean {
  return SEMESTERS.includes(semester)
}

function getMaxSemesterForYear(
  year: number,
): number {
  return year * 2
}

function getFirstSemesterForYear(
  year: number,
): number {
  return year * 2 - 1
}

async function apiRequest<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  let response: Response

  try {
    response = await fetch(
      `${API_BASE}${path}`,
      {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(options?.headers || {}),
        },
      },
    )
  } catch {
    throw new Error(
      `Unable to connect to the backend at ${API_BASE}. ` +
      'Make sure Spring Boot is running and CORS is configured correctly.',
    )
  }

  if (!response.ok) {
    let message =
      `Request failed (${response.status})`

    try {
      const errorBody =
        await response.json()

      if (
        typeof errorBody === 'string'
      ) {
        message = errorBody
      } else {
        message =
          errorBody.message ||
          errorBody.error ||
          errorBody.detail ||
          message
      }
    } catch {
      // Keep default message.
    }

    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  const text =
    await response.text()

  if (!text.trim()) {
    return undefined as T
  }

  try {
    return JSON.parse(text) as T
  } catch {
    return text as T
  }
}

type UnknownRecord =
  Record<string, unknown>

function getArrayPayload(
  value: unknown,
): unknown[] {
  if (Array.isArray(value)) {
    return value
  }

  if (
    value &&
    typeof value === 'object'
  ) {
    const record =
      value as UnknownRecord

    const candidates = [
      record.data,
      record.content,
      record.items,
      record.results,
      record.faculties,
      record.degrees,
    ]

    const found =
      candidates.find(
        candidate =>
          Array.isArray(candidate),
      )

    if (Array.isArray(found)) {
      return found
    }
  }

  return []
}

function normalizeFacultyList(
  payload: unknown,
): Faculty[] {
  const seen =
    new Set<string>()

  return getArrayPayload(payload)
    .map(item => {
      if (
        !item ||
        typeof item !== 'object'
      ) {
        return null
      }

      const record =
        item as UnknownRecord

      const rawId =
        record.facultyId ??
        record.facultyID ??
        record.faculty_id ??
        record.id ??
        record.code

      const rawName =
        record.facultyName ??
        record.faculty_name ??
        record.name ??
        record.title

      const facultyId =
        rawId == null
          ? ''
          : String(rawId).trim()

      const facultyName =
        rawName == null
          ? ''
          : String(rawName).trim()

      if (
        !facultyId ||
        !facultyName ||
        seen.has(facultyId)
      ) {
        return null
      }

      seen.add(facultyId)

      return {
        facultyId,
        facultyName,
      }
    })
    .filter(
      (
        faculty,
      ): faculty is Faculty =>
        faculty !== null,
    )
}

function normalizeDegreeList(
  payload: unknown,
): Degree[] {
  return getArrayPayload(payload)
    .map(item => {
      if (
        !item ||
        typeof item !== 'object'
      ) {
        return null
      }

      const record =
        item as UnknownRecord

      const rawDegreeId =
        record.degreeId ??
        record.degreeID ??
        record.degree_id ??
        record.id ??
        record.code

      const rawFacultyId =
        record.facultyId ??
        record.facultyID ??
        record.faculty_id ??
        (
          record.faculty &&
          typeof record.faculty === 'object'
            ? (
                record.faculty as UnknownRecord
              ).facultyId ??
              (
                record.faculty as UnknownRecord
              ).id
            : undefined
        )

      const rawDegreeName =
        record.degreeName ??
        record.degree_name ??
        record.name ??
        record.title

      const degreeId =
        rawDegreeId == null
          ? ''
          : String(rawDegreeId).trim()

      const facultyId =
        rawFacultyId == null
          ? ''
          : String(rawFacultyId).trim()

      const degreeName =
        rawDegreeName == null
          ? ''
          : String(rawDegreeName).trim()

      if (
        !degreeId ||
        !degreeName
      ) {
        return null
      }

      const rawFacultyName =
        record.facultyName ??
        record.faculty_name ??
        (
          record.faculty &&
          typeof record.faculty === 'object'
            ? (
                record.faculty as UnknownRecord
              ).facultyName ??
              (
                record.faculty as UnknownRecord
              ).name
            : undefined
        )

      return {
        degreeId,
        degreeName,
        facultyId,
        facultyName:
          rawFacultyName == null
            ? undefined
            : String(
                rawFacultyName,
              ).trim(),
        department: String(
          record.department ?? '',
        ),
        durationYears: Number(
          record.durationYears ??
          record.duration_years ??
          record.duration ??
          0,
        ),
      }
    })
    .filter(
      (
        degree,
      ): degree is Degree =>
        degree !== null,
    )
}

function facultiesFromDegrees(
  degreeList: Degree[],
): Faculty[] {
  const facultyIds =
    Array.from(
      new Set(
        degreeList
          .map(degree =>
            String(
              degree.facultyId || '',
            ).trim(),
          )
          .filter(Boolean),
      ),
    )

  return facultyIds.map(id => {
    const matchingDegree =
      degreeList.find(
        degree =>
          String(
            degree.facultyId,
          ) === id,
      )

    return {
      facultyId: id,
      facultyName:
        matchingDegree?.facultyName ||
        id,
    }
  })
}

function normalizeSemesterRecords(
  value: unknown,
): SemesterRecord[] {
  let items: unknown[] = []

  if (Array.isArray(value)) {
    items = value
  } else if (
    value &&
    typeof value === 'object'
  ) {
    const record =
      value as UnknownRecord

    const arrayValue =
      getArrayPayload(value)

    if (arrayValue.length > 0) {
      items = arrayValue
    } else {
      items =
        Object.entries(record)
          .map(
            ([semester, sgpa]) => ({
              semester,
              sgpa,
            }),
          )
    }
  }

  return items
    .map(item => {
      if (
        !item ||
        typeof item !== 'object'
      ) {
        return null
      }

      const record =
        item as UnknownRecord

      const semesterRaw =
        record.semester ??
        record.semesterNumber ??
        record.semester_no ??
        record.Semester ??
        record.sem

      const sgpaRaw =
        record.sgpa ??
        record.SGPA ??
        record.sgpaValue ??
        record.gpa ??
        record.GPA

      const semester =
        Number(semesterRaw)

      const sgpa =
        Number(sgpaRaw)

      if (
        !Number.isInteger(semester) ||
        !isValidSemester(semester)
      ) {
        return null
      }

      if (
        !Number.isFinite(sgpa) ||
        sgpa < 0 ||
        sgpa > 4
      ) {
        return null
      }

      return {
        semester,
        sgpa: Number(
          sgpa.toFixed(4),
        ),
        credits:
          record.credits == null
            ? undefined
            : Number(record.credits),
      }
    })
    .filter(
      (
        record,
      ): record is SemesterRecord =>
        record !== null,
    )
    .sort(
      (a, b) =>
        a.semester - b.semester,
    )
}

function normalizeGradeMap(
  value: unknown,
): Record<number, GradeEntry[]> {
  if (
    !value ||
    typeof value !== 'object'
  ) {
    return {}
  }

  const source =
    value as UnknownRecord

  const result:
    Record<number, GradeEntry[]> = {}

  Object.entries(source)
    .forEach(
      ([key, rawEntries]) => {
        const semester =
          Number(key)

        if (
          !isValidSemester(semester)
        ) {
          return
        }

        const entries =
          getArrayPayload(rawEntries)
            .map(item => {
              if (
                !item ||
                typeof item !== 'object'
              ) {
                return null
              }

              const record =
                item as UnknownRecord

              const courseCode =
                String(
                  record.courseCode ??
                  record.course_code ??
                  record.Course_Code ??
                  '',
                ).trim()

              const grade =
                String(
                  record.grade ??
                  record.Grade ??
                  '',
                ).trim()

              if (!courseCode) {
                return null
              }

              const rawPoint =
                record.gradePoint ??
                record.grade_point

              const parsedPoint =
                rawPoint == null
                  ? null
                  : Number(rawPoint)

              return {
                courseCode,
                grade,
                gradePoint:
                  Number.isFinite(
                    parsedPoint,
                  )
                    ? parsedPoint
                    : getGradePoint(
                        grade,
                      ),
              }
            })
            .filter(
              (
                entry,
              ): entry is GradeEntry =>
                entry !== null,
            )

        result[semester] =
          entries
      },
    )

  return result
}

function normalizeDashboardData(
  payload: unknown,
): DashboardData {
  const record =
    payload &&
    typeof payload === 'object'
      ? (
          payload as UnknownRecord
        )
      : {}

  const rawRecords =
    record.semesterRecords ??
    record.semesterGpas ??
    record.semesterGPAs ??
    record.sgpAs ??
    record.sgpaRecords ??
    record.gpaRecords ??
    []

  const rawGrades =
    record.grades ??
    record.results ??
    record.semesterGrades ??
    {}

  return {
    userId:
      typeof record.userId === 'number'
        ? record.userId
        : undefined,

    profile:
      (
        record.profile as
          | StudentProfile
          | null
          | undefined
      ) ?? null,

    semesterRecords:
      normalizeSemesterRecords(
        rawRecords,
      ),

    grades:
      normalizeGradeMap(
        rawGrades,
      ),
  }
}

function Icon({
  name,
}: {
  name:
    | 'book'
    | 'chart'
    | 'brain'
    | 'spark'
    | 'shield'
    | 'save'
    | 'edit'
    | 'arrow'
    | 'check'
    | 'info'
    | 'user'
    | 'graduation'
    | 'calendar'
    | 'refresh'
}) {
  const paths:
    Record<
      string,
      React.ReactNode
    > = {
      book: (
        <>
          <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v15H6.5A2.5 2.5 0 0 0 4 20.5z" />
          <path d="M4 5.5v15A2.5 2.5 0 0 1 6.5 18H20" />
        </>
      ),

      chart: (
        <>
          <path d="M4 19V5" />
          <path d="M4 19h16" />
          <path d="m7 15 3-4 3 2 5-7" />
        </>
      ),

      brain: (
        <>
          <path d="M9.5 4.5a3.5 3.5 0 0 0-6 2.5 3.5 3.5 0 0 0 0 5.5A3.5 3.5 0 0 0 6 18a3.5 3.5 0 0 0 6 1.5" />
          <path d="M14.5 4.5a3.5 3.5 0 0 1 6 2.5 3.5 3.5 0 0 1 0 5.5A3.5 3.5 0 0 1 18 18a3.5 3.5 0 0 1-6 1.5" />
          <path d="M12 3v18M8 8h4M8 13h4M12 10h4M12 16h4" />
        </>
      ),

      spark: (
        <>
          <path d="m12 2 1.8 6.2L20 10l-6.2 1.8L12 18l-1.8-6.2L4 10l6.2-1.8z" />
          <path d="m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8z" />
        </>
      ),

      shield: (
        <>
          <path d="M12 3 20 6v5c0 5-3.2 8.5-8 10-4.8-1.5-8-5-8-10V6z" />
          <path d="m8.5 12 2.2 2.2 4.8-5" />
        </>
      ),

      save: (
        <>
          <path d="M5 3h11l3 3v15H5z" />
          <path d="M8 3v6h8V3M8 21v-7h8v7" />
        </>
      ),

      edit: (
        <>
          <path d="M4 20h4L19 9l-4-4L4 16z" />
          <path d="m13.5 6.5 4 4" />
        </>
      ),

      arrow: (
        <>
          <path d="M5 12h14" />
          <path d="m13 6 6 6-6 6" />
        </>
      ),

      check: (
        <>
          <circle
            cx="12"
            cy="12"
            r="9"
          />
          <path d="m8 12 2.5 2.5L16 9" />
        </>
      ),

      info: (
        <>
          <circle
            cx="12"
            cy="12"
            r="9"
          />
          <path d="M12 10v6M12 7.5v.2" />
        </>
      ),

      user: (
        <>
          <circle
            cx="12"
            cy="8"
            r="3.5"
          />
          <path d="M5 21a7 7 0 0 1 14 0" />
        </>
      ),

      graduation: (
        <>
          <path d="m3 9 9-5 9 5-9 5z" />
          <path d="M7 11v5c2.5 2 5 3 10 0v-5" />
          <path d="M21 10v5" />
        </>
      ),

      calendar: (
        <>
          <rect
            x="4"
            y="5"
            width="16"
            height="16"
            rx="2"
          />
          <path d="M8 3v4M16 3v4M4 10h16" />
        </>
      ),

      refresh: (
        <>
          <path d="M20 11a8 8 0 0 0-14.7-4L4 9" />
          <path d="M4 4v5h5" />
          <path d="M4 13a8 8 0 0 0 14.7 4L20 15" />
          <path d="M20 20v-5h-5" />
        </>
      ),
    }

  return (
    <svg
      className="sd-icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths[name]}
    </svg>
  )
}

function StudentDashboard() {
  /* -------------------------------------------------------
     USER
     ------------------------------------------------------- */

  const [user, setUser] =
    useState<StoredUser | null>(null)

  /* -------------------------------------------------------
     REFERENCE DATA
     ------------------------------------------------------- */

  const [faculties, setFaculties] =
    useState<Faculty[]>([])

  const [degrees, setDegrees] =
    useState<Degree[]>([])

  const [
    loadingReferenceData,
    setLoadingReferenceData,
  ] = useState(true)

  const [
    referenceError,
    setReferenceError,
  ] = useState('')

  /* -------------------------------------------------------
     PROFILE
     ------------------------------------------------------- */

  const [profile, setProfile] =
    useState<StudentProfile | null>(
      null,
    )

  const [intake, setIntake] =
    useState<number | ''>('')

  const [facultyId, setFacultyId] =
    useState('')

  const [degreeId, setDegreeId] =
    useState('')

  const [currentYear, setCurrentYear] =
    useState<number | ''>('')

  const [
    currentSemester,
    setCurrentSemester,
  ] = useState<number | ''>('')

  /* -------------------------------------------------------
     MODULES
     ------------------------------------------------------- */

  const [
    modulesBySemester,
    setModulesBySemester,
  ] = useState<
    Record<number, CourseModule[]>
  >({})

  const [
    loadingModules,
    setLoadingModules,
  ] = useState(false)

  /* -------------------------------------------------------
     GRADES
     ------------------------------------------------------- */

  const [grades, setGrades] =
    useState<
      Record<number, GradeEntry[]>
    >({})

  const [
    selectedGradeSemester,
    setSelectedGradeSemester,
  ] = useState<number>(1)

  /* -------------------------------------------------------
     SGPA
     ------------------------------------------------------- */

  const [sgpaValues, setSgpaValues] =
    useState<
      Record<number, string>
    >({})

  const [
    semesterRecords,
    setSemesterRecords,
  ] = useState<SemesterRecord[]>([])

  /* -------------------------------------------------------
     UI
     ------------------------------------------------------- */

  const [loading, setLoading] =
    useState(true)

  const [
    savingProfile,
    setSavingProfile,
  ] = useState(false)

  const [
    savingGrades,
    setSavingGrades,
  ] = useState(false)

  const [
    savingSGPA,
    setSavingSGPA,
  ] = useState(false)

  const [
    savingSGPASemester,
    setSavingSGPASemester,
  ] = useState<number | null>(
    null,
  )

  const [
    profileOpen,
    setProfileOpen,
  ] = useState(false)

  const [message, setMessage] =
    useState('')

  const [error, setError] =
    useState('')

  /* =======================================================
     LOAD USER
     ======================================================= */

  useEffect(() => {
    const storedUser =
      localStorage.getItem('user')

    if (!storedUser) {
      setLoading(false)
      return
    }

    try {
      const parsed =
        JSON.parse(
          storedUser,
        ) as StoredUser

      setUser(parsed)
    } catch {
      setUser(null)
      setLoading(false)
    }
  }, [])

  const studentId =
    user?.studentId || ''

  /* =======================================================
     LOAD REFERENCE DATA
     ======================================================= */

  const loadReferenceData =
    useCallback(
      async () => {
        setLoadingReferenceData(
          true,
        )

        setReferenceError('')

        const [
          facultyResult,
          degreeResult,
        ] =
          await Promise.allSettled([
            apiRequest<unknown>(
              '/api/reference/faculties',
            ),
            apiRequest<unknown>(
              '/api/reference/degrees',
            ),
          ])

        let nextFaculties:
          Faculty[] = []

        let nextDegrees:
          Degree[] = []

        if (
          degreeResult.status ===
          'fulfilled'
        ) {
          nextDegrees =
            normalizeDegreeList(
              degreeResult.value,
            )

          setDegrees(
            nextDegrees,
          )
        } else {
          setDegrees([])
        }

        if (
          facultyResult.status ===
          'fulfilled'
        ) {
          nextFaculties =
            normalizeFacultyList(
              facultyResult.value,
            )
        }

        if (
          nextFaculties.length ===
            0 &&
          nextDegrees.length > 0
        ) {
          nextFaculties =
            facultiesFromDegrees(
              nextDegrees,
            )
        }

        setFaculties(
          nextFaculties,
        )

        const errors: string[] = []

        if (
          facultyResult.status ===
          'rejected'
        ) {
          errors.push(
            facultyResult.reason instanceof
              Error
              ? `Faculty request: ${facultyResult.reason.message}`
              : 'Faculty request failed.',
          )
        }

        if (
          degreeResult.status ===
          'rejected'
        ) {
          errors.push(
            degreeResult.reason instanceof
              Error
              ? `Degree request: ${degreeResult.reason.message}`
              : 'Degree request failed.',
          )
        }

        if (
          nextFaculties.length ===
          0
        ) {
          errors.push(
            'No faculty records were returned by the reference API.',
          )
        }

        if (errors.length > 0) {
          setReferenceError(
            errors.join(' '),
          )
        }

        setLoadingReferenceData(
          false,
        )
      },
      [],
    )

  useEffect(() => {
    loadReferenceData()
  }, [loadReferenceData])

  /* =======================================================
     APPLY PROFILE LOCALLY
     ======================================================= */

  const applyProfile =
    useCallback(
      (
        loadedProfile:
          | StudentProfile
          | null,
      ) => {
        setProfile(
          loadedProfile,
        )

        if (!loadedProfile) {
          setIntake('')
          setFacultyId('')
          setDegreeId('')
          setCurrentYear('')
          setCurrentSemester('')
          return
        }

        setIntake(
          loadedProfile.intake ??
            '',
        )

        setFacultyId(
          loadedProfile.facultyId ??
            '',
        )

        setDegreeId(
          loadedProfile.degreeId ??
            '',
        )

        setCurrentYear(
          loadedProfile.currentYear ??
            '',
        )

        setCurrentSemester(
          loadedProfile.currentSemester ??
            '',
        )
      },
      [],
    )

  /* =======================================================
     LOAD DASHBOARD
     ======================================================= */

  const loadDashboard =
    useCallback(
      async () => {
        if (!studentId) {
          setLoading(false)
          return
        }

        setLoading(true)
        setError('')

        try {
          const rawData =
            await apiRequest<unknown>(
              `/api/students/dashboard?studentId=${encodeURIComponent(
                studentId,
              )}`,
            )

          const data =
            normalizeDashboardData(
              rawData,
            )

          applyProfile(
            data.profile,
          )

          /*
           * HARD RULE:
           *
           * A student can only have/view
           * academic records up to their
           * CURRENT semester.
           */
          const loadedCurrentSemester =
            data.profile?.currentSemester

          /* -------------------------------------------------
             SEMESTER RECORDS
             ------------------------------------------------- */

          const normalizedRecords =
            data.semesterRecords
              .filter(record =>
                isValidSemester(
                  record.semester,
                ),
              )
              .filter(record =>
                loadedCurrentSemester == null ||
                Number(record.semester) <=
                  Number(
                    loadedCurrentSemester,
                  ),
              )
              .sort(
                (a, b) =>
                  a.semester -
                  b.semester,
              )

          setSemesterRecords(
            normalizedRecords,
          )

          /* -------------------------------------------------
             SGPA VALUES
             ------------------------------------------------- */

          const sgpaMap:
            Record<number, string> =
            {}

          normalizedRecords.forEach(
            record => {
              sgpaMap[
                record.semester
              ] = Number(
                record.sgpa,
              ).toFixed(4)
            },
          )

          setSgpaValues(
            sgpaMap,
          )

          /* -------------------------------------------------
             GRADES
             ------------------------------------------------- */

          const loadedGrades =
            data.grades || {}

          const filteredGrades:
            Record<
              number,
              GradeEntry[]
            > = {}

          Object.entries(
            loadedGrades,
          ).forEach(
            ([semesterKey, entries]) => {
              const semester =
                Number(semesterKey)

              if (
                !isValidSemester(
                  semester,
                )
              ) {
                return
              }

              if (
                loadedCurrentSemester !=
                  null &&
                semester >
                  Number(
                    loadedCurrentSemester,
                  )
              ) {
                return
              }

              filteredGrades[
                semester
              ] = entries
            },
          )

          setGrades(
            filteredGrades,
          )

          /* -------------------------------------------------
             SELECT GRADE SEMESTER
             ------------------------------------------------- */

          const semestersWithGrades =
            Object.keys(
              filteredGrades,
            )
              .map(Number)
              .filter(
                semester =>
                  filteredGrades[
                    semester
                  ]?.length > 0,
              )
              .sort(
                (a, b) => a - b,
              )

          if (
            semestersWithGrades.length >
            0
          ) {
            const latestGradeSemester =
              semestersWithGrades.at(
                -1,
              )!

            const allowedLatest =
              loadedCurrentSemester !=
              null
                ? Math.min(
                    latestGradeSemester,
                    Number(
                      loadedCurrentSemester,
                    ),
                  )
                : latestGradeSemester

            setSelectedGradeSemester(
              allowedLatest,
            )
          } else if (
            loadedCurrentSemester !=
              null &&
            Number(
              loadedCurrentSemester,
            ) > 0
          ) {
            setSelectedGradeSemester(
              Number(
                loadedCurrentSemester,
              ),
            )
          } else {
            setSelectedGradeSemester(1)
          }
        } catch (err) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load student dashboard.',
          )
        } finally {
          setLoading(false)
        }
      },
      [
        studentId,
        applyProfile,
      ],
    )

  useEffect(() => {
    loadDashboard()
  }, [loadDashboard])

  /* =======================================================
     FILTER DEGREES
     ======================================================= */

  const filteredDegrees =
    useMemo(() => {
      if (!facultyId) {
        return degrees
      }

      return degrees.filter(
        degree =>
          String(
            degree.facultyId,
          ) ===
          String(facultyId),
      )
    }, [degrees, facultyId])

  /* =======================================================
     SELECTED FACULTY / DEGREE
     ======================================================= */

  const selectedFaculty =
    useMemo(
      () =>
        faculties.find(
          faculty =>
            String(
              faculty.facultyId,
            ) ===
            String(facultyId),
        ),
      [faculties, facultyId],
    )

  const selectedDegree =
    useMemo(
      () =>
        degrees.find(
          degree =>
            String(
              degree.degreeId,
            ) ===
            String(degreeId),
        ),
      [degrees, degreeId],
    )

  /* =======================================================
     PROFILE VALIDATION
     ======================================================= */

  const profileComplete =
    Boolean(
      studentId &&
        intake &&
        facultyId &&
        degreeId &&
        currentYear &&
        currentSemester,
    )

  
  const maxDegreeYear =
    selectedDegree?.durationYears
      ? Math.min(
          selectedDegree.durationYears,
          4,
        )
      : 4

  const availableYears =
    YEARS.filter(
      year =>
        year <= maxDegreeYear,
    )

  
  const availableSemesters =
    typeof currentYear ===
    'number'
      ? SEMESTERS.filter(
          semester =>
            semesterBelongsToYear(
              semester,
              currentYear,
            ),
        )
      : []

  /* =======================================================
     LOAD MODULES
     ======================================================= */

  const loadModules =
    useCallback(
      async (
        selectedDegreeId: string,
        semester: number,
      ) => {
        if (
          !selectedDegreeId ||
          !isValidSemester(
            semester,
          )
        ) {
          return []
        }

        setLoadingModules(true)
        setError('')

        try {
          const moduleData =
            await apiRequest<
              CourseModule[]
            >(
              `/api/reference/degrees/${encodeURIComponent(
                selectedDegreeId,
              )}/semesters/${semester}/modules`,
            )

          const normalizedModules =
            Array.isArray(
              moduleData,
            )
              ? moduleData
              : []

          setModulesBySemester(
            previous => ({
              ...previous,
              [semester]:
                normalizedModules,
            }),
          )

          return normalizedModules
        } catch (err) {
          setError(
            err instanceof Error
              ? err.message
              : `Unable to load modules for Semester ${semester}.`,
          )

          return []
        } finally {
          setLoadingModules(
            false,
          )
        }
      },
      [],
    )

  /*
   * Load all semester modules when
   * degree changes.
   *
   * This intentionally does NOT depend
   * on modulesBySemester.
   */
  useEffect(() => {
    if (!degreeId) {
      setModulesBySemester({})
      return
    }

    let cancelled = false

    const loadAll =
      async () => {
        setLoadingModules(true)

        const results =
          await Promise.all(
            SEMESTERS.map(
              async semester => {
                try {
                  const data =
                    await apiRequest<
                      CourseModule[]
                    >(
                      `/api/reference/degrees/${encodeURIComponent(
                        degreeId,
                      )}/semesters/${semester}/modules`,
                    )

                  return [
                    semester,
                    Array.isArray(data)
                      ? data
                      : [],
                  ] as const
                } catch {
                  return [
                    semester,
                    [],
                  ] as const
                }
              },
            ),
          )

        if (!cancelled) {
          setModulesBySemester(
            Object.fromEntries(
              results,
            ),
          )

          setLoadingModules(
            false,
          )
        }
      }

    loadAll()

    return () => {
      cancelled = true
    }
  }, [degreeId])

  

  const handleFacultyChange =
    (value: string) => {
      setFacultyId(value)

      setDegreeId('')

      setModulesBySemester({})

      setCurrentYear('')
      setCurrentSemester('')
    }

  const handleDegreeChange =
    (value: string) => {
      setDegreeId(value)

      setModulesBySemester({})

      setCurrentYear('')
      setCurrentSemester('')
    }

  const handleYearChange =
    (value: string) => {
      const year =
        value
          ? Number(value)
          : ''

      setCurrentYear(year)

      if (
        typeof year ===
          'number' &&
        currentSemester &&
        !semesterBelongsToYear(
          Number(
            currentSemester,
          ),
          year,
        )
      ) {
        setCurrentSemester('')
      }
    }

  const handleSemesterChange =
    (value: string) => {
      const semester =
        value
          ? Number(value)
          : ''

      if (
        typeof semester ===
          'number' &&
        typeof currentYear ===
          'number' &&
        !semesterBelongsToYear(
          semester,
          currentYear,
        )
      ) {
        setError(
          `Semester ${semester} does not belong to Year ${currentYear}.`,
        )
        return
      }

      setCurrentSemester(
        semester,
      )

      if (
        typeof semester ===
          'number' &&
        degreeId
      ) {
        loadModules(
          degreeId,
          semester,
        )
      }
    }

  /* =======================================================
     SAVE PROFILE
     ======================================================= */

  const handleSaveProfile =
    async (
      event: FormEvent,
    ) => {
      event.preventDefault()

      setError('')
      setMessage('')

      if (!studentId) {
        setError(
          'Student account information is missing. Please log in again.',
        )
        return
      }

      if (
        !intake ||
        !facultyId ||
        !degreeId ||
        !currentYear ||
        !currentSemester
      ) {
        setError(
          'Please complete Faculty, Degree, Intake, Year and Semester.',
        )
        return
      }

      const numericYear =
        Number(currentYear)

      const numericSemester =
        Number(currentSemester)

      if (
        !availableYears.includes(
          numericYear,
        )
      ) {
        setError(
          'The selected year is outside the selected degree duration.',
        )
        return
      }

      if (
        !semesterBelongsToYear(
          numericSemester,
          numericYear,
        )
      ) {
        setError(
          `Semester ${numericSemester} does not belong to Year ${numericYear}.`,
        )
        return
      }

      setSavingProfile(true)

      try {
        const savedProfile =
          await apiRequest<StudentProfile>(
            `/api/students/profile?studentId=${encodeURIComponent(
              studentId,
            )}`,
            {
              method: 'PUT',
              body: JSON.stringify({
                studentId,
                intake: Number(intake),
                facultyId,
                degreeId,
                currentYear: numericYear,
                currentSemester: numericSemester,
              }),
            },
          )

        /*
         * Immediately use the exact
         * response from the backend.
         */
        const normalizedSavedProfile:
          StudentProfile = {
          studentId:
            savedProfile.studentId ||
            studentId,

          intake:
            savedProfile.intake ??
            Number(intake),

          facultyId:
            savedProfile.facultyId ??
            facultyId,

          degreeId:
            savedProfile.degreeId ??
            degreeId,

          currentYear:
            savedProfile.currentYear ??
            numericYear,

          currentSemester:
            savedProfile.currentSemester ??
            numericSemester,
        }

        applyProfile(
          normalizedSavedProfile,
        )


        setSemesterRecords(
          previous =>
            previous.filter(
              record =>
                record.semester <=
                numericSemester,
            ),
        )

       
        setSgpaValues(
          previous => {
            const next: Record<
              number,
              string
            > = {}

            Object.entries(
              previous,
            ).forEach(
              ([semesterKey, value]) => {
                const semester =
                  Number(semesterKey)

                if (
                  semester <=
                  numericSemester
                ) {
                  next[semester] =
                    value
                }
              },
            )

            return next
          },
        )

        
        setGrades(
          previous => {
            const next: Record<
              number,
              GradeEntry[]
            > = {}

            Object.entries(
              previous,
            ).forEach(
              ([semesterKey, entries]) => {
                const semester =
                  Number(semesterKey)

                if (
                  semester <=
                  numericSemester
                ) {
                  next[semester] =
                    entries
                }
              },
            )

            return next
          },
        )

       
        setModulesBySemester({})

        
        setSelectedGradeSemester(
          numericSemester,
        )

        
        await loadModules(
          normalizedSavedProfile.degreeId ||
            degreeId,
          normalizedSavedProfile.currentSemester ||
            numericSemester,
        )

        setMessage(
          `Academic profile saved successfully: Year ${numericYear}, Semester ${numericSemester}.`,
        )

       
        setProfileOpen(false)
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to save academic profile.',
        )
      } finally {
        setSavingProfile(false)
      }
    }

  /* =======================================================
     GRADE SEMESTER
     ======================================================= */

  const maximumAllowedSemester =
    typeof currentSemester ===
    'number'
      ? currentSemester
      : 0

 
  useEffect(() => {
    if (
      maximumAllowedSemester > 0 &&
      selectedGradeSemester >
        maximumAllowedSemester
    ) {
      setSelectedGradeSemester(
        maximumAllowedSemester,
      )
    }
  }, [
    maximumAllowedSemester,
    selectedGradeSemester,
  ])

  const handleGradeSemesterChange =
    async (
      semester: number,
    ) => {
      
      if (
        !degreeId ||
        semester >
          maximumAllowedSemester
      ) {
        return
      }

      setSelectedGradeSemester(
        semester,
      )

      await loadModules(
        degreeId,
        semester,
      )
    }

  /* =======================================================
     SELECTED MODULES
     ======================================================= */

  const selectedSemesterModules =
    useMemo(() => {
      if (
        !degreeId ||
        !selectedGradeSemester
      ) {
        return []
      }

      return (
        modulesBySemester[
          selectedGradeSemester
        ] || []
      )
    }, [
      degreeId,
      selectedGradeSemester,
      modulesBySemester,
    ])

  /* =======================================================
     GRADE UPDATE
     ======================================================= */

  const updateGrade = (
    semester: number,
    courseCode: string,
    grade: string,
  ) => {
    
    if (
      semester >
      maximumAllowedSemester
    ) {
      return
    }

    setGrades(previous => {
      const semesterGrades = [
        ...(previous[semester] ||
          []),
      ]

      const existingIndex =
        semesterGrades.findIndex(
          entry =>
            entry.courseCode ===
            courseCode,
        )

      const nextEntry:
        GradeEntry = {
        courseCode,
        grade,
        gradePoint:
          getGradePoint(
            grade,
          ),
      }

      if (
        existingIndex >= 0
      ) {
        semesterGrades[
          existingIndex
        ] = nextEntry
      } else {
        semesterGrades.push(
          nextEntry,
        )
      }

      return {
        ...previous,
        [semester]:
          semesterGrades,
      }
    })
  }

  const getGradeForCourse = (
    semester: number,
    courseCode: string,
  ) => {
    return (
      grades[semester]?.find(
        entry =>
          entry.courseCode ===
          courseCode,
      )?.grade || ''
    )
  }

  /* =======================================================
     SAVE GRADES
     ======================================================= */

  const handleSaveGrades =
    async () => {
      if (
        !studentId ||
        !degreeId ||
        !selectedGradeSemester
      ) {
        setError(
          'Please complete your academic profile first.',
        )
        return
      }

      if (
        selectedGradeSemester >
        maximumAllowedSemester
      ) {
        setError(
          `You cannot save grades for Semester ${selectedGradeSemester}. Your current semester is Semester ${maximumAllowedSemester}.`,
        )
        return
      }

      const semesterGrades =
        grades[
          selectedGradeSemester
        ] || []

      if (
        semesterGrades.length ===
        0
      ) {
        setError(
          'Please enter at least one module grade.',
        )
        return
      }

      setSavingGrades(true)
      setError('')
      setMessage('')

      try {
        await apiRequest(
        `/api/students/results?studentId=${encodeURIComponent(studentId)}`,
        {
          method: 'PUT',
          body: JSON.stringify({
            studentId,
            degreeId,
            semester: selectedGradeSemester,
            grades: semesterGrades,
          }),
        },
      )

        setMessage(
          `Semester ${selectedGradeSemester} grades saved successfully.`,
        )

        
        await loadDashboard()

        
        setSelectedGradeSemester(
          Math.min(
            selectedGradeSemester,
            maximumAllowedSemester,
          ),
        )
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to save grades.',
        )
      } finally {
        setSavingGrades(false)
      }
    }

  /* =======================================================
     SGPA UPDATE
     ======================================================= */

  const handleSGPAChange = (
    semester: number,
    value: string,
  ) => {
   
    if (
      maximumAllowedSemester > 0 &&
      semester >
        maximumAllowedSemester
    ) {
      return
    }

    
    if (
      value !== '' &&
      !/^\d*\.?\d{0,4}$/.test(
        value,
      )
    ) {
      return
    }

    setSgpaValues(
      previous => ({
        ...previous,
        [semester]:
          value,
      }),
    )
  }

  /* =======================================================
     SAVE SGPA
     ======================================================= */

  const handleSaveSGPA =
    async (
      semester: number,
    ) => {
      
      if (
        maximumAllowedSemester <=
        0
      ) {
        setError(
          'Please save your academic profile first.',
        )
        return
      }

      if (
        semester >
        maximumAllowedSemester
      ) {
        setError(
          `You cannot save SGPA for Semester ${semester}. Your current semester is Semester ${maximumAllowedSemester}.`,
        )
        return
      }

      
      if (
        typeof currentYear ===
          'number' &&
        !semesterBelongsToYear(
          semester,
          currentYear,
        )
      ) {
        setError(
          `Semester ${semester} does not belong to Year ${currentYear}.`,
        )
        return
      }

      const rawValue =
        sgpaValues[semester]

      if (
        rawValue === undefined ||
        rawValue.trim() === ''
      ) {
        setError(
          `Please enter an SGPA for Semester ${semester}.`,
        )
        return
      }

      const sgpa =
        Number(rawValue)

      if (
        !Number.isFinite(sgpa) ||
        sgpa < 0 ||
        sgpa > 4
      ) {
        setError(
          'SGPA must be between 0.0000 and 4.0000.',
        )
        return
      }

      const roundedSGPA =
        Number(
          sgpa.toFixed(4),
        )

      setSavingSGPA(true)
      setSavingSGPASemester(
        semester,
      )
      setError('')
      setMessage('')

      try {
        await apiRequest(
          `/api/students/sgpa?studentId=${encodeURIComponent(
            studentId,
          )}`,
          {
            method: 'PUT',
            body: JSON.stringify({
              studentId,
              semester,
              sgpa: roundedSGPA,
            }),
          },
        )

        /*
         * Update local semester records
         * immediately.
         */
        setSemesterRecords(
          previous => {
            const existing =
              previous.find(
                record =>
                  record.semester ===
                  semester,
              )

            if (existing) {
              return previous
                .map(record =>
                  record.semester ===
                  semester
                    ? {
                        ...record,
                        sgpa:
                          roundedSGPA,
                      }
                    : record,
                )
                .sort(
                  (a, b) =>
                    a.semester -
                    b.semester,
                )
            }

            return [
              ...previous,
              {
                semester,
                sgpa:
                  roundedSGPA,
              },
            ].sort(
              (a, b) =>
                a.semester -
                b.semester,
            )
          },
        )

        setSgpaValues(
          previous => ({
            ...previous,
            [semester]:
              String(
                roundedSGPA,
              ),
          }),
        )

        setMessage(
          `Semester ${semester} SGPA saved successfully.`,
        )

       
        await loadDashboard()

        
        setSelectedGradeSemester(
          Math.min(
            semester,
            maximumAllowedSemester,
          ),
        )
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : 'Unable to save SGPA.',
        )
      } finally {
        setSavingSGPA(false)
        setSavingSGPASemester(
          null,
        )
      }
    }

  /* =======================================================
     GPA CALCULATIONS
     ======================================================= */

 
  const validSemesterRecords =
    useMemo(() => {
      if (
        maximumAllowedSemester <=
        0
      ) {
        return []
      }

      return semesterRecords
        .filter(
          record =>
            record.semester <=
              maximumAllowedSemester &&
            Number.isFinite(
              Number(record.sgpa),
            ) &&
            Number(record.sgpa) >= 0 &&
            Number(record.sgpa) <= 4,
        )
        .sort(
          (a, b) =>
            a.semester -
            b.semester,
        )
    }, [
      semesterRecords,
      maximumAllowedSemester,
    ])

  
  const currentSGPA =
    useMemo(() => {
      if (
        validSemesterRecords.length ===
        0
      ) {
        return null
      }

      if (
        maximumAllowedSemester >
        0
      ) {
        const currentRecord =
          validSemesterRecords.find(
            record =>
              record.semester ===
              maximumAllowedSemester,
          )

        if (currentRecord) {
          return currentRecord.sgpa
        }
      }

      return (
        validSemesterRecords.at(
          -1,
        )?.sgpa ?? null
      )
    }, [
      validSemesterRecords,
      maximumAllowedSemester,
    ])

  
  const overallFGPA =
    useMemo(() => {
      const values =
        validSemesterRecords.map(
          record =>
            Number(record.sgpa),
        )

      if (
        values.length === 0
      ) {
        return null
      }

      const average =
        values.reduce(
          (
            sum,
            value,
          ) =>
            sum + value,
          0,
        ) / values.length

      return Number(
        average.toFixed(4),
      )
    }, [validSemesterRecords])

  const completedSemesterCount =
    useMemo(() => {
      return validSemesterRecords.length
    }, [validSemesterRecords])

  /* =======================================================
     CREDITS
     ======================================================= */

  const selectedSemesterCredits =
    selectedSemesterModules.reduce(
      (sum, module) =>
        sum +
        Number(
          module.credits || 0,
        ),
      0,
    )

  const gradeRows =
    selectedSemesterModules

  /* =======================================================
     CHART
     ======================================================= */

  const chartMax = 4

  
  const chartRecords =
    SEMESTERS
      .filter(
        semester =>
          semester <=
          maximumAllowedSemester,
      )
      .map(
        semester => {
          const record =
            validSemesterRecords.find(
              item =>
                item.semester ===
                semester,
            )

          return {
            semester,
            sgpa:
              record?.sgpa ??
              null,
          }
        },
      )

  /* =======================================================
     PROFILE HEADER
     ======================================================= */

  const displayName =
    user?.fullName ||
    'Student'

  const firstName =
    displayName
      .trim()
      .split(/\s+/)[0] ||
    'Student'

  /* =======================================================
     LOADING
     ======================================================= */

  if (loading) {
    return (
      <main className="student-dashboard">
        <div className="student-page-shell">
          <div className="sd-loading-screen">
            <div className="sd-spinner" />

            <strong>
              Loading your academic dashboard
            </strong>

            <span>
              Connecting to your student record...
            </span>
          </div>
        </div>
      </main>
    )
  }

  

  return (
    <main className="student-dashboard">
      <div className="student-page-shell">

        {/* =================================================
            HERO
            ================================================= */}

        <section className="sd-hero">
          <div className="sd-hero-copy">

            <span className="sd-eyebrow">
              STUDENT DASHBOARD
            </span>

            <h1>
              Welcome back, {firstName}.
            </h1>

            <p>
              Manage your academic profile,
              track semester performance,
              record your grades, and access
              personalized AI support.
            </p>

          </div>

          <div className="sd-hero-actions">
            <button
              type="button"
              className="sd-refresh-button"
              onClick={loadDashboard}
              title="Refresh dashboard"
            >
              <Icon name="refresh" />
              Refresh
            </button>
          </div>
        </section>

        {/* =================================================
            ALERTS
            ================================================= */}

        {message && (
          <div className="sd-alert sd-alert-success">
            <Icon name="check" />

            <span>
              {message}
            </span>

            <button
              type="button"
              onClick={() =>
                setMessage('')
              }
            >
              ×
            </button>
          </div>
        )}

        {error && (
          <div className="sd-alert sd-alert-error">
            <Icon name="info" />

            <span>
              {error}
            </span>

            <button
              type="button"
              onClick={() =>
                setError('')
              }
            >
              ×
            </button>
          </div>
        )}

        {/* =================================================
            STUDENT CARD
            ================================================= */}

        <section className="sd-student-card">

          <div className="sd-student-avatar">
            {getInitials(
              displayName,
            )}
          </div>

          <div className="sd-student-main">

            <div className="sd-student-name-row">

              <h2>
                {displayName}
              </h2>

              {profileComplete && (
                <span className="sd-profile-status">
                  <span />
                  Profile complete
                </span>
              )}

            </div>

            <p className="sd-student-id">
              {studentId}
            </p>

            <div className="sd-student-meta">

              <span>
                <Icon name="graduation" />

                {selectedDegree?.degreeName ||
                  'Degree not selected'}
              </span>

              <span>
                <Icon name="user" />

                {selectedFaculty?.facultyName ||
                  'Faculty not selected'}
              </span>

              {intake && (
                <span>
                  <Icon name="calendar" />
                  Intake {intake}
                </span>
              )}

            </div>

          </div>

          <button
            type="button"
            className="sd-edit-profile"
            onClick={() =>
              setProfileOpen(
                previous =>
                  !previous,
              )
            }
          >
            <Icon name="edit" />

            {profileOpen
              ? 'Close'
              : profileComplete
                ? 'Edit profile'
                : 'Set up profile'}
          </button>

        </section>

        {/* =================================================
            PROFILE
            ================================================= */}

        {profileOpen && (
          <section className="sd-panel sd-profile-panel">

            <div className="sd-panel-heading">

              <div className="sd-heading-icon">
                <Icon name="user" />
              </div>

              <div>
                <span className="sd-section-kicker">
                  ACADEMIC PROFILE
                </span>

                <h2>
                  {profileComplete
                    ? 'Update your academic details'
                    : 'Complete your academic profile'}
                </h2>

                <p>
                  Select your actual academic
                  programme. Modules are loaded
                  from the degree-module mapping.
                </p>
              </div>

            </div>

            <form
              className="sd-profile-form"
              onSubmit={
                handleSaveProfile
              }
            >

              {/* INTAKE */}

              <label className="sd-field">
                <span>
                  Intake
                  <b>*</b>
                </span>

                <select
                  value={intake}
                  onChange={event =>
                    setIntake(
                      event.target
                        .value
                        ? Number(
                            event.target
                              .value,
                          )
                        : '',
                    )
                  }
                >
                  <option value="">
                    Select intake
                  </option>

                  {INTAKES.map(
                    value => (
                      <option
                        key={value}
                        value={value}
                      >
                        Intake {value}
                      </option>
                    ),
                  )}
                </select>
              </label>

              {/* FACULTY */}

              <label className="sd-field">
                <span>
                  Faculty
                  <b>*</b>
                </span>

                <select
                  value={facultyId}
                  onChange={event =>
                    handleFacultyChange(
                      event.target
                        .value,
                    )
                  }
                  disabled={
                    loadingReferenceData
                  }
                >
                  <option value="">
                    {loadingReferenceData
                      ? 'Loading faculties...'
                      : faculties.length ===
                          0
                        ? 'No faculties available'
                        : 'Select faculty'}
                  </option>

                  {faculties.map(
                    faculty => (
                      <option
                        key={
                          faculty.facultyId
                        }
                        value={
                          faculty.facultyId
                        }
                      >
                        {
                          faculty.facultyName
                        }
                      </option>
                    ),
                  )}
                </select>

                {referenceError && (
                  <div className="sd-reference-error">
                    <span>
                      {
                        referenceError
                      }
                    </span>

                    <button
                      type="button"
                      onClick={
                        loadReferenceData
                      }
                    >
                      Retry
                    </button>
                  </div>
                )}
              </label>

              {/* DEGREE */}

              <label className="sd-field sd-field-wide">
                <span>
                  Degree programme
                  <b>*</b>
                </span>

                <select
                  value={degreeId}
                  onChange={event =>
                    handleDegreeChange(
                      event.target
                        .value,
                    )
                  }
                  disabled={
                    !facultyId
                  }
                >
                  <option value="">
                    {!facultyId
                      ? 'Select faculty first'
                      : 'Select degree programme'}
                  </option>

                  {filteredDegrees.map(
                    degree => (
                      <option
                        key={
                          degree.degreeId
                        }
                        value={
                          degree.degreeId
                        }
                      >
                        {
                          degree.degreeName
                        }
                      </option>
                    ),
                  )}
                </select>

                {selectedDegree && (
                  <small className="sd-field-hint">
                    {
                      selectedDegree.department
                    }
                    {' · '}
                    {
                      selectedDegree.durationYears
                    }{' '}
                    years
                  </small>
                )}
              </label>

              {/* YEAR */}

              <label className="sd-field">
                <span>
                  Current year
                  <b>*</b>
                </span>

                <select
                  value={currentYear}
                  onChange={event =>
                    handleYearChange(
                      event.target
                        .value,
                    )
                  }
                >
                  <option value="">
                    Select year
                  </option>

                  {availableYears.map(
                    year => (
                      <option
                        key={year}
                        value={year}
                      >
                        Year {year}
                      </option>
                    ),
                  )}
                </select>
              </label>

              {/* SEMESTER */}

              <label className="sd-field">
                <span>
                  Current semester
                  <b>*</b>
                </span>

                <select
                  value={
                    currentSemester
                  }
                  onChange={event =>
                    handleSemesterChange(
                      event.target
                        .value,
                    )
                  }
                  disabled={
                    !currentYear
                  }
                >
                  <option value="">
                    {!currentYear
                      ? 'Select year first'
                      : 'Select semester'}
                  </option>

                  {availableSemesters.map(
                    semester => (
                      <option
                        key={semester}
                        value={semester}
                      >
                        Semester{' '}
                        {semester}
                      </option>
                    ),
                  )}
                </select>

                <small className="sd-field-hint">
                  {currentYear
                    ? `Year ${currentYear} contains semesters ${getFirstSemesterForYear(
                        currentYear,
                      )} and ${getMaxSemesterForYear(
                        currentYear,
                      )}.`
                    : 'Semester is determined by your current year.'}
                </small>
              </label>

              <div className="sd-profile-actions">

                <button
                  type="submit"
                  className="sd-primary-button"
                  disabled={
                    savingProfile ||
                    !profileComplete
                  }
                >
                  <Icon name="save" />

                  {savingProfile
                    ? 'Saving...'
                    : 'Save academic profile'}

                  {!savingProfile && (
                    <Icon name="arrow" />
                  )}
                </button>

              </div>

            </form>
          </section>
        )}

        {/* =================================================
            ACADEMIC OVERVIEW
            ================================================= */}

        <section className="sd-section">

          <div className="sd-section-heading">

            <div>
              <span className="sd-section-kicker">
                OVERVIEW
              </span>

              <h2>
                Academic performance
              </h2>
            </div>

            {profileComplete && (
              <span className="sd-semester-context">
                Year {currentYear}
                {' · '}
                Semester {currentSemester}
              </span>
            )}

          </div>

          <div className="sd-stat-grid">

            {/* CURRENT SGPA */}

            <article className="sd-stat-card">

              <div className="sd-stat-icon blue">
                <Icon name="chart" />
              </div>

              <div>
                <span>
                  Current SGPA
                </span>

                <strong>
                  {formatGPA(
                    currentSGPA,
                  )}
                </strong>

                <small>
                  {currentSemester
                    ? `Semester ${currentSemester}`
                    : 'Latest recorded semester'}
                </small>
              </div>

            </article>

            {/* FGPA */}

            <article className="sd-stat-card">

              <div className="sd-stat-icon purple">
                <Icon name="graduation" />
              </div>

              <div>
                <span>
                  Overall FGPA
                </span>

                <strong>
                  {formatGPA(
                    overallFGPA,
                  )}
                </strong>

                <small>
                  Based on saved semester GPAs
                </small>
              </div>

            </article>

            {/* SEMESTERS */}

            <article className="sd-stat-card">

              <div className="sd-stat-icon green">
                <Icon name="calendar" />
              </div>

              <div>
                <span>
                  Semesters
                </span>

                <strong>
                  {completedSemesterCount}
                  <em>/ 8</em>
                </strong>

                <small>
                  Semesters with SGPA
                </small>
              </div>

            </article>

            {/* CREDITS */}

            <article className="sd-stat-card">

              <div className="sd-stat-icon orange">
                <Icon name="book" />
              </div>

              <div>
                <span>
                  Current credits
                </span>

                <strong>
                  {selectedSemesterCredits}
                </strong>

                <small>
                  Mapped modules
                </small>
              </div>

            </article>

          </div>
        </section>

        {/* =================================================
            PERFORMANCE + SGPA
            ================================================= */}

        <section className="sd-main-grid">

          {/* PERFORMANCE CHART */}

          <article className="sd-panel sd-chart-panel">

            <div className="sd-panel-heading compact">

              <div className="sd-heading-icon">
                <Icon name="chart" />
              </div>

              <div>
                <span className="sd-section-kicker">
                  PERFORMANCE TREND
                </span>

                <h2>
                  Semester SGPA
                </h2>

                <p>
                  Your chart updates automatically
                  after an SGPA is saved.
                </p>
              </div>

            </div>

            <div className="sd-chart">

              <div className="sd-y-axis">
                <span>4.0</span>
                <span>3.0</span>
                <span>2.0</span>
                <span>1.0</span>
                <span>0.0</span>
              </div>

              <div className="sd-chart-area">

                <div className="sd-grid-lines">
                  <span />
                  <span />
                  <span />
                  <span />
                  <span />
                </div>

                <div className="sd-bars">

                  {chartRecords.map(
                    item => {

                      /*
                       * 0.00 = 0%
                       * 2.00 = 50%
                       * 3.00 = 75%
                       * 4.00 = 100%
                       */
                      const height =
                        item.sgpa ===
                        null
                          ? 0
                          : Math.max(
                              0,
                              Math.min(
                                100,
                                (
                                  item.sgpa /
                                  chartMax
                                ) *
                                  100,
                              ),
                            )

                      return (
                        <div
                          className="sd-bar-column"
                          key={
                            item.semester
                          }
                        >

                          <div className="sd-bar-value">
                            {item.sgpa !==
                            null
                              ? item.sgpa.toFixed(
                                  2,
                                )
                              : '—'}
                          </div>

                          <div className="sd-bar-track">

                            {item.sgpa !==
                              null && (
                              <div
                                className="sd-bar"
                                style={{
                                  height:
                                    `${height}%`,
                                }}
                                title={`Semester ${item.semester}: ${item.sgpa.toFixed(
                                  4,
                                )}`}
                              />
                            )}

                          </div>

                          <span>
                            S
                            {
                              item.semester
                            }
                          </span>

                        </div>
                      )
                    },
                  )}

                </div>
              </div>
            </div>
          </article>

          {/* SGPA ENTRY */}

          <article className="sd-panel sd-sgpa-panel">

            <div className="sd-panel-heading compact">

              <div className="sd-heading-icon">
                <Icon name="edit" />
              </div>

              <div>
                <span className="sd-section-kicker">
                  SEMESTER RECORD
                </span>

                <h2>
                  Enter SGPA
                </h2>

                <p>
                  You can only enter SGPA for
                  your current or previously
                  completed semesters.
                </p>
              </div>

            </div>

            <div className="sd-sgpa-list">

              {SEMESTERS
                .filter(
                  semester =>
                    semester <=
                    maximumAllowedSemester,
                )
                .map(
                  semester => {

                    const isCurrent =
                      semester ===
                      maximumAllowedSemester

                    return (
                      <div
                        className="sd-sgpa-row"
                        key={
                          semester
                        }
                      >

                        <div className="sd-sgpa-label">

                          <strong>
                            Semester{' '}
                            {semester}
                          </strong>

                          <span>
                            Year{' '}
                            {Math.ceil(
                              semester /
                                2,
                            )}

                            {isCurrent &&
                              ' · Current'}
                          </span>

                        </div>

                        <input
                          type="number"
                          min="0"
                          max="4"
                          step="0.0001"
                          placeholder="0.0000"
                          value={
                            sgpaValues[
                              semester
                            ] || ''
                          }
                          disabled={
                            !profileComplete
                          }
                          onChange={event =>
                            handleSGPAChange(
                              semester,
                              event.target
                                .value,
                            )
                          }
                        />

                        <button
                          type="button"
                          className="sd-small-save"
                          onClick={() =>
                            handleSaveSGPA(
                              semester,
                            )
                          }
                          disabled={
                            savingSGPA ||
                            !profileComplete ||
                            !sgpaValues[
                              semester
                            ]
                          }
                        >
                          {savingSGPASemester ===
                          semester
                            ? '...'
                            : 'Save'}
                        </button>

                      </div>
                    )
                  },
                )}

            </div>
          </article>
        </section>

        {/* =================================================
            COURSE GRADES
            ================================================= */}

        <section className="sd-panel sd-modules-panel">

          <div className="sd-panel-heading">

            <div className="sd-heading-icon">
              <Icon name="book" />
            </div>

            <div>
              <span className="sd-section-kicker">
                ACADEMIC RESULTS
              </span>

              <h2>
                Course modules & grades
              </h2>

              <p>
                Modules are automatically loaded
                from the selected degree and
                semester.
              </p>
            </div>

          </div>

          {/* SEMESTER TABS */}

          <div className="sd-semester-tabs">

            {SEMESTERS
              .filter(
                semester =>
                  semester <=
                  maximumAllowedSemester,
              )
              .map(
                semester => {

                  const hasGrades =
                    (
                      grades[
                        semester
                      ] || []
                    ).length > 0

                  return (
                    <button
                      type="button"
                      key={
                        semester
                      }
                      className={
                        selectedGradeSemester ===
                        semester
                          ? 'active'
                          : ''
                      }
                      onClick={() =>
                        handleGradeSemesterChange(
                          semester,
                        )
                      }
                      disabled={
                        !degreeId
                      }
                    >
                      <span>
                        S{semester}
                      </span>

                      {hasGrades && (
                        <i>
                          <Icon name="check" />
                        </i>
                      )}
                    </button>
                  )
                },
              )}

          </div>

          {!profileComplete ? (
            <div className="sd-empty-state">

              <div className="sd-empty-icon">
                <Icon name="user" />
              </div>

              <h3>
                Complete your academic profile
              </h3>

              <p>
                Select your faculty, degree,
                intake, year and semester above.
              </p>

              <button
                type="button"
                className="sd-primary-button"
                onClick={() =>
                  setProfileOpen(true)
                }
              >
                <Icon name="edit" />
                Complete profile
              </button>

            </div>
          ) : loadingModules ? (
            <div className="sd-module-loading">

              <div className="sd-spinner" />

              <span>
                Loading modules for Semester{' '}
                {
                  selectedGradeSemester
                }...
              </span>

            </div>
          ) : gradeRows.length ===
            0 ? (
            <div className="sd-empty-state">

              <div className="sd-empty-icon">
                <Icon name="book" />
              </div>

              <h3>
                No mapped modules
              </h3>

              <p>
                No modules are mapped to{' '}
                {
                  selectedDegree?.degreeName ||
                  'this degree'
                }{' '}
                for Semester{' '}
                {
                  selectedGradeSemester
                }.
              </p>

            </div>
          ) : (
            <>
              <div className="sd-module-summary">

                <div>
                  <strong>
                    Semester{' '}
                    {
                      selectedGradeSemester
                    }
                  </strong>

                  <span>
                    {
                      gradeRows.length
                    }{' '}
                    modules
                  </span>
                </div>

                <div>
                  <strong>
                    {
                      selectedSemesterCredits
                    }
                  </strong>

                  <span>
                    total credits
                  </span>
                </div>

              </div>

              <div className="sd-module-table-wrap">

                <table className="sd-module-table">

                  <thead>
                    <tr>
                      <th>
                        Module
                      </th>

                      <th>
                        Type
                      </th>

                      <th>
                        Credits
                      </th>

                      <th>
                        Category
                      </th>

                      <th>
                        Grade
                      </th>

                      <th>
                        GPA
                      </th>
                    </tr>
                  </thead>

                  <tbody>

                    {gradeRows.map(
                      module => {

                        const grade =
                          getGradeForCourse(
                            selectedGradeSemester,
                            module.courseCode,
                          )

                        const point =
                          getGradePoint(
                            grade,
                          )

                        return (
                          <tr
                            key={
                              module.courseCode
                            }
                          >

                            <td>
                              <div className="sd-module-name">

                                <strong>
                                  {
                                    module.moduleName
                                  }
                                </strong>

                                <span>
                                  {
                                    module.courseCode
                                  }
                                </span>

                              </div>
                            </td>

                            <td>
                              <span
                                className={`sd-type-badge ${
                                  module.moduleType ===
                                  'Elective'
                                    ? 'elective'
                                    : 'core'
                                }`}
                              >
                                {
                                  module.moduleType ||
                                  'Core'
                                }
                              </span>
                            </td>

                            <td>
                              <span className="sd-credit">
                                {
                                  module.credits
                                }
                              </span>
                            </td>

                            <td>
                              <span
                                className={`sd-category-badge ${
                                  module.moduleCategory ===
                                  'GPA'
                                    ? 'gpa'
                                    : 'nongpa'
                                }`}
                              >
                                {
                                  module.moduleCategory
                                }
                              </span>
                            </td>

                            <td>

                              <select
                                className="sd-grade-select"
                                value={
                                  grade
                                }
                                onChange={event =>
                                  updateGrade(
                                    selectedGradeSemester,
                                    module.courseCode,
                                    event.target
                                      .value,
                                  )
                                }
                              >
                                <option value="">
                                  Select
                                </option>

                                {GRADE_OPTIONS.map(
                                  option => (
                                    <option
                                      key={
                                        option.grade
                                      }
                                      value={
                                        option.grade
                                      }
                                    >
                                      {
                                        option.grade
                                      }
                                    </option>
                                  ),
                                )}
                              </select>

                            </td>

                            <td>

                              <span
                                className={`sd-grade-point ${
                                  point !==
                                    null &&
                                  point >=
                                    3.7
                                    ? 'excellent'
                                    : point !==
                                          null &&
                                      point >=
                                        3
                                      ? 'good'
                                      : point !==
                                          null
                                        ? 'low'
                                        : ''
                                }`}
                              >
                                {point !==
                                null
                                  ? point.toFixed(
                                      1,
                                    )
                                  : '—'}
                              </span>

                            </td>

                          </tr>
                        )
                      },
                    )}

                  </tbody>
                </table>
              </div>

              <div className="sd-module-footer">

                <div className="sd-grade-note">
                  <Icon name="info" />

                  <span>
                    GPA modules contribute to GPA.
                    NON_GPA modules are recorded
                    but should not be included in
                    GPA calculations.
                  </span>
                </div>

                <button
                  type="button"
                  className="sd-primary-button"
                  onClick={
                    handleSaveGrades
                  }
                  disabled={
                    savingGrades
                  }
                >
                  <Icon name="save" />

                  {savingGrades
                    ? 'Saving grades...'
                    : 'Save semester grades'}
                </button>

              </div>
            </>
          )}
        </section>

        {/* =================================================
            AI SERVICES
            ================================================= */}

        <section className="sd-section sd-ai-section">

          <div className="sd-section-heading">

            <div>
              <span className="sd-section-kicker">
                AI SUPPORT
              </span>

              <h2>
                Your academic intelligence tools
              </h2>

              <p>
                Three AI services designed for
                prediction, optimization and
                explainable academic reasoning.
              </p>
            </div>

          </div>

          <div className="sd-ai-grid">

            {/* PREDICTION */}

            <Link
              to="/prediction"
              className="sd-ai-card prediction"
            >
              <div className="sd-ai-top">

                <div className="sd-ai-icon">
                  <Icon name="brain" />
                </div>

                <span className="sd-ai-arrow">
                  <Icon name="arrow" />
                </span>

              </div>

              <span className="sd-ai-label">
                NEURAL NETWORK
              </span>

              <h3>
                Performance Prediction
              </h3>

              <p>
                Predict your expected academic
                performance using your academic
                and behavioural information.
              </p>

              <span className="sd-ai-action">
                Open prediction
                <Icon name="arrow" />
              </span>
            </Link>

            {/* STUDY PLAN */}

            <Link
              to="/study-plan"
              className="sd-ai-card optimization"
            >
              <div className="sd-ai-top">

                <div className="sd-ai-icon">
                  <Icon name="spark" />
                </div>

                <span className="sd-ai-arrow">
                  <Icon name="arrow" />
                </span>

              </div>

              <span className="sd-ai-label">
                GENETIC ALGORITHM
              </span>

              <h3>
                Personalized Study Plan
              </h3>

              <p>
                Allocate your available study
                hours intelligently across modules
                according to priorities and credits.
              </p>

              <span className="sd-ai-action">
                Create study plan
                <Icon name="arrow" />
              </span>
            </Link>

            {/* ELIGIBILITY */}

            <Link
              to="/eligibility"
              className="sd-ai-card eligibility"
            >
              <div className="sd-ai-top">

                <div className="sd-ai-icon">
                  <Icon name="shield" />
                </div>

                <span className="sd-ai-arrow">
                  <Icon name="arrow" />
                </span>

              </div>

              <span className="sd-ai-label">
                RULE-BASED SYSTEM
              </span>

              <h3>
                Academic Eligibility
              </h3>

              <p>
                Check academic requirements and
                receive an explainable eligibility
                decision based on university rules.
              </p>

              <span className="sd-ai-action">
                Check eligibility
                <Icon name="arrow" />
              </span>
            </Link>

          </div>
        </section>

        {/* =================================================
            FOOTER NOTE
            ================================================= */}

        <div className="sd-dashboard-note">

          <Icon name="info" />

          <p>
            Academic information entered here is
            stored against your student account and
            is used to provide personalized decision
            support. AI outputs are advisory and do
            not replace official university decisions.
          </p>

        </div>

      </div>
    </main>
  )
}

export default StudentDashboard