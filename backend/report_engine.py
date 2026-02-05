# filename: report_engine.py (SAVE THIS FILE)

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def generate_pdf_bytes(filename, findings):
    """
    Generates a PDF report in memory and returns the binary data.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # 1. Header
    title = Paragraph(f"DPDP Compliance Audit Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    subtitle = Paragraph(f"Target File: {filename}", styles['Heading2'])
    story.append(subtitle)
    story.append(Spacer(1, 24))

    # 2. Summary
    if not findings:
        story.append(Paragraph("✅ STATUS: COMPLIANT", styles['Heading3']))
        story.append(Paragraph("No Personally Identifiable Information (PII) detected.", styles['Normal']))
    else:
        story.append(Paragraph(f"⚠️ STATUS: NON-COMPLIANT (Risk Level: HIGH)", styles['Heading3']))
        story.append(Paragraph(f"Total Leaks Found: {len(findings)}", styles['Normal']))
    
    story.append(Spacer(1, 24))

    # 3. The Table Data
    if findings:
        # Table Header
        data = [['Violation Type', 'Line No', 'Masked Data']]
        
        # Table Rows
        for f in findings:
            # --- FIX STARTS HERE ---
            # Check if 'f' is a Pydantic object (has .dict() method) or a standard dictionary
            # This makes the code work for both manual scripts and API calls
            if hasattr(f, 'dict'):
                row = f.dict()
            else:
                row = f
            
            data.append([row['type'], str(row['line']), row['value_masked']])
            # --- FIX ENDS HERE ---

        # Table Styling (Keep the rest the same)
        table = Table(data, colWidths=[120, 180, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue), # Header Color
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),   # Row Color
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        
        story.append(Spacer(1, 24))
        story.append(Paragraph("ACTION REQUIRED: Encrypt or anonymize the data above immediately to comply with DPDP Act 2023.", styles['BodyText']))

    # 4. Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer