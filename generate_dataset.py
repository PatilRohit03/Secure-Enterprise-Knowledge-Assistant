import os
import json
import logging
import pandas as pd
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Import DB and ingestion utilities directly from main backend module
from main import init_db, ingest_document, DATA_DIR

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("DatasetGenerator")

def build_pdf_document(filepath: Path, title: str, paragraphs: list) -> None:
    """Uses reportlab library to generate a formatted PDF document."""
    try:
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph(title, styles['Title']), Spacer(1, 15)]
        
        for p in paragraphs:
            story.append(Paragraph(p, styles['BodyText']))
            story.append(Spacer(1, 10))
            
        doc.build(story)
    except Exception as e:
        logger.error(f"Error generating PDF {filepath.name}: {e}")

def run_generation() -> None:
    """Generates the required enterprise documents and runs the ingestion pipeline."""
    raw_dir = DATA_DIR / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("Initializing database tables...")
    init_db()
    
    logger.info("Generating 10 synthetic PDF documents...")
    
    pdf_files = [
        {
            "filename": "HR_Employee_Handbook.pdf",
            "title": "Enterprise Employee Handbook",
            "department": "HR",
            "access_level": "Internal",
            "allowed_roles": ["Admin", "HR", "Finance", "Engineering", "Compliance"],
            "paragraphs": [
                "Welcome to the Enterprise Platform. We are dedicated to providing a professional, inclusive, and collaborative working environment for all our staff.",
                "Working Hours: Our core business hours are 9:00 AM to 5:00 PM local time. Flexible working arrangements are available with approval from your manager.",
                "Leave Policy: Full-time employees receive 20 days of paid annual leave per fiscal year. In addition, employees receive 10 days of paid sick leave and 5 personal days.",
                "Code of Conduct: Professional integrity and mutual respect are foundational. Harassment, discrimination, or unethical behavior of any kind will not be tolerated."
            ]
        },
        {
            "filename": "HR_Benefits_Summary_2026.pdf",
            "title": "Employee Benefits Plan Summary 2026",
            "department": "HR",
            "access_level": "Internal",
            "allowed_roles": ["Admin", "HR", "Finance", "Engineering", "Compliance"],
            "paragraphs": [
                "Health Insurance: We offer comprehensive medical, dental, and vision insurance coverage. Plans are subsidized up to 80% for employees and their dependents.",
                "Retirement: The company matches 100% of employee 401(k) contributions up to 4% of their annual salary. Matching vests immediately upon contribution.",
                "Wellness Program: Employees are eligible for a $50 monthly wellness reimbursement. This can be used for gym memberships, fitness classes, or wellness applications.",
                "Educational Assistance: Tuition reimbursement is provided up to $5,000 annually for relevant coursework and degree programs approved by HR."
            ]
        },
        {
            "filename": "HR_Salary_Bands_Confidential.pdf",
            "title": "CONFIDENTIAL: Corporate Salary Bands & Compensation Guidelines",
            "department": "HR",
            "access_level": "Confidential",
            "allowed_roles": ["Admin", "HR"],
            "paragraphs": [
                "This document outlines the standard salary ranges and compensation bands across different job levels for the 2026 fiscal year.",
                "Level 1 (Associate): Salary range is $60,000 to $85,000. Eligible for up to 5% performance bonus.",
                "Level 2 (Senior Specialist / Engineer): Salary range is $90,000 to $135,000. Eligible for up to 10% performance bonus.",
                "Level 3 (Lead / Manager): Salary range is $140,000 to $190,000. Eligible for up to 15% performance bonus.",
                "Level 4 (Director / Executive): Salary range starts at $200,000. Eligible for up to 25% performance bonus and equity packages."
            ]
        },
        {
            "filename": "Finance_Q2_Revenue_Report.pdf",
            "title": "Q2 Financial Performance & Revenue Analysis",
            "department": "Finance",
            "access_level": "Confidential",
            "allowed_roles": ["Admin", "Finance", "Compliance"],
            "paragraphs": [
                "Overall Financial Position: In Q2, the corporation recorded gross revenue of $14.2 million, representing an 8.5% quarter-over-quarter growth compared to Q1.",
                "Operating Expenses: Total operating expenses were $9.8 million. Research and development accounted for 40% of spend, while sales and marketing accounted for 35%.",
                "Net Profit Margin: Net income for the quarter stood at $3.1 million, reflecting a profit margin of 21.8%.",
                "Regional Growth: North America continues to be the largest market, contributing 60% of revenue, followed by EMEA at 25% and APAC at 15%."
            ]
        },
        {
            "filename": "Finance_Forecast_2027.pdf",
            "title": "RESTRICTED: Long-Term Financial Forecast 2027",
            "department": "Finance",
            "access_level": "Restricted",
            "allowed_roles": ["Admin", "Finance"],
            "paragraphs": [
                "This document contains high-level strategic projections for the 2027 fiscal year. All information is strictly proprietary and restricted to Finance leadership.",
                "Target Revenue: Our goal is to achieve $75 million in annual revenue by end of 2027, driven by our new cloud intelligence platform expansion.",
                "Projected Headcount Growth: We anticipate increasing the engineering team by 45% and the sales team by 30% to support scaling requirements.",
                "Strategic M&A: We have allocated $8 million for the acquisition of boutique data science firms to expand our model capabilities."
            ]
        },
        {
            "filename": "Engineering_Architecture_Design.pdf",
            "title": "Engineering Design & Architecture Specifications",
            "department": "Engineering",
            "access_level": "Internal",
            "allowed_roles": ["Admin", "Engineering"],
            "paragraphs": [
                "System Overview: The platform utilizes a microservices architecture built on FastAPI backend systems and deployed via Docker containers.",
                "Data Storage: Core transactional data is stored in PostgreSQL. Embeddings are generated using Sentence Transformers and cached in FAISS.",
                "Security: Microservices communicate using gRPC with TLS. Authentication is managed via OAuth2 with JSON Web Tokens (JWT).",
                "Scalability: Horizontal scaling is managed using Kubernetes. Auto-scaling rules are based on CPU usage exceeding 75% for more than 5 minutes."
            ]
        },
        {
            "filename": "Engineering_Coding_Guidelines.pdf",
            "title": "Engineering Coding Guidelines & Best Practices",
            "department": "Engineering",
            "access_level": "Public",
            "allowed_roles": ["Admin", "HR", "Finance", "Engineering", "Compliance"],
            "paragraphs": [
                "Python Standards: We adhere strictly to PEP 8 standards. All code must be formatted using Black and checked with Flake8 before merging.",
                "Documentation: All public classes and functions must include descriptive docstrings detailing parameters and return types.",
                "Testing: Minimum unit test coverage is 80%. Pull requests will fail CI/CD checks if coverage drops below this threshold.",
                "Pull Requests: Code reviews require approval from at least two senior team members before a merge into the main branch can occur."
            ]
        },
        {
            "filename": "Security_Incident_Response_Plan.pdf",
            "title": "CONFIDENTIAL: Enterprise Security Incident Response Plan",
            "department": "Security",
            "access_level": "Confidential",
            "allowed_roles": ["Admin", "Compliance"],
            "paragraphs": [
                "Severity Levels: Incidents are classified into three severity levels: Sev-1 (Critical Breach), Sev-2 (Partial Degradation), and Sev-3 (Low Threat).",
                "Containment Protocol: For Sev-1 incidents, the Security Operations Center (SOC) must isolate affected networks within 15 minutes of detection.",
                "Communication Plan: External notifications for data breaches must be made within 72 hours to comply with international regulations.",
                "Post-Mortem: A detailed Root Cause Analysis (RCA) must be published within 5 business days after any Sev-1 or Sev-2 incident is resolved."
            ]
        },
        {
            "filename": "Compliance_SOC2_Audit_Report.pdf",
            "title": "SOC 2 Type II Compliance & Audit Statement",
            "department": "Legal",
            "access_level": "Confidential",
            "allowed_roles": ["Admin", "Compliance"],
            "paragraphs": [
                "Trust Services Criteria: This report evaluates the controls implemented by the organization related to Security, Availability, and Confidentiality.",
                "Access Reviews: User access privileges are audited quarterly. Non-active accounts are deactivated within 90 days of inactivity.",
                "Vulnerability Scanning: Automated external vulnerability scans are executed weekly. Critical issues must be patched within 14 days.",
                "Physical Security: Data centers are hosted in ISO 27001 certified facilities with biometric access controls and 24/7 video monitoring."
            ]
        },
        {
            "filename": "Compliance_GDPR_Data_Policy.pdf",
            "title": "GDPR Compliance & General Data Protection Policy",
            "department": "Legal",
            "access_level": "Internal",
            "allowed_roles": ["Admin", "HR", "Finance", "Engineering", "Compliance"],
            "paragraphs": [
                "Data Subject Rights: Employees and customers have the right to access, rectify, or delete their personal data (Right to be Forgotten).",
                "Data Minimization: We collect only the minimum personal data required to perform business functions, and store it securely.",
                "Data Retention: Personal data is retained for 7 years post-employment, after which it is automatically anonymized or destroyed.",
                "Data Processing Agreements: All third-party vendor contracts must include a standard Data Processing Agreement (DPA) protecting user privacy."
            ]
        }
    ]
    
    for item in pdf_files:
        path = raw_dir / item["filename"]
        build_pdf_document(path, item["title"], item["paragraphs"])
        ingest_document(
            file_path=path,
            department=item["department"],
            access_level=item["access_level"],
            allowed_roles=item["allowed_roles"],
            owner="system"
        )
        logger.info(f"Generated & Ingested PDF: {item['filename']}")
        
    logger.info("Generating 5 CSV datasets...")
    
    # 1. Sales Records
    sales = {
        "TransactionID": ["TX1001", "TX1002", "TX1003", "TX1004", "TX1005"],
        "Client": ["Apex Corp", "ByteSize LLC", "Core Industries", "Delta Ltd", "Echo Solutions"],
        "Amount": [150000, 45000, 220000, 85000, 12000],
        "Region": ["US-East", "US-West", "EMEA", "APAC", "US-East"],
        "Status": ["Paid", "Paid", "Pending", "Paid", "Refunded"]
    }
    pd.DataFrame(sales).to_csv(raw_dir / "finance_sales_records.csv", index=False)
    ingest_document(raw_dir / "finance_sales_records.csv", "Finance", "Confidential", ["Admin", "Finance"], "system")
    
    # 2. Directory
    directory = {
        "EmployeeID": ["EMP001", "EMP002", "EMP003", "EMP004", "EMP005"],
        "Name": ["John Doe", "Jane Smith", "Bob Johnson", "Alice Williams", "Charlie Brown"],
        "Department": ["HR", "Finance", "Engineering", "Security", "Engineering"],
        "Role": ["HR Manager", "Controller", "Tech Lead", "Security Analyst", "Software Engineer"],
        "WorkEmail": ["john.doe@corp.com", "jane.smith@corp.com", "bob.johnson@corp.com", "alice.williams@corp.com", "charlie.brown@corp.com"]
    }
    pd.DataFrame(directory).to_csv(raw_dir / "hr_employee_directory.csv", index=False)
    ingest_document(raw_dir / "hr_employee_directory.csv", "HR", "Internal", ["Admin", "HR", "Finance", "Engineering", "Compliance"], "system")
    
    # 3. Code Repos
    repos = {
        "Repository": ["auth-service", "gateway-api", "rag-engine", "data-pipeline", "frontend-ui"],
        "Language": ["Python", "Go", "Python", "Scala", "TypeScript"],
        "ActiveBranch": ["main", "main", "develop", "main", "main"],
        "OpenPRs": [2, 1, 4, 0, 3],
        "Vulnerabilities": [0, 1, 0, 3, 2]
    }
    pd.DataFrame(repos).to_csv(raw_dir / "engineering_repo_inventory.csv", index=False)
    ingest_document(raw_dir / "engineering_repo_inventory.csv", "Engineering", "Internal", ["Admin", "Engineering"], "system")
    
    # 4. Security Vulnerabilities
    vulns = {
        "CVE_ID": ["CVE-2026-1011", "CVE-2026-1012", "CVE-2026-1013", "CVE-2026-1014", "CVE-2026-1015"],
        "Severity": ["Critical", "High", "Medium", "High", "Low"],
        "TargetSystem": ["Authentication Service", "Public Gateway", "User DB Cache", "Analytics API", "Static File Server"],
        "Status": ["Unpatched", "In Progress", "Patched", "Unpatched", "Patched"],
        "Owner": ["Charlie Brown", "Alice Williams", "Bob Johnson", "Alice Williams", "Charlie Brown"]
    }
    pd.DataFrame(vulns).to_csv(raw_dir / "security_vulnerabilities_tracker.csv", index=False)
    ingest_document(raw_dir / "security_vulnerabilities_tracker.csv", "Security", "Restricted", ["Admin", "Compliance"], "system")
    
    # 5. Controls Status
    controls = {
        "ControlID": ["CC-1.1", "CC-2.1", "CC-3.2", "CC-4.5", "CC-5.1"],
        "ControlName": ["Quarterly Access Reviews", "Weekly Firewall Scan", "Biometric Vault Logs", "Data Backup Frequency", "Vendor Risk Questionnaire"],
        "Framework": ["SOC 2", "ISO 27001", "SOC 2", "GDPR", "ISO 27001"],
        "Status": ["Compliant", "Compliant", "Non-Compliant", "Compliant", "Compliant"],
        "LastAudited": ["2026-03-15", "2026-05-20", "2026-04-01", "2026-05-01", "2026-05-15"]
    }
    pd.DataFrame(controls).to_csv(raw_dir / "compliance_controls_status.csv", index=False)
    ingest_document(raw_dir / "compliance_controls_status.csv", "Legal", "Internal", ["Admin", "HR", "Finance", "Engineering", "Compliance"], "system")
    
    logger.info("Generating 5 JSON logs...")
    
    # 1. Access logs
    acc_logs = [
        {"timestamp": "2026-06-05T08:12:00Z", "event": "Unsuccessful Login Attempt", "username": "bob", "ip_address": "192.168.1.45", "status": "Failed"},
        {"timestamp": "2026-06-05T09:30:15Z", "event": "Resource Access", "username": "alice", "resource": "HR_Salary_Bands_Confidential.pdf", "status": "Success"},
        {"timestamp": "2026-06-05T10:15:22Z", "event": "API Key Request", "username": "charlie", "client": "gateway-api", "status": "Success"},
        {"timestamp": "2026-06-05T11:45:00Z", "event": "Resource Access Attempt", "username": "bob", "resource": "HR_Salary_Bands_Confidential.pdf", "status": "Denied"}
    ]
    with open(raw_dir / "security_access_logs.json", "w") as f:
        json.dump(acc_logs, f, indent=2)
    ingest_document(raw_dir / "security_access_logs.json", "Security", "Restricted", ["Admin", "Compliance"], "system")
    
    # 2. Audit Trail
    trail = [
        {"action": "role_change", "operator": "admin", "target_user": "bob", "old_role": "Finance", "new_role": "Admin", "timestamp": "2026-06-04T14:20:00Z"},
        {"action": "document_deletion", "operator": "admin", "target_doc": "finance_forecast_2025.pdf", "timestamp": "2026-06-04T16:05:10Z"},
        {"action": "policy_bypass", "operator": "david", "bypass_id": "BY-901", "reason": "Emergency incident triage", "timestamp": "2026-06-05T01:30:00Z"}
    ]
    with open(raw_dir / "audit_trail_database.json", "w") as f:
        json.dump(trail, f, indent=2)
    ingest_document(raw_dir / "audit_trail_database.json", "Security", "Restricted", ["Admin", "Compliance"], "system")
    
    # 3. Performance
    perf = [
        {"timestamp": "2026-06-05T21:00:00Z", "service": "rag-engine", "cpu_percent": 34.2, "memory_used_mb": 512, "latency_ms": 122.4},
        {"timestamp": "2026-06-05T21:05:00Z", "service": "rag-engine", "cpu_percent": 56.1, "memory_used_mb": 528, "latency_ms": 195.8},
        {"timestamp": "2026-06-05T21:10:00Z", "service": "rag-engine", "cpu_percent": 41.5, "memory_used_mb": 520, "latency_ms": 150.1}
    ]
    with open(raw_dir / "system_performance_logs.json", "w") as f:
        json.dump(perf, f, indent=2)
    ingest_document(raw_dir / "system_performance_logs.json", "Security", "Internal", ["Admin", "HR", "Finance", "Engineering", "Compliance"], "system")
    
    # 4. API Logs
    api = [
        {"method": "POST", "path": "/api/v1/chat", "status_code": 200, "user": "charlie", "timestamp": "2026-06-05T22:00:00Z"},
        {"method": "GET", "path": "/api/v1/documents", "status_code": 200, "user": "alice", "timestamp": "2026-06-05T22:01:10Z"},
        {"method": "POST", "path": "/api/v1/users", "status_code": 403, "user": "bob", "timestamp": "2026-06-05T22:02:15Z"}
    ]
    with open(raw_dir / "api_request_logs.json", "w") as f:
        json.dump(api, f, indent=2)
    ingest_document(raw_dir / "api_request_logs.json", "Security", "Internal", ["Admin", "HR", "Finance", "Engineering", "Compliance"], "system")
    
    # 5. Incidents
    inc = [
        {"incident_id": "INC-889", "summary": "Brute force attack on admin endpoint", "status": "Mitigated", "owner": "Alice Williams", "resolved_at": "2026-06-05T10:45:00Z"},
        {"incident_id": "INC-890", "summary": "Anomalous database query volume", "status": "Investigating", "owner": "David Compliance", "resolved_at": None}
    ]
    with open(raw_dir / "incident_response_logs.json", "w") as f:
        json.dump(inc, f, indent=2)
    ingest_document(raw_dir / "incident_response_logs.json", "Security", "Restricted", ["Admin", "Compliance"], "system")
    
    logger.info("Seeding data successfully completed!")

if __name__ == "__main__":
    run_generation()
