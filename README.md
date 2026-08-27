# 🎓 AI-Based Smart Campus Decision Support System

### Personalized Student Services using Artificial Intelligence

An AI-based web application designed to provide university students with **personalized academic decision support** through student performance prediction, study-plan optimization, and academic eligibility assessment.

> **Academic Project — Faculty of Computing, General Sir John Kotelawala Defence University (KDU)**

---

## 📌 Overview

University students often need to consider multiple factors when making academic decisions, including previous performance, attendance, assessment marks, study hours, repeated courses, and academic requirements.

The **AI-Based Smart Campus Decision Support System** addresses these challenges by integrating three complementary Artificial Intelligence techniques:

* 🧠 **Neural Network** — Student Next Semester GPA Prediction
* 🧬 **Genetic Algorithm** — Personalized Study-Plan Optimization
* 📋 **Rule-Based Expert System** — Academic Eligibility Assessment

The three AI components are integrated into a web-based platform to provide students with personalized and explainable academic support.

> **Note:** The system is a decision-support tool and does not replace lecturers, academic advisors, or official university academic decisions.

---

## ✨ Key Features

### 🧠 Student Next Semester GPA Prediction

Predicts expected student academic performance using relevant academic and behavioral information such as:

* Previous SGPA
* Current SGPA
* Repeated courses

### 🧬 Personalized Study-Plan Optimization

Uses a **Genetic Algorithm** to allocate a student's limited weekly study hours among modules based on:

* Module performance
* Module priority
* Module credits
* Available study hours
* Defined constraints

### 📋 Academic Eligibility Assessment

Uses a **Rule-Based Expert System** to evaluate academic requirements such as:

* Attendance
* Fee status
* Examination requirements
* Prerequisites
* Course requirements

The system provides both an **eligibility decision and an explanation**.

---

## 🏗️ System Architecture

```text
                    ┌──────────────────┐
                    │     Student      │
                    └────────┬─────────┘
                             │
                             ▼
                 ┌──────────────────────┐
                 │ React + TypeScript   │
                 │     Frontend         │
                 └──────────┬───────────┘
                            │ REST API
                            ▼
                 ┌──────────────────────┐
                 │    Spring Boot       │
                 │      Backend         │
                 └───────┬───────┬──────┘
                         │       │
                         ▼       ▼
                    ┌────────┐ ┌──────────────┐
                    │ MySQL  │ │   FastAPI    │
                    │        │ │  AI Service  │
                    └────────┘ └──────┬───────┘
                                      │
                           ┌──────────┼──────────┐
                           ▼          ▼          ▼
                       Neural Net    GA     Rule Engine
```

---

## 🤖 AI Components

| Component              | Technique                | Purpose                        |
| ---------------------- | ------------------------ | ------------------------------ |
| Performance Prediction | Neural Network           | Predict next semester GPA      |
| Study Planning         | Genetic Algorithm        | Optimize study-hour allocation |
| Eligibility            | Rule-Based Expert System | Evaluate academic requirements |

Together, the system demonstrates three major AI capabilities:

**Learning → Optimization → Reasoning**

---

## 🛠️ Technology Stack

### Frontend

* React
* TypeScript
* Tailwind CSS
* Vite

### Backend

* Java 21
* Spring Boot
* Spring Data JPA
* Spring Security
* Hibernate
* Maven

### AI / Machine Learning

* Python
* TensorFlow / Keras
* Scikit-learn
* Pandas
* NumPy
* FastAPI

### Database & Tools

* MySQL
* Git & GitHub
* Postman
* Jupyter Notebook
* Visual Studio Code

---

## 📊 Dataset

The system uses structured academic data for development and testing.

### Main datasets

```text
data/
├── faculties.csv
├── degrees.csv
├── course_modules.csv
├── degree_modules.csv
├── students.csv
├── student_results.csv
└── ml/
    └── next_semester_gpa_dataset_clean.csv
```

### Current Dataset

| Dataset          | Records |
| ---------------- | ------: |
| Students         |   3,000 |
| Student Results  | 108,083 |
| Degrees          |       5 |
| Faculties        |       2 |
| Course Modules   |     220 |
| Degree Modules   |     345 |
| Clean ML Records |   6,129 |

Dataset validation and cleaning scripts are included to improve data quality before ML development.

---

## 📂 Project Structure

```text
AI-Smart-Campus-Decision-Support-System/
│
├── app/                 # React + TypeScript frontend
│
├── backend/             # Spring Boot backend
│
├── data/                # Academic datasets
│
├── ml/                  # ML & dataset processing
│
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have:

```text
Node.js
Java 21
Maven
Python 3.11+
MySQL
Git
```

### Clone the Repository

```bash
git clone https://github.com/<your-username>/AI-Smart-Campus-Decision-Support-System.git

cd AI-Smart-Campus-Decision-Support-System
```

### Frontend

```bash
cd app
npm install
npm run dev
```

### Backend

```bash
cd backend
```

Windows:

```powershell
.\mvnw.cmd clean install
.\mvnw.cmd spring-boot:run
```

### Machine Learning

Create a virtual environment:

```bash
python -m venv smartcampus-ai
```

Windows:

```powershell
.\smartcampus-ai\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install pandas numpy matplotlib scikit-learn tensorflow jupyter
```

---

## 🗄️ Database Configuration

Create the MySQL database:

```sql
CREATE DATABASE smart_campus;
```

Configure the connection in:

```text
backend/src/main/resources/application.properties
```

Example:

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/smart_campus
spring.datasource.username=root
spring.datasource.password=YOUR_PASSWORD

spring.jpa.hibernate.ddl-auto=update
```

> ⚠️ Never commit real passwords, API keys, JWT secrets, or other sensitive credentials to GitHub.

---

## 🧪 Evaluation

The project evaluates each AI component using appropriate measures.

### Neural Network

* MAE
* RMSE
* R²

### Genetic Algorithm

* Fitness score
* Constraint satisfaction
* Study-time utilization
* Comparison with baseline allocation

### Rule-Based Expert System

* Rule correctness
* Decision correctness
* Requirement coverage
* Explanation correctness

---

## 🎯 Project Objectives

The project aims to:

1. Develop a Neural Network for student performance prediction.
2. Develop a Genetic Algorithm for personalized study-plan optimization.
3. Develop a Rule-Based Expert System for academic eligibility assessment.
4. Integrate the AI components into a web-based system.
5. Evaluate the performance and correctness of the proposed AI solutions.

---

## ⚠️ Disclaimer

This project is an **academic prototype** developed for educational and research purposes.

AI-generated predictions, recommendations, and eligibility results are intended only as **decision-support information**. They should not be considered official university academic decisions.

---

## ⭐ Vision

> **Transform student academic data into intelligent, personalized, and explainable academic decision support.**

**Built with React • TypeScript • Spring Boot • Python • AI • MySQL**

### Developed by Group 20

**Faculty of Computing — General Sir John Kotelawala Defence University**
