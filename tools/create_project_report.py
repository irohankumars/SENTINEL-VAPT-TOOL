from pathlib import Path
from datetime import date
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SentinelVAPT_Project_Report.docx"
ASSETS = ROOT / "tools" / "report_assets"
ASSETS.mkdir(parents=True, exist_ok=True)

NAVY = "17365D"; BLUE = "DCE6F1"; PALE = "F4F7FA"; GRID = "D9D9D9"; BLACK = "000000"; WHITE = "FFFFFF"

def font(name="Arial", size=24):
    try: return ImageFont.truetype("arial.ttf", size)
    except: return ImageFont.load_default()

def diagram(filename, title, columns, arrows):
    w,h=1500,820
    im=Image.new("RGB",(w,h),"white"); d=ImageDraw.Draw(im)
    d.text((w//2,35),title,fill="#111827",font=font(size=36),anchor="ma")
    boxes={}
    for label,x,y,bw,bh,color in columns:
        d.rounded_rectangle((x,y,x+bw,y+bh),radius=18,fill=color,outline="#334155",width=3)
        wrapped=[]; words=label.split(); line=""
        for word in words:
            if len(line+" "+word)>22: wrapped.append(line); line=word
            else: line=(line+" "+word).strip()
        if line: wrapped.append(line)
        yy=y+bh/2-(len(wrapped)-1)*18
        for i,t in enumerate(wrapped): d.text((x+bw/2,yy+i*36),t,fill="#111827",font=font(size=25),anchor="mm")
        boxes[label]=(x,y,bw,bh)
    for a,b in arrows:
        ax,ay,aw,ah=boxes[a]; bx,by,bw,bh=boxes[b]
        x1,y1=ax+aw/2,ay+ah/2; x2,y2=bx+bw/2,by+bh/2
        if abs(x2-x1)>abs(y2-y1): x1=ax+aw if x2>x1 else ax; x2=bx if x2>x1 else bx+bw
        else: y1=ay+ah if y2>y1 else ay; y2=by if y2>y1 else by+bh
        d.line((x1,y1,x2,y2),fill="#8B1E1E",width=5)
        import math
        ang=math.atan2(y2-y1,x2-x1)
        pts=[(x2,y2),(x2-18*math.cos(ang-.55),y2-18*math.sin(ang-.55)),(x2-18*math.cos(ang+.55),y2-18*math.sin(ang+.55))]
        d.polygon(pts,fill="#8B1E1E")
    path=ASSETS/filename; im.save(path); return path

figures=[]
figures.append(diagram("architecture.png","SentinelVAPT System Architecture",[
    ("React and Vite Frontend",540,110,420,95,"#DCE6F1"),("FastAPI REST Backend",540,260,420,95,"#DCE6F1"),("Application Services",180,420,330,95,"#EAF2F8"),("SQLite Database",585,420,330,95,"#EAF2F8"),("Report Generators",990,420,330,95,"#EAF2F8"),("HTTP Scanner",80,620,260,90,"#FDEDEC"),("Nuclei Adapter",410,620,260,90,"#FDEDEC"),("ZAP Adapter",740,620,260,90,"#FDEDEC"),("PDF and HTML",1070,620,260,90,"#FDEDEC")],[("React and Vite Frontend","FastAPI REST Backend"),("FastAPI REST Backend","Application Services"),("FastAPI REST Backend","SQLite Database"),("FastAPI REST Backend","Report Generators"),("Application Services","HTTP Scanner"),("Application Services","Nuclei Adapter"),("Application Services","ZAP Adapter"),("Report Generators","PDF and HTML")]))
figures.append(diagram("scan_flow.png","Scan Execution Workflow",[("Create Scan",40,330,190,85,"#DCE6F1"),("Validate Target",270,330,190,85,"#DCE6F1"),("Background Execution",500,330,210,85,"#EAF2F8"),("Run Selected Scanners",750,330,220,85,"#EAF2F8"),("Normalize and Deduplicate",1010,330,230,85,"#FDEDEC"),("Persist and Complete",1280,330,180,85,"#FDEDEC")],[("Create Scan","Validate Target"),("Validate Target","Background Execution"),("Background Execution","Run Selected Scanners"),("Run Selected Scanners","Normalize and Deduplicate"),("Normalize and Deduplicate","Persist and Complete")]))
figures.append(diagram("database.png","Database Relationship Model",[("Project",120,280,330,190,"#DCE6F1"),("Scan",585,280,330,190,"#EAF2F8"),("Finding",1050,280,330,190,"#FDEDEC")],[("Project","Scan"),("Scan","Finding")]))
figures.append(diagram("finding_flow.png","Finding Processing Workflow",[("Scanner Output",50,330,210,85,"#DCE6F1"),("Parse",300,330,170,85,"#DCE6F1"),("Normalize Severity and Fields",510,330,260,85,"#EAF2F8"),("Rule Based Deduplication",810,330,250,85,"#EAF2F8"),("SHA 256 Fingerprint",1100,330,210,85,"#FDEDEC"),("Persist Finding",1350,330,120,85,"#FDEDEC")],[("Scanner Output","Parse"),("Parse","Normalize Severity and Fields"),("Normalize Severity and Fields","Rule Based Deduplication"),("Rule Based Deduplication","SHA 256 Fingerprint"),("SHA 256 Fingerprint","Persist Finding")]))
figures.append(diagram("report_flow.png","Report Generation Workflow",[("Completed Scan",160,310,230,90,"#DCE6F1"),("Load Project and Findings",470,310,280,90,"#EAF2F8"),("Severity Summary",830,210,240,90,"#FDEDEC"),("Detailed Findings",830,430,240,90,"#FDEDEC"),("PDF ReportLab",1160,210,220,90,"#DCE6F1"),("HTML Jinja2",1160,430,220,90,"#DCE6F1")],[("Completed Scan","Load Project and Findings"),("Load Project and Findings","Severity Summary"),("Load Project and Findings","Detailed Findings"),("Severity Summary","PDF ReportLab"),("Detailed Findings","HTML Jinja2")]))
figures.append(diagram("security_flow.png","Target Security Validation Flow",[("Submitted URL",70,330,200,85,"#DCE6F1"),("HTTP or HTTPS",320,330,210,85,"#EAF2F8"),("Reject Embedded Credentials",580,330,240,85,"#EAF2F8"),("Resolve Hostname",870,330,210,85,"#FDEDEC"),("Check Address Class",1130,330,210,85,"#FDEDEC"),("Allow Public Target",1380,330,100,85,"#DCE6F1")],[("Submitted URL","HTTP or HTTPS"),("HTTP or HTTPS","Reject Embedded Credentials"),("Reject Embedded Credentials","Resolve Hostname"),("Resolve Hostname","Check Address Class"),("Check Address Class","Allow Public Target")]))

doc=Document()
sec=doc.sections[0]; sec.page_height=Cm(29.7); sec.page_width=Cm(21); sec.top_margin=Cm(2.2); sec.bottom_margin=Cm(2.0); sec.left_margin=Cm(2.6); sec.right_margin=Cm(2.2); sec.different_first_page_header_footer=True
styles=doc.styles
styles["Normal"].font.name="Times New Roman"; styles["Normal"]._element.rPr.rFonts.set(qn("w:ascii"),"Times New Roman"); styles["Normal"]._element.rPr.rFonts.set(qn("w:hAnsi"),"Times New Roman"); styles["Normal"].font.size=Pt(11)
styles["Normal"].paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY; styles["Normal"].paragraph_format.line_spacing=1.25; styles["Normal"].paragraph_format.space_after=Pt(6)
for name,size in [("Title",22),("Heading 1",16),("Heading 2",13),("Heading 3",12)]:
    s=styles[name]; s.font.name="Times New Roman"; s._element.rPr.rFonts.set(qn("w:ascii"),"Times New Roman"); s._element.rPr.rFonts.set(qn("w:hAnsi"),"Times New Roman"); s.font.size=Pt(size); s.font.bold=True; s.font.color.rgb=RGBColor(0,0,0)
    s.paragraph_format.space_before=Pt(10); s.paragraph_format.space_after=Pt(7); s.paragraph_format.keep_with_next=True
styles["Caption"].font.name="Times New Roman"; styles["Caption"].font.size=Pt(10); styles["Caption"].font.italic=True; styles["Caption"].font.color.rgb=RGBColor(0,0,0)

header=sec.header.paragraphs[0]; header.alignment=WD_ALIGN_PARAGRAPH.CENTER; hr=header.add_run("SENTINELVAPT | WEB APPLICATION VULNERABILITY ASSESSMENT PLATFORM"); hr.bold=True; hr.font.name="Times New Roman"; hr.font.size=Pt(9)
footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
fr=footer.add_run("SentinelVAPT Project Report | Department of Information Science and Engineering | Page "); fr.font.name="Times New Roman"; fr.font.size=Pt(9)
fld=OxmlElement("w:fldSimple"); fld.set(qn("w:instr"),"PAGE"); footer._p.append(fld)

def page_break(): doc.add_page_break()
def p(text="",bold_lead=None,center=False,italic=False):
    para=doc.add_paragraph(); para.alignment=WD_ALIGN_PARAGRAPH.CENTER if center else WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_lead and text.startswith(bold_lead):
        r=para.add_run(bold_lead); r.bold=True; para.add_run(text[len(bold_lead):])
    else: para.add_run(text)
    if italic:
        for r in para.runs:r.italic=True
    return para
def bullet(text,level=0):
    para=doc.add_paragraph(text,style="List Bullet" if level==0 else "List Bullet 2"); para.paragraph_format.space_after=Pt(3); return para
def heading(text,level=1): return doc.add_heading(text,level=level)
def caption(text):
    para=doc.add_paragraph(text,style="Caption"); para.alignment=WD_ALIGN_PARAGRAPH.CENTER; para.paragraph_format.keep_with_next=False
def set_cell(cell, text, bold=False, color=None, align=WD_ALIGN_PARAGRAPH.LEFT):
    cell.text=""; para=cell.paragraphs[0]; para.alignment=align; run=para.add_run(str(text)); run.bold=bold; run.font.name="Times New Roman"; run.font.size=Pt(9); run.font.color.rgb=RGBColor.from_string(color or BLACK); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
    tcPr=cell._tc.get_or_add_tcPr(); mar=tcPr.first_child_found_in("w:tcMar")
    if mar is None: mar=OxmlElement("w:tcMar"); tcPr.append(mar)
    for side in ("top","left","bottom","right"):
        el=OxmlElement("w:"+side); el.set(qn("w:w"),"90"); el.set(qn("w:type"),"dxa"); mar.append(el)
def table(caption_text, headers, rows, widths=None):
    caption(caption_text)
    t=doc.add_table(rows=1,cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
    for i,h in enumerate(headers):
        set_cell(t.rows[0].cells[i],h,True,WHITE,WD_ALIGN_PARAGRAPH.CENTER); shd=OxmlElement("w:shd"); shd.set(qn("w:fill"),NAVY); t.rows[0].cells[i]._tc.get_or_add_tcPr().append(shd)
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,val in enumerate(row):
            set_cell(cells[i],val,False,None,WD_ALIGN_PARAGRAPH.CENTER if len(str(val))<18 else WD_ALIGN_PARAGRAPH.LEFT)
            if ri%2: shd=OxmlElement("w:shd"); shd.set(qn("w:fill"),PALE); cells[i]._tc.get_or_add_tcPr().append(shd)
    if widths:
        for row in t.rows:
            for i,w in enumerate(widths): row.cells[i].width=Cm(w)
    for row in t.rows:
        trPr=row._tr.get_or_add_trPr()
        if row is t.rows[0]: rep=OxmlElement("w:tblHeader"); rep.set(qn("w:val"),"true"); trPr.append(rep)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
    return t
def add_figure(path,text,width=6.5):
    para=doc.add_paragraph(); para.alignment=WD_ALIGN_PARAGRAPH.CENTER; para.paragraph_format.keep_with_next=True; para.add_run().add_picture(str(path),width=Inches(width)); caption(text)
def chapter(title):
    para=heading(title,1)
    para.paragraph_format.page_break_before=True

# Cover
for _ in range(2): doc.add_paragraph()
q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=q.add_run("AKSHAYA INSTITUTE OF TECHNOLOGY"); r.bold=True; r.font.size=Pt(17)
p("DEPARTMENT OF INFORMATION SCIENCE AND ENGINEERING",center=True); doc.add_paragraph()
p("PROJECT REPORT",center=True); doc.add_paragraph()
q=doc.add_paragraph(style="Title"); q.alignment=WD_ALIGN_PARAGRAPH.CENTER; q.add_run("SENTINELVAPT")
q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=q.add_run("WEB BASED VULNERABILITY ASSESSMENT\nAND REPORTING PLATFORM"); r.bold=True; r.font.size=Pt(16)
doc.add_paragraph(); p("Submitted in partial fulfilment of the requirements\nfor the award of the degree of\nBachelor of Engineering\nin\nInformation Science and Engineering",center=True)
doc.add_paragraph(); p("Submitted by",center=True); q=doc.add_paragraph(); q.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=q.add_run("ROHAN"); r.bold=True; r.font.size=Pt(14)
p("University Seat Number: ____________________",center=True); p("Project Guide: ____________________",center=True)
doc.add_paragraph(); p("Academic Year 2026",center=True)

page_break(); heading("Certificate",1)
p("This is to certify that the project report entitled SentinelVAPT Web Based Vulnerability Assessment and Reporting Platform is a record of project work carried out by ROHAN in the Department of Information Science and Engineering, Akshaya Institute of Technology, during the academic year 2026, in partial fulfilment of the requirements for the award of the Bachelor of Engineering degree in Information Science and Engineering.")
p("The work represented in this report describes the implementation available in the submitted repository at the time of evaluation. It has been examined with respect to the stated project objectives and current prototype scope.")
doc.add_paragraph(); doc.add_paragraph(); table("",["Project Guide","Head of Department","Principal"],[["Signature: __________","Signature: __________","Signature: __________"],["Name: __________","Name: __________","Name: __________"]],[5.2,5.2,5.2])

page_break(); heading("Declaration",1)
p("I, ROHAN, declare that the project report entitled SentinelVAPT Web Based Vulnerability Assessment and Reporting Platform is an account of the engineering work carried out by me during the academic year 2026. The implementation, observations, testing results, limitations and completion estimates stated in this report correspond to the project repository examined for this submission.")
p("The work has not been presented as a complete commercial vulnerability assessment product. External standards and tool documentation used for technical context are acknowledged in the reference section. No registration number, guide name or faculty identity has been assumed where that information was unavailable.")
doc.add_paragraph(); p("Place: ____________________",center=False); p("Date: ____________________",center=False); p("Signature of Student: ____________________",center=False)

page_break(); heading("Acknowledgement",1)
p("I express my gratitude to the Department of Information Science and Engineering, Akshaya Institute of Technology, for providing the academic setting in which this project was developed. The project required the integration of frontend engineering, backend API development, database design, defensive web assessment, report generation and software testing. Working across these areas helped convert a security-tool concept into a functioning prototype whose present strengths and limitations can be measured directly.")
p("I also acknowledge the maintainers and contributors of the open-source technologies and public security guidance used during the work, including FastAPI, React, SQLAlchemy, OWASP guidance, NIST publications, ProjectDiscovery Nuclei, OWASP ZAP, ReportLab and Jinja2. These resources supplied standards, implementation tools and reference material without which the current prototype would not have been practical.")

page_break(); heading("Abstract",1)
p("SentinelVAPT is a web-based vulnerability assessment and reporting prototype intended to make a small, authorized assessment workflow easier to organize and understand. The implemented system combines a React and Vite frontend with a FastAPI backend, SQLAlchemy persistence and an SQLite development database. It supports project creation and maintenance, scan configuration, asynchronous scan execution, progress tracking, cancellation, finding management, dashboard aggregation and generation of PDF and HTML assessment reports. The project does not attempt autonomous exploitation or claim complete vulnerability coverage.")
p("The current scanner layer contains a built-in defensive HTTP scanner and isolated adapters for ProjectDiscovery Nuclei, ProjectDiscovery httpx and OWASP ZAP. The HTTP scanner performs safe GET-based observations for missing security headers, HTTPS-related configuration, server header disclosure and cookie attributes. It applies connection and redirect limits, response-size restrictions and timeouts. Target controls reject malformed or unsupported URLs, credential-bearing URLs and restricted network destinations by default. Scanner outputs are normalized to one finding structure, assigned deterministic severity labels, deduplicated by target and finding identity, fingerprinted with SHA-256 and persisted under the related scan.")
p("The backend exposes REST endpoints for projects, scans, findings, dashboard data and completed-scan reports. Optional AI explanations do not participate in scanning and remain disabled when no compatible API credentials are supplied. Testing covers CRUD operations, mock scan completion, cancellation, failure persistence, filtering, status transitions, deduplication, report generation, dashboard aggregation, security headers, target restrictions and controlled scanner-adapter behavior. The latest verification executed twelve tests: twelve passed, none failed and none were skipped. The frontend production build and backend compilation also passed. Live Nuclei, ZAP and ProjectDiscovery httpx execution could not be verified because those external tools were unavailable. On the basis of implemented functionality and known gaps, overall completion is estimated at approximately 72 percent. SentinelVAPT is therefore best described as a tested engineering prototype with meaningful defensive functionality and a defined path toward persistent workers, authentication, broader live-scanner validation and multi-user deployment.")

page_break(); heading("Table of Contents",1)
toc=doc.add_paragraph(); fld=OxmlElement("w:fldSimple"); fld.set(qn("w:instr"),'TOC \\o "1-3" \\h \\z \\u'); toc._p.append(fld)
heading("List of Figures",1)
for i,t in enumerate(["SentinelVAPT System Architecture","Scan Execution Workflow","Database Relationship Model","Finding Processing Workflow","Report Generation Workflow","Target Security Validation Flow"],1): p(f"Figure {i}: {t}")
heading("List of Tables",1)
for i,t in enumerate(["Related standards and tools","Functional requirements","Non-functional requirements","Database entities","API endpoints","Technology stack","Scanner capabilities","Build verification","Functional test coverage","Security regression tests","Defects found and corrected","Current completion assessment","Future enhancement roadmap"],1): p(f"Table {i}: {t}")
page_break(); heading("List of Abbreviations",1)
table("",["Abbreviation","Expansion"],[["API","Application Programming Interface"],["ASVS","Application Security Verification Standard"],["CORS","Cross-Origin Resource Sharing"],["CSP","Content Security Policy"],["CVSS","Common Vulnerability Scoring System"],["CWE","Common Weakness Enumeration"],["HTTP","Hypertext Transfer Protocol"],["HSTS","HTTP Strict Transport Security"],["ORM","Object Relational Mapper"],["REST","Representational State Transfer"],["SSRF","Server-Side Request Forgery"],["VAPT","Vulnerability Assessment and Penetration Testing"],["WSTG","Web Security Testing Guide"],["ZAP","Zed Attack Proxy"]],[3.2,12.5])

chapter("Chapter 1 Introduction")
heading("1.1 Background",2)
p("Web applications expose business processes, information and user interactions through HTTP interfaces. Their security depends on correct behavior across application code, frameworks, deployment configuration, browser controls and supporting infrastructure. Vulnerability assessment is the structured process of observing these systems for weaknesses, documenting evidence and recommending corrective action. Penetration testing may extend assessment by attempting controlled exploitation, but SentinelVAPT deliberately remains focused on orchestration, non-destructive observation, result management and reporting.")
p("NIST SP 800-115 describes technical assessment as a planned activity that includes preparation, execution, analysis and mitigation-oriented reporting [1]. The OWASP Web Security Testing Guide similarly organizes web security testing into repeatable categories rather than treating tool output as a complete assessment [2]. These principles matter because automated scanners often produce heterogeneous results that vary in naming, severity and evidence. A usable assessment platform must retain target context, preserve scanner errors, normalize output and present remediation information in a form that can be reviewed.")
heading("1.2 Motivation",2)
p("The project was motivated by the practical difficulty of coordinating small web assessments across separate command-line tools. A learner may run reconnaissance, template-based checks and proxy-assisted scanning independently, then manually copy results into notes. That workflow makes it difficult to compare findings, track scan state, avoid duplicates and produce a consistent report. SentinelVAPT addresses this coordination problem through one local interface without attempting to replace expert judgment or established scanners.")
heading("1.3 Problem Statement",2)
p("The engineering problem is to design a compact platform that accepts an authorized HTTP or HTTPS target, manages a repeatable scan lifecycle, invokes selected defensive scanner adapters safely, converts heterogeneous output into a consistent finding model, stores the relationship between projects, scans and findings, and produces readable reports. The design must remain usable when optional external tools or an AI service are unavailable, and it must prevent straightforward misuse such as arbitrary command execution or scanning restricted network destinations by default.")
heading("1.4 Proposed Solution",2)
p("SentinelVAPT provides a React interface for project and finding management and a FastAPI service for persistence, scan orchestration and reporting. Scans begin in a pending state and run as FastAPI background tasks. The frontend polls scan state until completion, failure or cancellation. The built-in HTTP scanner provides real defensive observations, while the Nuclei, httpx and ZAP integrations remain isolated adapters. A mock mode produces deterministic development findings when external tools are unavailable.")
heading("1.5 Objectives",2)
for x in ["Provide understandable project CRUD and scan configuration workflows.","Persist scan state, progress, timestamps, tool selection, errors and findings.","Normalize scanner output into deterministic severities and shared fields.","Prevent obvious unsafe targets and protect scanner subprocess execution.","Support filtering and controlled status transitions for findings.","Generate reports only from the selected completed scan.","Remain operable without AI credentials or external scanner binaries.","Verify the implementation with repeatable build, API, security and adapter tests."]: bullet(x)
heading("1.6 Scope",2)
p("Current scope. The current repository implements project management, background mock scanning, a safe HTTP scanner, scanner adapters, finding persistence, dashboard aggregation, status updates, PDF and HTML reports, defensive target validation, frontend error states and automated regression tests.")
p("Future scope. Authentication, role-based authorization, persistent job workers, authenticated scanning, live external-tool qualification, broader vulnerability checks, multi-user operation and production database deployment remain future work. These items are not represented as current features.")

chapter("Chapter 2 Background and Related Work")
heading("2.1 Security Assessment Guidance",2)
p("NIST SP 800-115 supplies a useful methodological foundation because it separates planning, execution, analysis and mitigation activities [1]. SentinelVAPT reflects this sequence at a smaller scale: the operator defines a target and scan mode, the backend records and executes the scan, processors analyze and normalize results, and the report communicates evidence and remediation. The guide also emphasizes legal and policy considerations, which supports the platform's explicit authorized-use positioning.")
p("The OWASP WSTG is relevant as a structured catalogue of web testing practices and stable test identifiers [2]. SentinelVAPT does not claim to implement the WSTG in full. Its current HTTP checks cover only a limited configuration-oriented subset, while external adapters can contribute additional alerts. OWASP Top 10:2025 is used as an awareness context for major web application risks, not as a claim of automated coverage [3]. OWASP itself distinguishes Top 10 awareness material from the more verifiable control requirements of ASVS [4].")
heading("2.2 Verification and Risk Context",2)
p("OWASP ASVS 5.0 offers a basis for testing technical security controls and organizing secure development requirements [4]. It is relevant when future SentinelVAPT checks need traceable verification objectives. NIST CSF 2.0 addresses organizational cybersecurity outcomes rather than scanner implementation [5]; its relevance lies in communicating that assessment findings support wider identification, protection and improvement processes rather than replacing risk management.")
heading("2.3 Tool Context",2)
p("Nuclei uses YAML-based templates containing identifiers, metadata, protocol requests, matchers and extractors [6]. The SentinelVAPT adapter executes Nuclei through a controlled argument array, requests JSONL output, ignores malformed lines and maps valid records into the common finding structure. ZAP supplies passive, spider and active scanning capabilities and exposes an API suitable for automation [7]. SentinelVAPT checks ZAP connectivity, initiates the configured scan type, polls completion and normalizes alerts. Active mode remains an explicit operator choice because ZAP warns that active testing can affect a target [7].")
p("Research evaluating automated web scanners has repeatedly shown that automated results depend on scanner capability, configuration and the vulnerability class being tested. Bau et al. examined the state of automated black-box web vulnerability testing and demonstrated limitations across common weakness classes [8]. This supports the report's deliberate avoidance of complete-coverage claims.")
table("Table 1: Related standards and tools",["Source or approach","Purpose","Relevance to SentinelVAPT"],[["NIST SP 800-115","Technical assessment planning and execution","Supports planned, authorized testing and mitigation-focused reporting"],["OWASP WSTG","Web application testing practices","Provides structured testing context; not fully implemented"],["OWASP Top 10:2025","Awareness of major web application risks","Frames risk discussion without implying complete coverage"],["OWASP ASVS 5.0","Verifiable application security requirements","Potential basis for traceable checks and future assurance levels"],["NIST CSF 2.0","Cybersecurity risk outcomes","Connects assessment output to organizational risk processes"],["Nuclei documentation","Template-driven detection","Explains external adapter output and metadata"],["OWASP ZAP documentation","Proxy and automated web assessment","Explains passive, spider and active modes"],["Bau et al. 2010","Scanner effectiveness research","Supports cautious interpretation of automated coverage"]],[3.7,4.3,8.0])

chapter("Chapter 3 Requirements Analysis")
heading("3.1 Functional Requirements",2)
table("Table 2: Functional requirements",["ID","Requirement","Implementation evidence"],[["FR-01","Create, view, edit, search and delete projects","React project views and projects router CRUD endpoints"],["FR-02","Configure an HTTP or HTTPS scan","New scan view and ScanCreate schema"],["FR-03","Start and cancel scans","BackgroundTasks orchestration and cancellation flag"],["FR-04","Monitor progress and terminal states","Persisted progress/stage plus frontend polling"],["FR-05","View and filter findings","Findings API search and multiple query filters"],["FR-06","Change finding disposition","Validated open, confirmed, false positive and resolved states"],["FR-07","Aggregate dashboard metrics","Dedicated dashboard endpoint"],["FR-08","Generate PDF and HTML reports","ReportLab and Jinja2 generators for completed scans"],["FR-09","Operate without external scanners","MOCK_SCANNERS development mode"],["FR-10","Preserve scanner failures","Scan error_message and failed terminal state"]],[1.3,6.1,8.6])
heading("3.2 Non Functional Requirements",2)
table("Table 3: Non-functional requirements",["Quality","Current response","Limitation"],[["Security","Protocol checks, SSRF controls, size limits, shell-free subprocesses","No authentication or authorization"],["Reliability","Persisted terminal states, error handling and isolated tests","Background tasks do not survive restart"],["Maintainability","Separated routers, services, scanners, processors and schemas","Frontend remains concentrated in App.jsx"],["Performance","Connection limits and bounded response reads","SQLite and synchronous scanner calls limit concurrency"],["Usability","Responsive console UI, filters, modals and error states","No browser automation suite"],["Scalability","Simple local deployment and relational model","Not designed for distributed workers or enterprise tenants"]],[3.0,7.0,6.0])
heading("3.3 Hardware Requirements",2)
p("The development prototype requires a conventional x86-64 workstation capable of running Python, Node.js and a modern browser. A minimum of 4 GB RAM is sufficient for the core mock-mode application; additional memory and storage are required when running ZAP, large Nuclei template sets or multiple scans. Network access is required only for targets that the operator is authorized to assess and for optional external APIs.")
heading("3.4 Software Requirements",2)
p("The repository targets Python 3.12 or later and uses FastAPI, Uvicorn, SQLAlchemy, Pydantic, python-dotenv, httpx, ReportLab, Jinja2 and pytest. The frontend uses React, React Router, Vite and Lucide React with project-specific CSS. SQLite is the development database. External ProjectDiscovery httpx, Nuclei and OWASP ZAP installations are optional because mock mode and the built-in HTTP scanner permit development without them.")
heading("3.5 User Roles",2)
p("The current system has no complete authentication or authorization layer. It therefore does not implement administrator, analyst or viewer roles. The interface assumes a trusted local operator. Any discussion of multi-user roles belongs to future scope and must not be interpreted as implemented access control.")

chapter("Chapter 4 System Analysis and Design")
heading("4.1 Existing Approach",2)
p("A fragmented assessment workflow typically involves separate commands, output formats and handwritten reports. Tool failures may be lost, repeated findings may be copied more than once, and scan context may be disconnected from remediation. This approach is workable for an experienced tester but difficult to demonstrate, reproduce or maintain in a student project.")
heading("4.2 Proposed System",2)
p("SentinelVAPT coordinates the existing tools through a narrow backend contract. The frontend does not execute scanners. It creates persisted scan records and calls explicit start or cancel actions. Scanner adapters return data to a processing pipeline, and reports read persisted findings rather than transient console output. This separation improves traceability without introducing microservices or a distributed queue.")
heading("4.3 System Architecture",2); add_figure(figures[0],"Figure 1: SentinelVAPT System Architecture")
p("The frontend communicates exclusively through REST endpoints in the FastAPI application. Routers handle HTTP concerns, services coordinate business operations, scanners isolate external execution, processors normalize results, and SQLAlchemy manages SQLite persistence. Report generation is downstream of completed scan data.")
heading("4.4 Database Design",2); add_figure(figures[2],"Figure 3: Database Relationship Model",5.8)
table("Table 4: Database entities",["Entity","Important fields","Relationship"],[["Project","id, name, target_url, description, created_at, updated_at","Owns zero or more scans"],["Scan","id, project_id, target_url, status, mode, timestamps, duration, tools, progress, stage, error","Belongs to an optional project; owns findings"],["Finding","id, scan_id, title, severity, category, URL, tool, CWE, CVSS, evidence, impact, remediation, AI explanation, status, fingerprint","Belongs to one scan"]],[2.5,9.0,4.5])
heading("4.5 Data Flow",2); add_figure(figures[1],"Figure 2: Scan Execution Workflow")
p("The create endpoint stores a pending scan. The start endpoint changes it to running and schedules execution. The service validates and invokes selected scanners, updates progress and stage values, normalizes and deduplicates results, optionally requests an explanation, writes findings, and commits a completed or failed terminal state. Cancellation is represented by a persisted request flag checked between stages.")
heading("4.6 API Architecture",2)
table("Table 5: API endpoints",["Method","Endpoint","Purpose","Principal result"],[["GET","/api/health","Read service readiness","Status and mock-mode flag"],["GET","/api/dashboard","Aggregate current activity","Metrics, severity and recent records"],["GET/POST","/api/projects","List or create projects","Project representations"],["GET/PUT/DELETE","/api/projects/{id}","Read, update or delete a project","Project or 204"],["GET/POST","/api/scans","List or create scans","Scan representations"],["GET","/api/scans/{id}","Poll scan state","Progress, stage and error"],["POST","/api/scans/{id}/start","Begin background execution","Running scan"],["POST","/api/scans/{id}/cancel","Request cancellation","Updated scan"],["GET","/api/findings","Filter findings","Finding list"],["GET","/api/findings/{id}","Read finding detail","Finding"],["PATCH","/api/findings/{id}/status","Update controlled disposition","Updated finding"],["GET","/api/reports/{scan}/pdf","Download completed scan PDF","PDF response"],["GET","/api/reports/{scan}/html","Download completed scan HTML","HTML response"]],[1.6,5.1,6.3,3.2])

chapter("Chapter 5 Technology Stack")
table("Table 6: Technology stack",["Technology","Role in SentinelVAPT","Reason for use"],[["React","Renders all dashboard and workflow views","Component model and local state support"],["React Router","Maps dashboard, project, scan, finding, report, settings and 404 routes","Client-side navigation"],["Vite","Development server and production bundling","Fast compact frontend workflow"],["JavaScript and CSS","Frontend logic and existing visual system","Direct control without added state or CSS frameworks"],["Python","Backend and scanner implementation language","Readable services and broad library support"],["FastAPI","REST API, validation integration and background tasks","Typed endpoints and automatic documentation"],["Pydantic","Request and response schemas","Declarative validation"],["SQLAlchemy","ORM models, relationships and queries","Parameterized persistence"],["SQLite","Local development database","Simple file-based operation"],["httpx library","Built-in HTTP assessment and AI/ZAP requests","Timeouts, streaming and structured client API"],["Nuclei","Optional external template scanner","Structured JSONL findings"],["OWASP ZAP","Optional proxy/scanner integration","Passive, spider and active modes"],["ReportLab","PDF generation","Programmatic portable reports"],["Jinja2","HTML report generation","Readable templating"],["pytest","Automated regression tests","API and adapter verification"]],[3.0,6.2,6.0])
p("The current frontend does not use Tailwind CSS even though it appeared in an early design requirement. Styling is implemented in src/styles.css. Recording the actual implementation is important because dependency claims should match package.json and the source tree.")
heading("5.1 Interaction Between Technologies",2)
p("React uses src/services/api.js for JSON calls and downloads. FastAPI validates requests and queries SQLAlchemy. Services invoke scanner adapters, normalize findings, and select ReportLab or Jinja2 output; environment variables control integrations, CORS, timeouts and private-target behavior.")

chapter("Chapter 6 Implementation")
heading("6.1 Frontend Implementation",2)
p("The frontend is implemented primarily in src/App.jsx, supported by centralized mock data, an API service and a single stylesheet. A persistent sidebar and header wrap route-specific views for the dashboard, projects, project details, new scans, scan details, findings, finding details, reports, settings and unknown routes. The visual design uses near-black panels, red accents, compact typography and monospace metadata without changing into an entertainment-style hacker interface.")
p("Asynchronous pages maintain loading, error and empty states. Project creation and editing use a modal form with backend validation errors. Destructive deletion uses confirmation. The scan page validates the URL format before submission and disables launch when no scanner is selected. The scan detail view polls only while work remains and stops after completed, failed or cancelled states. Reports show generation state while the file response is prepared.")
heading("6.2 API Client",2)
p("src/services/api.js defines one request helper and named functions for dashboard, project, scan, finding and report operations. Non-success responses are converted into Error objects using the API detail message when available. Report downloads retain the selected scan identifier, create an object URL from the response blob and revoke it after triggering the download.")
heading("6.3 Backend Application",2)
p("backend/app/main.py creates the FastAPI application, initializes the database during lifespan startup, installs configurable CORS handling and registers the project, scan, finding, report and dashboard routers. Middleware rejects request bodies over one megabyte and adds X-Content-Type-Options, X-Frame-Options, Referrer-Policy and Cache-Control headers. SQLAlchemy errors are logged internally and returned as a generic database-operation failure.")
heading("6.4 Project Management",2)
p("The projects router implements list, create, retrieve, update and delete operations. Project responses include scan and severity counts derived from related records. Eager loading supports these calculations without depending on an open session after serialization. Cascading relationships intentionally remove child scans and findings when a project is deleted.")
heading("6.5 Scan Management",2)
p("ScanCreate accepts an optional project, target, mode and controlled list of tool names. Creation stores pending state and JSON-encoded tools. Start enforces a pending-to-running transition and schedules execute_scan through BackgroundTasks. Progress and current_stage values are committed between stages. Completion records elapsed duration and timestamps; exceptions record a bounded error message; cancellation produces its own terminal state.")
heading("6.6 Scanner Architecture",2)
p("BaseScanner defines the run target interface and ScannerError provides a shared controlled failure. SafeHttpScanner, HttpxScanner, NucleiScanner and ZapScanner remain isolated from route code. The current real orchestration maps the frontend httpx option to the built-in safe HTTP scanner; the separate ProjectDiscovery httpx adapter remains present but is not exercised by the active service mapping.")
table("Table 7: Scanner capabilities",["Component","Implemented behavior","Verification state"],[["Safe HTTP scanner","GET request, redirect and size bounds, headers, server and cookie checks","Verified using a controlled local server"],["Nuclei adapter","Binary invocation, timeout, JSONL parsing and errors","Adapter verified; live executable unavailable"],["ZAP adapter","Version check, scan initiation, polling, alerts and errors","Adapter verified; live service unavailable"],["ProjectDiscovery httpx adapter","JSON reconnaissance subprocess parser","Present; live executable unavailable and not active in orchestration"],["Mock scanner","Deterministic findings and staged progress","Verified end to end"]],[3.1,8.1,4.8])
heading("6.7 HTTP Scanner",2)
p("The built-in scanner first applies network target validation. It creates an httpx client with five-second connection timeout, ten-second overall timeout, three maximum connections, one keep-alive connection, five redirects and a SentinelVAPT user agent. It performs GET only and stops reading when MAX_RESPONSE_BYTES is exceeded. Findings cover missing Content-Security-Policy, HSTS where HTTPS is used, X-Content-Type-Options, clickjacking protection and Referrer-Policy. It also records server header disclosure and cookies missing Secure, HttpOnly or SameSite attributes.")
heading("6.8 Nuclei Adapter",2)
p("Nuclei is invoked using a list of arguments with shell execution disabled. The adapter requests JSONL and disables interactsh. It returns clear errors for a missing binary, timeout and non-zero exit. Malformed output lines are ignored, while valid metadata such as template identifier, matched location, name, severity, classification and matcher information are normalized. Adapter behaviour was verified. A real Nuclei executable was not installed during verification.")
heading("6.9 OWASP ZAP Adapter",2)
p("The ZAP adapter checks the core version endpoint, accesses the authorized URL and initiates spider or active scanning according to mode. It polls the relevant status endpoint until 100 percent or timeout, then loads alerts for the base URL. Passive mode reads available alerts without initiating an active attack. Adapter behaviour was verified with controlled API responses. A live ZAP service was not available during verification.")
heading("6.10 Finding Processing",2); add_figure(figures[3],"Figure 4: Finding Processing Workflow")
p("normalizer.py contains separate conversions for httpx, Nuclei and ZAP. severity_service.py maps scanner labels to Critical, High, Medium, Low or Informational and supplies simple fallback CVSS values. deduplicator.py canonicalizes URLs and titles, including known CSP aliases. The service then hashes the lowercase URL and title with SHA-256. A unique database index on scan_id and fingerprint prevents the same normalized identity from being persisted twice in one scan.")
heading("6.11 Dashboard and Reporting",2)
p("The dashboard router calculates counts directly from Project, Scan and Finding tables and returns recent records. The report service rejects nonexistent scans and scans that are not completed. It computes a severity counter, loads project context and dispatches to the selected renderer.")
add_figure(figures[4],"Figure 5: Report Generation Workflow")
heading("6.12 Error Handling",2)
p("Backend routers return 404 for missing resources, 409 for invalid state transitions, 422 for schema validation and controlled failures for database or scanner problems. The frontend API client extracts detail messages and major pages render explicit error states instead of blank areas. Unknown frontend paths show a 404 page rather than silently returning the dashboard.")

chapter("Chapter 7 Security Design")
heading("7.1 Target Validation",2)
p("Project and scan schemas accept only HTTP and HTTPS URLs with a network location. Empty values, malformed URLs, unsupported schemes, localhost names, restricted literal IP addresses and embedded credentials are rejected. Scanner-time validation resolves hostnames and checks every resolved address before sending a request.")
heading("7.2 SSRF Protection",2); add_figure(figures[5],"Figure 6: Target Security Validation Flow")
p("The target service uses socket.getaddrinfo and Python ipaddress classification. When ALLOW_PRIVATE_TARGETS is false, any non-global result is rejected, covering loopback, private, link-local, multicast, unspecified and reserved ranges. This second-stage DNS check reduces the risk that a public-looking hostname resolves to an internal destination. The setting can be enabled only for an intentionally authorized local laboratory.")
heading("7.3 Additional Controls",2)
p("Credential-bearing URLs are rejected to avoid accidental disclosure and ambiguous authentication behavior. API middleware limits request bodies to one megabyte. The HTTP scanner limits response consumption, redirects, connections and time. External scanner commands are built from server-configured executable paths and fixed argument arrays; API clients cannot submit command fragments or executable paths. SQLAlchemy supplies parameterized database operations, foreign keys are enabled for each SQLite connection, and indexes support status and fingerprint integrity.")
heading("7.4 Error and Secret Handling",2)
p("Configuration values are loaded from environment variables and .env is excluded from version control. AI credentials never enter the frontend. Database exceptions are logged on the server and replaced with a generic API response. Scanner messages are bounded before persistence. These controls reduce leakage, but they do not replace authentication, authorization, audit logging or production secret management.")
heading("7.5 Security Limitations",2)
p("The application currently trusts the local operator because it has no authentication or authorization layer. Background jobs execute in the API process and do not survive restart. SQLite is not appropriate for high write concurrency. External-tool security also depends on installed versions and local configuration that were not available for live qualification. The platform must therefore not be described as fully secure or production-ready.")

chapter("Chapter 8 Testing and Validation")
heading("8.1 Testing Strategy",2)
p("Verification combines production frontend bundling, Python bytecode compilation, FastAPI TestClient workflows, isolated SQLite data, unit-level processor checks, controlled scanner adapter behavior, a local HTTP server, database integrity queries and seed-idempotency checks. The tests intentionally avoid destructive security actions and never require a public target.")
table("Table 8: Build verification",["Verification","Observed result"],[["Frontend npm run build","PASS; Vite transformed 1,804 modules"],["Backend python -m compileall app","PASS"],["SQLite integrity_check","PASS; result ok"],["Application foreign-key PRAGMA","PASS; enabled through engine event"],["Seed idempotency","PASS; populated database skipped"],["Development data preservation","PASS; 2 projects, 3 scans, 5 findings"]],[8.5,7.5])
heading("8.2 Automated Test Results",2)
p("The latest complete run executed 12 tests. All 12 passed, none failed and none were skipped. Pytest reported one non-blocking Starlette TestClient deprecation warning. The warning concerns a dependency interface and did not change functional results.")
table("Table 9: Functional test coverage",["Area","Cases verified","Result"],[["Projects","Create, retrieve, update, delete, missing project and validation","PASS"],["Scans","Create, start, mock completion, cancellation, state conflict and failure persistence","PASS"],["Findings","Creation, retrieval, filters, status, note and invalid status","PASS"],["Processing","Known-alias deduplication and deterministic normalized severity","PASS"],["Reports","Selected completed scan, PDF, HTML, project identity, invalid and incomplete scan","PASS"],["Dashboard","Response structure and aggregated data endpoint","PASS"],["Frontend","Production build, imports and route compilation","PASS"]],[3.0,10.2,2.8])
heading("8.3 Security and Scanner Tests",2)
table("Table 10: Security regression tests",["Control","Test condition","Result"],[["Scheme validation","file, ftp, empty and malformed values","PASS"],["Credential URLs","Embedded username and password","PASS"],["Restricted literals","localhost, loopback, private, link-local and reserved","PASS"],["DNS restriction","Hostname mocked to loopback","PASS"],["HTTP redirects","Controlled redirect loop","PASS; bounded failure"],["Response size","Body exceeded configured limit","PASS; bounded read"],["Headers and cookies","Missing headers, server disclosure and weak cookie","PASS; findings generated"],["Security headers","API response headers inspected","PASS"],["Subprocess safety","Argument-array adapters reviewed and exercised","PASS"]],[3.2,8.6,4.2])
heading("8.4 External Scanner Verification",2)
table("Table 11: Scanner verification status",["Scanner","Verified behavior","Live integration"],[["Safe HTTP scanner","Timeout/redirect bounds, size limit, headers, server and cookie checks","VERIFIED on controlled local server"],["Nuclei","Missing binary, timeout, malformed and valid JSONL normalization","NOT VERIFIED live; executable unavailable"],["OWASP ZAP","Connection failure, polling, alert response and normalization","NOT VERIFIED live; service unavailable"],["ProjectDiscovery httpx","Source reviewed; missing executable handled","NOT VERIFIED live; executable unavailable"],["Mock scanner","Progress stages, persisted findings and completion","VERIFIED end to end"]],[3.2,8.2,4.6])
heading("8.5 Defects Found and Corrected",2)
table("Table 12: Defects found and corrected",["Defect","Correction"],[["Unknown frontend routes rendered the dashboard","Added an explicit 404 route and recovery link"],["Project API failures displayed stale mock detail","Added loading and error states"],["Unsafe literal targets reached scan creation","Added schema-level address and localhost rejection"],["Credential-bearing URLs were accepted","Rejected parsed username or password"],["Reports were available before completion","Added completed-state enforcement with HTTP 409"],["Reports omitted project identity","Loaded and rendered project context"],["Report tests did not verify selected context","Added project identity and invalid/incomplete cases"],["Scanner and target regression coverage was incomplete","Added controlled HTTP, Nuclei, ZAP and DNS tests"]],[6.5,9.5])

chapter("Chapter 9 Results and Discussion")
heading("9.1 Current Functional State",2)
p("The current repository is a coherent working prototype. The frontend can manage projects, launch and observe scans, filter findings, change dispositions and request completed-scan reports. The backend persists these operations and supports a real bounded HTTP assessment. Mock mode allows repeatable demonstrations without external infrastructure.")
heading("9.2 Security and Scanner Results",2)
p("The strongest current result is the combination of usable orchestration and explicit defensive boundaries. Public-target validation occurs before the built-in scanner request, restricted destinations are denied by default and external commands do not pass through a shell. The built-in scanner produces configuration findings in a controlled local test. Nuclei and ZAP adapter behavior is tested, but live tool effectiveness cannot be inferred from mocked API and subprocess results.")
heading("9.3 Database State",2)
p("The development database passed SQLite integrity checking and contained two projects, three scans and five findings at verification time. Application connections enable foreign keys. Startup performs additive migration for finding metadata and does not seed automatically. Running seed.py against populated data exits without duplication.")
heading("9.4 Completion Assessment",2)
table("Table 13: Current completion assessment",["Area","Approximate completion"],[["Frontend and UI","88%"],["Backend","68%"],["Scanner implementation","58%"],["Reporting","78%"],["Testing","72%"],["Security hardening","70%"],["Overall","Approximately 72%"]],[9.5,6.5])
p("These percentages are engineering development estimates rather than formal quality scores. They reflect implemented workflows, verified behavior and remaining operational gaps. Passing tests increases confidence in the implemented subset but does not increase scope or prove comprehensive vulnerability coverage.")

chapter("Chapter 10 Limitations")
p("SentinelVAPT remains incomplete in several material areas. It does not authenticate users, enforce roles or isolate multiple tenants. Anyone with network access to the API could invoke its current routes unless deployment controls are added. This is the most important limitation before shared use.")
p("FastAPI BackgroundTasks are suitable for the prototype but are not persistent jobs. A process restart can interrupt a running scan, and work is not coordinated across multiple API instances. SQLite is convenient for local use but constrains concurrent writes, migration management and horizontal scaling.")
p("Real Nuclei, ZAP and ProjectDiscovery httpx executions were not available during verification. The adapters handle missing tools and controlled responses, but installation-specific behavior, template versions, ZAP add-ons, API authorization and long-running production targets remain unqualified. The active orchestration uses the built-in HTTP scanner under the httpx selection; the separate ProjectDiscovery httpx adapter is present but not wired as a distinct selectable stage.")
p("Vulnerability coverage is deliberately narrow. The built-in scanner checks observable HTTP configuration and cookie attributes, not authentication logic, authorization, complex business rules, client-side execution, API schemas or authenticated application states. Scanner findings require human validation. There is no authenticated crawling, credential vault, browser automation or evidence capture beyond scanner-provided text.")
p("The frontend has no automated browser or component test suite. Settings are largely presentational. AI explanation depends on an external compatible service and is not tested as an essential workflow. Reports are suitable for a project prototype but do not yet offer organizational branding, reviewer sign-off, risk acceptance workflow or digital signatures.")

chapter("Chapter 11 Future Enhancements")
table("Table 14: Future enhancement roadmap",["Phase","Focus","Proposed work"],[["Phase 1","Production backend reliability","Formal migrations, structured logs, health detail, scan recovery and deployment configuration"],["Phase 2","Authentication and authorization","Secure accounts, sessions, roles and route-level authorization"],["Phase 3","Persistent scan workers","Durable queue, worker isolation, retries, cancellation and restart recovery"],["Phase 4","Live scanner qualification","Install, configure and test Nuclei, ZAP and ProjectDiscovery httpx in an authorized lab"],["Phase 5","Expanded detection","Authenticated crawling, additional safe checks, API-aware assessment and traceable standards mapping"],["Phase 6","Advanced reporting","Custom templates, reviewer workflow, signed exports and improved evidence presentation"],["Phase 7","Multi-user deployment","Tenant isolation, production database, audit logging, quotas and operational monitoring"]],[2.2,4.0,9.8])
p("This roadmap intentionally separates future work from the current implementation. The next engineering priority should be reliability and access control rather than adding more scanner types. Live external-tool qualification should use intentionally vulnerable laboratory applications and documented authorization boundaries.")

chapter("Conclusion")
p("SentinelVAPT was developed to address a practical coordination problem in small web application vulnerability assessments. Individual tools can discover useful information, but their output is difficult to organize when project context, execution state, evidence, severity, remediation and reporting are handled separately. The implemented prototype demonstrates that a compact local platform can coordinate these concerns without becoming an autonomous exploitation system.")
p("The solution uses a React and Vite frontend, a FastAPI REST backend, SQLAlchemy models and an SQLite development database. Projects contain scans, and scans contain findings. The frontend exposes project management, scan configuration, progress monitoring, finding review, filtering, disposition changes, dashboard metrics and report downloads. The backend validates these operations, persists state and separates routers, schemas, services, scanner adapters, processors and report generators. This architecture remains simple enough for an engineering project while creating clear boundaries for future development.")
p("Scanning is intentionally defensive. The built-in HTTP scanner performs bounded GET requests and evaluates a defined set of headers, HTTPS-related behavior, server disclosure and cookie attributes. It limits connections, redirects, response data and time. Nuclei, ProjectDiscovery httpx and OWASP ZAP are represented through isolated adapters rather than arbitrary command execution. The Nuclei adapter parses JSONL and persists controlled errors. The ZAP adapter checks service availability, starts a mode-appropriate scan, polls status and retrieves alerts. Mock mode supports demonstrations when these dependencies are unavailable.")
p("Finding processing is a significant part of the implemented work. Raw records are normalized into common fields for title, severity, category, URL, tool, CWE, CVSS, evidence, impact and remediation. Deterministic severity mapping avoids client-controlled risk labels. Rule-based title and URL comparison reduces known duplicates, and SHA-256 fingerprints with per-scan database uniqueness provide a second persistence boundary. Finding status is restricted to open, confirmed, false positive or resolved, with an optional resolution note.")
p("Security controls were implemented around the scanning workflow because an assessment platform can otherwise become an SSRF or command-execution risk. The API rejects unsupported schemes, credential-bearing URLs, localhost names and restricted literal addresses. The scanner resolves hostnames and blocks non-global results unless private targets are explicitly enabled for an authorized laboratory. Request and response sizes, redirect counts, connections and scanner durations are bounded. Subprocess adapters use fixed argument arrays and shell execution remains disabled. These measures improve the prototype, but they do not justify describing it as secure or production-ready while authentication and durable job isolation are absent.")
p("Verification provides evidence for the current claims. The latest Vite production build succeeded after transforming 1,804 modules. Every backend module compiled. Twelve automated tests executed; all twelve passed, with no failures or skips. Tests covered project CRUD, scan completion, cancellation and failure, findings, status validation, deduplication, reports, dashboard output, restricted targets, security headers and controlled scanner behavior. SQLite integrity and seed idempotency also passed. The safe HTTP scanner was exercised against a controlled local server. Nuclei and ZAP adapters were tested with controlled responses, but live integrations were not verified because the executable and service were unavailable.")
p("The present completion estimate remains approximately 72 percent. The frontend is comparatively mature, while backend durability, live scanner qualification and deployment controls remain incomplete. Passing tests improves confidence only within the implemented scope. The project does not provide comprehensive vulnerability detection, authenticated assessment, multi-user access, persistent workers or enterprise scalability.")
p("As an engineering outcome, SentinelVAPT demonstrates a complete path from an authorized target and scan record to normalized findings and downloadable reports. It also documents its limitations instead of hiding them. Future work should first strengthen authentication, migration management and persistent scan execution, then qualify external tools in a controlled laboratory and broaden coverage gradually. This sequence would preserve the project's understandable architecture while moving it from a tested academic prototype toward a dependable security assessment platform.")

chapter("References")
refs=[
"[1] K. Scarfone, M. Souppaya, A. Cody and A. Orebaugh, Technical Guide to Information Security Testing and Assessment, NIST Special Publication 800-115, September 2008. doi: 10.6028/NIST.SP.800-115. https://csrc.nist.gov/pubs/sp/800/115/final",
"[2] OWASP Foundation, OWASP Web Security Testing Guide, stable version 4.2. https://wstg.owasp.org/",
"[3] OWASP Foundation, OWASP Top 10:2025. https://owasp.org/projects/top-ten/",
"[4] OWASP Foundation, Application Security Verification Standard 5.0.0. https://owasp.org/projects/asvs/",
"[5] C. Pascoe, S. Quinn and K. Scarfone, The NIST Cybersecurity Framework 2.0, NIST CSWP 29, February 2024. doi: 10.6028/NIST.CSWP.29.",
"[6] ProjectDiscovery, Nuclei Documentation: Template Structure and Running Nuclei. https://docs.projectdiscovery.io/templates/structure and https://docs.projectdiscovery.io/opensource/nuclei/running",
"[7] OWASP Foundation, ZAP Documentation and Getting Started Guide. https://www.zaproxy.org/docs/ and https://www.zaproxy.org/getting-started/",
"[8] J. Bau, E. Bursztein, D. Gupta and J. Mitchell, State of the Art: Automated Black-Box Web Application Vulnerability Testing, 2010 IEEE Symposium on Security and Privacy, pp. 332-345. doi: 10.1109/SP.2010.27.",
"[9] FastAPI Project, FastAPI Documentation. https://fastapi.tiangolo.com/",
"[10] SQLAlchemy Authors, SQLAlchemy Documentation. https://docs.sqlalchemy.org/",
]
for ref in refs: p(ref)

# Update fields on open and set core metadata.
settings=doc.settings.element; upd=OxmlElement("w:updateFields"); upd.set(qn("w:val"),"true"); settings.append(upd)
doc.core_properties.title="SentinelVAPT Project Report"
doc.core_properties.subject="Web Based Vulnerability Assessment and Reporting Platform"
doc.core_properties.author="Rohan"
doc.core_properties.keywords="SentinelVAPT, VAPT, FastAPI, React, security assessment"
doc.save(OUT)
print(OUT)
