"""
generate_sample_policies.py

Generates 10 realistic corporate policy PDF documents for testing 
and benchmarking an Enterprise Agentic RAG pipeline.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

# Ensure destination directory exists
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Define dataset of 10 organization policies
POLICIES = [
    {
        "filename": "POL-HR-001_Remote_Work_Policy.pdf",
        "title": "Remote Work and Telecommuting Policy",
        "code": "POL-HR-001",
        "effective_date": "January 1, 2026",
        "department": "Human Resources",
        "content": [
            ("1. Purpose", "This policy outlines eligibility, responsibilities, and guidelines for employees authorized to work remotely or follow a hybrid schedule."),
            ("2. Eligibility", "Full-time employees who have completed their initial 90-day probationary period are eligible for hybrid or fully remote arrangements with manager approval."),
            ("3. Core Working Hours", "All remote personnel must remain accessible on Microsoft Teams and email during core operational hours: 10:00 AM to 4:00 PM local time."),
            ("4. Home Office Stipend", "Eligible full-time employees receive a one-time equipment reimbursement of up to $500 for ergonomic chairs, monitors, and workspace essentials."),
            ("5. Data Protection", "Remote work must take place on company-issued laptops. Using personal computers or unsecured public Wi-Fi networks without an approved VPN is strictly prohibited.")
        ]
    },
    {
        "filename": "POL-HR-002_Annual_and_Sick_Leave_Policy.pdf",
        "title": "Annual and Sick Leave Policy",
        "code": "POL-HR-002",
        "effective_date": "January 1, 2026",
        "department": "Human Resources",
        "content": [
            ("1. Paid Time Off (PTO)", "Employees accrue 1.75 days of paid annual leave per month, totaling 21 calendar days of annual vacation per calendar year."),
            ("2. Sick Leave Allocation", "Employees are granted 10 paid sick days annually on January 1st. Consecutive sick leave exceeding 3 business days requires a physician's medical certificate."),
            ("3. Carryover Rules", "A maximum of 5 unused annual leave days may be carried over into the following calendar year. Any remaining balance beyond 5 days is forfeited on March 31st."),
            ("4. Advance Notice", "Planned leaves exceeding 3 consecutive days must be submitted in the HRMS at least two weeks in advance for supervisor approval.")
        ]
    },
    {
        "filename": "POL-IT-003_Information_Security_Policy.pdf",
        "title": "Information Security and Acceptable Use Policy",
        "code": "POL-IT-003",
        "effective_date": "February 1, 2026",
        "department": "Information Technology",
        "content": [
            ("1. Password Standards", "Passwords must be at least 14 characters long and include uppercase, lowercase, numerical, and special characters. Passwords expire every 90 days."),
            ("2. Multi-Factor Authentication (MFA)", "MFA is mandatory across all enterprise accounts, email inboxes, and internal VPN connections."),
            ("3. Unauthorized Software", "Employees may not install third-party applications, browser extensions, or torrent clients on corporate assets without explicit written authorization from IT."),
            ("4. Incident Reporting", "Any suspected phishing email, lost hardware, or data compromise must be reported to security@company.com within 60 minutes.")
        ]
    },
    {
        "filename": "POL-ETH-004_Code_of_Conduct.pdf",
        "title": "Code of Business Conduct and Ethics",
        "code": "POL-ETH-004",
        "effective_date": "January 15, 2026",
        "department": "Legal & Compliance",
        "content": [
            ("1. Standard of Integrity", "Employees must act with honesty, fairness, and transparency in all corporate dealings, avoiding actual or perceived conflicts of interest."),
            ("2. Gifts and Entertainment", "Gifts from vendors or partners exceeding $50 in value must be disclosed and approved by the Compliance Officer. Cash or cash equivalents may never be accepted."),
            ("3. Outside Employment", "Secondary employment, consulting contracts, or board memberships require prior review to ensure no conflict with primary company duties.")
        ]
    },
    {
        "filename": "POL-FIN-005_Travel_and_Expense_Policy.pdf",
        "title": "Business Travel and Expense Reimbursement Policy",
        "code": "POL-FIN-005",
        "effective_date": "March 1, 2026",
        "department": "Finance",
        "content": [
            ("1. Air Travel", "Economy class is required for domestic flights and international flights under 6 hours duration. Business class requires VP-level pre-authorization."),
            ("2. Lodging Limits", "Standard hotel reimbursements are capped at $200 per night for standard tier cities and $300 per night for high-cost metropolitan areas."),
            ("3. Per Diem Meals", "A daily meal allowance of $75 is provided for approved business travel. Itemized receipts are required for all meal expense claims above $25."),
            ("4. Submission Window", "Expense reports must be filed within 30 days of trip completion via the corporate finance portal.")
        ]
    },
    {
        "filename": "POL-BEN-006_Health_and_Wellness_Benefits.pdf",
        "title": "Employee Health Insurance and Wellness Benefits",
        "code": "POL-BEN-006",
        "effective_date": "January 1, 2026",
        "department": "Benefits Administration",
        "content": [
            ("1. Medical Coverage", "The company covers 90% of employee healthcare premiums and 70% of dependent coverage for medical, dental, and vision plans."),
            ("2. Wellness Stipend", "Full-time personnel are eligible for a $50 monthly wellness stipend covering gym memberships, fitness trackers, or mental wellness app subscriptions."),
            ("3. Employee Assistance Program (EAP)", "Confidential counseling sessions and financial planning assistance are available 24/7 at no cost to all employees and immediate family members.")
        ]
    },
    {
        "filename": "POL-HR-007_Parental_Leave_Policy.pdf",
        "title": "Parental and Family Support Leave Policy",
        "code": "POL-HR-007",
        "effective_date": "January 1, 2026",
        "department": "Human Resources",
        "content": [
            ("1. Primary Caregiver Leave", "Employees welcoming a child through birth or adoption are eligible for up to 16 weeks of 100% paid primary caregiver leave."),
            ("2. Secondary Caregiver Leave", "Secondary caregivers are entitled to 4 weeks of fully paid leave, which can be taken within the first 12 months following birth or placement."),
            ("3. Phased Return Program", "Returning parents can elect a temporary 80% working schedule during their first month back at full salary to facilitate childcare transitions.")
        ]
    },
    {
        "filename": "POL-HR-008_Performance_Review_Framework.pdf",
        "title": "Performance Review and Promotion Guidelines",
        "code": "POL-HR-008",
        "effective_date": "April 1, 2026",
        "department": "Talent Development",
        "content": [
            ("1. Review Cycles", "Formal performance assessments occur twice annually: Mid-Year Check-in (June) and Annual Evaluation (December)."),
            ("2. Evaluation Metrics", "Staff are assessed across two criteria: Key Performance Indicators / Deliverables (70%) and Core Cultural Values & Collaboration (30%)."),
            ("3. Promotion Eligibility", "To qualify for promotion consideration, an employee must have maintained a 'Consistently Exceeds Expectations' rating for at least two consecutive evaluation cycles.")
        ]
    },
    {
        "filename": "POL-LEG-009_Anti_Harassment_Policy.pdf",
        "title": "Anti-Harassment, Discrimination, and Grievance Policy",
        "code": "POL-LEG-009",
        "effective_date": "January 1, 2026",
        "department": "Legal & Human Resources",
        "content": [
            ("1. Zero Tolerance", "The company maintains an absolute zero-tolerance policy regarding sexual harassment, racial discrimination, verbal abuse, or retaliation of any kind."),
            ("2. Reporting Mechanisms", "Incidents can be reported directly to HR, a trusted supervisor, or via the anonymous 24/7 Ethics Hotline (1-800-555-0199)."),
            ("3. Investigation Protocol", "All filed complaints are initiated for formal investigation within 48 business hours. Retaliation against any reporting individual results in immediate termination.")
        ]
    },
    {
        "filename": "POL-HR-010_Separation_and_Notice_Period.pdf",
        "title": "Employee Separation and Notice Period Policy",
        "code": "POL-HR-010",
        "effective_date": "January 1, 2026",
        "department": "Human Resources",
        "content": [
            ("1. Standard Notice Period", "Individual contributors are required to provide 30 calendar days of written notice upon resignation. Team leads, managers, and directors must provide 60 calendar days."),
            ("2. Notice Buyout Option", "Early release before completion of notice period requires formal manager approval and may involve salary adjustments for unserved notice days."),
            ("3. Equipment & Access Handover", "All corporate laptops, security access badges, and confidential documents must be returned to HR on or before the designated final relieving date.")
        ]
    }
]

def build_pdf(policy_data: dict):
    """Compiles policy dictionary into a formatted PDF using ReportLab."""
    filepath = os.path.join(OUTPUT_DIR, policy_data["filename"])
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=6
    )
    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4A5568"),
        spaceAfter=14
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=8
    )

    story = []

    # Title & Metadata
    story.append(Paragraph(policy_data["title"], title_style))
    metadata_line = f"<b>Document Code:</b> {policy_data['code']} | <b>Department:</b> {policy_data['department']} | <b>Effective Date:</b> {policy_data['effective_date']}"
    story.append(Paragraph(metadata_line, meta_style))
    story.append(Spacer(1, 10))

    # Policy Sections
    for section_title, section_body in policy_data["content"]:
        story.append(Paragraph(section_title, heading_style))
        story.append(Paragraph(section_body, body_style))
        story.append(Spacer(1, 4))

    # Build the document
    doc.build(story)
    print(f"Generated: {filepath}")

def main():
    print("=" * 60)
    print("Generating 10 Sample Corporate Policy PDF Documents...")
    print("=" * 60)
    for policy in POLICIES:
        build_pdf(policy)
    print(f"\nAll 10 PDFs successfully created in './{OUTPUT_DIR}/'.")

if __name__ == "__main__":
    main()