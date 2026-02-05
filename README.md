# 🛡️ DPDP Compliance Shield (Enterprise Edition)

![Version](https://img.shields.io/badge/Version-2.0.0-blue?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Stack-FastAPI%20|%20Next.js%20|%20Docker-success?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-NextAuth%20v5-red?style=for-the-badge)

**An Automated Data Security Posture Management (DSPM) Platform designed for the Indian DPDP Act, 2023.**

> **Note:** This project is a fully containerized microservices application. It scans Files, Databases, and AWS Cloud Storage for PII (Personally Identifiable Information) leaks.

---

## 📖 Overview

The **DPDP Compliance Shield** helps organizations prevent massive fines (up to ₹250 Cr) by proactively discovering sensitive data leaks. Unlike simple scripts, this is a full-stack SaaS platform that provides:

1.  **🔍 Deep Packet Inspection:** Uses Regex & NLP patterns to find Aadhaar, PAN, and Mobile numbers.
2.  **☁️ Cloud Security:** Connects directly to **AWS S3 Buckets** to find public or unencrypted PII.
3.  **🏢 Enterprise Architecture:** Runs on **Docker** with separate frontend/backend containers.
4.  **🔒 Role-Based Access:** Protected by **NextAuth.js** (Credentials Provider).

---

## ✨ Key Features

### 1. 🛡️ Secure Dashboard
- **Dark Mode UI:** Professional "Command Center" aesthetic with glassmorphism effects.
- **Authentication:** Admin-only access via NextAuth.js v5.
- **Audit History:** Immutable logs of all past scans for compliance reporting.

### 2. ⚡ Multi-Vector Scanning
| Vector | Description |
| :--- | :--- |
| **📂 Files** | Upload `.csv`, `.txt`, or `.sql` dumps to scan for local leaks. |
| **🔌 Databases** | Connect to live `SQLite` or `MySQL` databases via connection strings. |
| **☁️ Cloud S3** | Scan AWS S3 buckets using `boto3` integration (Server-side streaming). |

### 3. 📄 Compliance Reporting
- Generates **PDF Audit Certificates** instantly.
- Flags "High Risk" data points automatically.

---

## 🚀 Quick Start (Docker)

You can run the entire infrastructure with a single command. No Python or Node.js installation required.

### Prerequisites
- **Docker Desktop** installed and running.

### Installation

1. **Clone the repository**
   ```bash
   git clone [https://github.com/Prem-Kt-2522/dpdp-compliance-shield.git](https://github.com/Prem-Kt-2522/dpdp-compliance-shield.git)
   cd dpdp-compliance-shield
2. **Start the Application**
   ```bash
   docker-compose up --build

Wait for backend-1 and frontend-1 to show "Ready".
3. **Access the Dashboard**

Open: http://localhost:3000

Login: admin123

Password: admin123

🛠️ Tech Stack & Architecture
The application follows a Microservices Architecture:

Frontend Container: Next.js 14 (App Router), TypeScript, Tailwind CSS.

Backend Container: Python FastAPI, Uvicorn, SQLAlchemy, Boto3.

Database: SQLite (persisted via Docker Volumes).

Orchestration: Docker Compose (Bridge Network).

Project Structure
Bash
├── backend/            # FastAPI Python Server
│   ├── main.py         # API Entry points
│   ├── s3_scanner.py   # AWS Logic
│   └── Dockerfile      # Python Environment
├── frontend/           # Next.js Dashboard
│   ├── app/            # Pages & Routes
│   ├── auth.ts         # NextAuth Security Config
│   └── Dockerfile      # Node.js Environment
└── docker-compose.yml  # Infrastructure as Code

Login Page,Security Dashboard,AWS S3 Scan,Pdf report
<img width="1361" height="626" alt="image" src="https://github.com/user-attachments/assets/a28c7fc1-83e1-43c4-955f-027322ec912a" />

<img width="1348" height="632" alt="image" src="https://github.com/user-attachments/assets/630a5708-95da-4db8-bddc-bb7c87b108b6" />

<img width="1346" height="628" alt="image" src="https://github.com/user-attachments/assets/2a594ccd-ab95-4e55-b64c-f53cc743e8d1" />

<img width="1344" height="628" alt="image" src="https://github.com/user-attachments/assets/fd17aafb-3df4-4dc0-8982-00f91134dd8d" />

