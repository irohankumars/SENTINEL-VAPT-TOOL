from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

def render_pdf(scan, findings, summary, tools, project) -> bytes:
    out = BytesIO()
    doc = SimpleDocTemplate(out, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Severity", parent=styles["Normal"], textColor=colors.HexColor("#991b1b"), fontSize=9, spaceAfter=4))
    story = [Paragraph("SentinelVAPT", styles["Title"]), Paragraph("Security Assessment Report", styles["Heading2"]), Spacer(1, 8), Paragraph(f"<b>Project:</b> {project.name if project else 'Unassigned assessment'}<br/><b>Target:</b> {scan.target_url}<br/><b>Scan date:</b> {scan.started_at or 'Not started'}<br/><b>Duration:</b> {scan.duration or 0} seconds<br/><b>Tools:</b> {', '.join(tools)}", styles["BodyText"]), Spacer(1, 14)]
    data = [[name, str(count)] for name, count in summary.items()]
    table = Table([["Severity", "Count"], *data], colWidths=[55*mm, 25*mm])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#991b1b")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.4,colors.grey),("PADDING",(0,0),(-1,-1),6)]))
    story += [table, Spacer(1, 18), Paragraph("Detailed Findings", styles["Heading2"])]
    for index, f in enumerate(findings):
        if index and index % 3 == 0: story.append(PageBreak())
        safe = lambda value: str(value or "Not supplied").replace("&", "&amp;").replace("<", "&lt;")
        story += [Paragraph(f.severity.upper(), styles["Severity"]), Paragraph(safe(f.title), styles["Heading3"]), Paragraph(f"<b>URL:</b> {safe(f.url)}<br/><b>Tool:</b> {safe(f.tool)} · <b>CWE:</b> {safe(f.cwe)} · <b>CVSS:</b> {safe(f.cvss)}<br/><b>Description:</b> {safe(f.description)}<br/><b>Evidence:</b> {safe(f.evidence)}<br/><b>Impact:</b> {safe(f.impact)}<br/><b>Remediation:</b> {safe(f.remediation)}", styles["BodyText"]), Spacer(1, 14)]
    doc.build(story)
    return out.getvalue()
