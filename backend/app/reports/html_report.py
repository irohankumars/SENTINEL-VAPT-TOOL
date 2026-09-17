from jinja2 import Template

TEMPLATE = Template("""<!doctype html><html><head><meta charset="utf-8"><title>SentinelVAPT Report</title><style>
body{font:14px Arial;color:#222;max-width:900px;margin:40px auto}header{border-bottom:3px solid #991b1b;padding-bottom:18px}h1{margin:0}code{font-family:monospace}.summary{display:flex;gap:12px;margin:24px 0}.summary span{border:1px solid #ddd;padding:12px}.finding{page-break-inside:avoid;border-top:1px solid #ddd;padding:18px 0}.sev{color:#991b1b;text-transform:uppercase;font-weight:bold;font-size:11px}dt{font-weight:bold;margin-top:8px}dd{margin:3px 0 0}</style></head><body>
<header><h1>SentinelVAPT</h1><h2>Security Assessment Report</h2><p><b>Project:</b> {{ project.name if project else 'Unassigned assessment' }}<br><b>Target:</b> <code>{{ scan.target_url }}</code><br><b>Date:</b> {{ scan.started_at or 'Not started' }}<br><b>Duration:</b> {{ scan.duration or 0 }} seconds<br><b>Tools:</b> {{ tools|join(', ') }}</p></header>
<section class="summary">{% for name,count in summary.items() %}<span><b>{{ count }}</b><br>{{ name }}</span>{% endfor %}</section>
<h2>Detailed Findings</h2>{% for f in findings %}<article class="finding"><div class="sev">{{ f.severity }}</div><h3>{{ f.title }}</h3><dl><dt>URL</dt><dd><code>{{ f.url }}</code></dd><dt>Tool / CWE / CVSS</dt><dd>{{ f.tool }} · {{ f.cwe or 'N/A' }} · {{ f.cvss if f.cvss is not none else 'N/A' }}</dd><dt>Description</dt><dd>{{ f.description }}</dd><dt>Evidence</dt><dd><code>{{ f.evidence or 'Not supplied' }}</code></dd><dt>Impact</dt><dd>{{ f.impact or 'Not supplied' }}</dd><dt>Remediation</dt><dd>{{ f.remediation or 'Not supplied' }}</dd></dl></article>{% else %}<p>No findings were recorded.</p>{% endfor %}</body></html>""")

def render_html(scan, findings, summary, tools, project):
    return TEMPLATE.render(scan=scan, findings=findings, summary=summary, tools=tools, project=project)
