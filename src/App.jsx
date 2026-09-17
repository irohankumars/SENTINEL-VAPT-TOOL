import React, { useEffect, useState } from "react";
import {
  Routes,
  Route,
  NavLink,
  Link,
  useNavigate,
  useParams,
  useSearchParams,
} from "react-router-dom";
import {
  LayoutDashboard,
  FolderKanban,
  Radar,
  Bug,
  FileText,
  Settings as SettingsIcon,
  Menu,
  X,
  Plus,
  ArrowRight,
  Download,
  Check,
  Shield,
  Search,
  Play,
  ExternalLink,
  ChevronRight,
  Terminal,
  Activity,
} from "lucide-react";
import {
  projects,
  findings as seedFindings,
  scans,
  logs,
} from "./data/mockData";
import * as api from "./services/api";

const sevOrder = { Critical: 5, High: 4, Medium: 3, Low: 2, Info: 1 };
const uiFinding = (f) => ({
  ...f,
  id: String(f.id),
  name: f.title || f.name,
  path: f.url ? new URL(f.url).pathname : f.path,
  target: f.url ? new URL(f.url).host : f.target,
  severity: f.severity === "Informational" ? "Info" : f.severity,
  status: f.status ? f.status[0].toUpperCase() + f.status.slice(1) : "Open",
  cvss: String(f.cvss ?? "—"),
});
const uiProject = (p) => ({
  ...p,
  id: String(p.id),
  url: p.target_url || p.url,
  last: p.updated_at
    ? new Date(p.updated_at).toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric",
      })
    : p.last,
  findings: p.finding_count ?? p.findings ?? 0,
  critical: p.critical_count ?? p.critical ?? 0,
  high: p.high_count ?? p.high ?? 0,
  medium: p.medium_count ?? p.medium ?? 0,
  score: p.score ?? Math.max(45, 100 - (p.finding_count || 0) * 3),
});
const Severity = ({ level }) => (
  <span className={"severity " + level.toLowerCase()}>
    <i />
    {level}
  </span>
);
const Status = ({ children }) => (
  <span className={"status " + String(children).toLowerCase()}>{children}</span>
);
function Toast({ message }) {
  return message ? (
    <div className="toast">
      <Check size={16} />
      {message}
    </div>
  ) : null;
}
const AsyncState=({loading,error,empty,children})=>loading?<div className="panel state-card" role="status">Loading security data…</div>:error?<div className="panel state-card error-state"><b>Unable to load data</b><span>{error}</span></div>:empty?<div className="panel state-card"><b>No data yet</b><span>Create a project or run a scan to get started.</span></div>:children;
function ProjectForm({initial,onClose,onSaved}){const [name,setName]=useState(initial?.name||'');const [target,setTarget]=useState(initial?.target_url||initial?.url||'https://');const [description,setDescription]=useState(initial?.description||'');const [busy,setBusy]=useState(false);const [error,setError]=useState('');const save=async e=>{e.preventDefault();setBusy(true);setError('');try{const payload={name:name.trim(),target_url:target.trim(),description:description.trim()||null};const item=initial?await api.updateProject(initial.id,payload):await api.createProject(payload);onSaved(item)}catch(err){setError(err.message)}finally{setBusy(false)}};return <div className="modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)onClose()}}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="project-form-title"><div className="panel-title"><span id="project-form-title">{initial?'Edit project':'New project'}</span><button className="icon-btn" aria-label="Close" onClick={onClose}><X size={16}/></button></div><form onSubmit={save}><label>Project name<input autoFocus required minLength="2" value={name} onChange={e=>setName(e.target.value)}/></label><label>Target URL<input required type="url" pattern="https?://.*" value={target} onChange={e=>setTarget(e.target.value)}/></label><label>Description<textarea rows="3" value={description} onChange={e=>setDescription(e.target.value)}/></label>{error&&<div className="form-error" role="alert">{error}</div>}<div className="modal-actions"><button type="button" className="btn" onClick={onClose}>Cancel</button><button className="btn primary" disabled={busy}>{busy?'Saving…':'Save project'}</button></div></form></section></div>}

function Layout() {
  const [open, setOpen] = useState(false);
  const links = [
    [LayoutDashboard, "Dashboard", "/dashboard"],
    [FolderKanban, "Projects", "/projects"],
    [Radar, "New scan", "/scan/new"],
    [Bug, "Findings", "/findings"],
    [FileText, "Reports", "/reports"],
  ];
  return (
    <div className="app">
      <aside className={open ? "sidebar open" : "sidebar"}>
        <button className="close mobile" onClick={() => setOpen(false)}>
          <X />
        </button>
        <Link to="/dashboard" className="brand">
          <span className="brandmark">
            <Shield size={21} />
          </span>
          <span>
            <b>SENTINEL</b>
            <em>VAPT</em>
          </span>
        </Link>
        <p className="brandline">Security assessment platform</p>
        <div className="nav-label">Workspace</div>
        <nav>
          {links.map(([Icon, label, to]) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              <Icon size={17} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
        <div className="side-bottom">
          <NavLink to="/settings">
            <SettingsIcon size={17} />
            Settings
          </NavLink>
          <div className="local">
            <i /> v0.1.0 · LOCAL
          </div>
        </div>
      </aside>
      <div className="shell">
        <header>
          <button className="mobile menu" onClick={() => setOpen(true)}>
            <Menu />
          </button>
          <div className="crumb">
            SENTINEL <span>/</span> WORKSPACE
          </div>
          <div className="system">
            <span>
              <i /> SYSTEM ONLINE
            </span>
            <span>SCANNER READY</span>
            <span>LOCAL MODE</span>
            <div className="avatar">KS</div>
          </div>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/projects/:id" element={<Project />} />
            <Route path="/scan/new" element={<NewScan />} />
            <Route path="/scans/:id" element={<Scan />} />
            <Route path="/findings" element={<Findings />} />
            <Route path="/findings/:id" element={<Finding />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

const PageHead = ({ eyebrow = "OPERATIONS", title, desc, action }) => (
  <div className="pagehead">
    <div>
      <div className="eyebrow">{eyebrow}</div>
      <h1>{title}</h1>
      <p>{desc}</p>
    </div>
    {action}
  </div>
);
function Dashboard() {
  const [data,setData]=useState(null);const [loading,setLoading]=useState(true);const [error,setError]=useState('');
  useEffect(()=>{api.getDashboard().then(setData).catch(e=>setError(e.message)).finally(()=>setLoading(false))},[]);
  const counts=data?.severity||{};const recent=data?.recent_scans?.[0];const recentFindings=(data?.recent_findings||[]).map(uiFinding);const maximum=Math.max(1,...Object.values(counts));
  return (
    <>
      <PageHead
        title="Security Overview"
        desc="Monitor your web application security assessments."
        action={
          <Link className="btn primary" to="/scan/new">
            <Play size={15} />
            Start scan
          </Link>
        }
      />
      <AsyncState loading={loading} error={error} empty={!data}>{data&&<><div className="metrics">
        {[
          ["Total projects", data.metrics.projects, `${data.metrics.scans} scans`],
          ["Active scans", data.metrics.active_scans, `${data.metrics.completed_scans} completed`],
          ["Critical", counts.Critical||0, "Needs attention"],
          ["High", counts.High||0, `${data.metrics.open_findings} open findings`],
        ].map((x, i) => (
          <div className={"metric m" + i} key={x[0]}>
            <label>{x[0]}</label>
            <strong>{String(x[1]).padStart(2, "0")}</strong>
            <small>{x[2]}</small>
          </div>
        ))}
      </div>
      <div className="dashboard-grid">
        <section className="panel recent-scan">
          <div className="panel-title">
            <span>Recent scan</span>
            {recent&&<Link to={`/scans/${recent.id}`}>
              View results <ArrowRight size={14} />
            </Link>}
          </div>
          <div className="scan-id">
            <div>
              <label>Target</label>
              <b>{recent?new URL(recent.target_url).host:'No scans yet'}</b>
            </div>
            <div>
              <label>Scan ID</label>
              <code>{recent?`SCN-${String(recent.id).padStart(6,'0')}`:'—'}</code>
            </div>
            <div>
              <label>Status</label>
              <Status>{recent?.status||'Pending'}</Status>
            </div>
            <div>
              <label>Duration</label>
              <code>{recent?.duration?`${Math.round(recent.duration)}s`:'—'}</code>
            </div>
          </div>
          <div className="tools">
            <label>Toolchain</label>
            {(recent?.tools||[]).map(tool=><React.Fragment key={tool}><span>{tool.toUpperCase()}</span><i/></React.Fragment>)}
          </div>
          <div className="distribution">
            <label>Severity distribution</label>
            {[["Critical",counts.Critical||0],["High",counts.High||0],["Medium",counts.Medium||0],["Low",counts.Low||0],["Info",counts.Informational||0]].map(([s, n]) => (
              <div className="barrow" key={s}>
                <span>{s}</span>
                <div>
                  <i
                    className={s.toLowerCase()}
                    style={{ width: (n / maximum) * 100 + "%" }}
                  />
                </div>
                <code>{String(n).padStart(2, "0")}</code>
              </div>
            ))}
          </div>
        </section>
        <section className="panel">
          <div className="panel-title">
            <span>Recent findings</span>
            <Link to="/findings">
              View all <ArrowRight size={14} />
            </Link>
          </div>
          <div className="finding-list">
            {recentFindings.slice(0, 4).map((f) => (
              <Link to={"/findings/" + f.id} key={f.id}>
                <Severity level={f.severity} />
                <div>
                  <b>{f.name}</b>
                  <code>{f.path}</code>
                </div>
                <span>
                  {f.tool}
                  <small>{f.ago}</small>
                </span>
                <ChevronRight size={16} />
              </Link>
            ))}
          </div>
        </section>
      </div></>}</AsyncState>
    </>
  );
}

function Projects() {
  const [items, setItems] = useState(projects);
  const [loading,setLoading]=useState(true);const [error,setError]=useState('');const [showForm,setShowForm]=useState(false);const [query,setQuery]=useState('');
  const load=()=>{setLoading(true);setError('');api.getProjects().then(x=>setItems(x.map(uiProject))).catch(e=>setError(e.message)).finally(()=>setLoading(false))};
  useEffect(() => {
    load();
  }, []);
  const visible=items.filter(p=>(p.name+p.url).toLowerCase().includes(query.toLowerCase()));
  return (
    <>
      <PageHead
        eyebrow="ASSETS"
        title="My Projects"
        desc="Organize targets and review their assessment history."
        action={
          <button className="btn primary" onClick={()=>setShowForm(true)}>
            <Plus size={16} />
            New project
          </button>
        }
      />
      <div className="filters"><div className="search"><Search size={16}/><input aria-label="Search projects" placeholder="Search projects or targets…" value={query} onChange={e=>setQuery(e.target.value)}/></div></div>
      <AsyncState loading={loading} error={error} empty={!visible.length}>
      <div className="project-grid">
        {visible.map((p) => (
          <article className="project-card" key={p.id}>
            <div className="project-top">
              <span className="target-icon">
                <FolderKanban />
              </span>
              <span className="score">
                Score <b>{p.score}</b>/100
              </span>
            </div>
            <h2>{p.name}</h2>
            <code>{p.url}</code>
            <div className="project-meta">
              <span>
                <label>Last scan</label>
                {p.last}
              </span>
              <span>
                <label>Findings</label>
                {p.findings}
              </span>
            </div>
            <div className="severity-counts">
              <span>
                <i className="critical" />
                {p.critical} Critical
              </span>
              <span>
                <i className="high" />
                {p.high} High
              </span>
              <span>
                <i className="medium" />
                {p.medium} Medium
              </span>
            </div>
            <Link className="card-link" to={"/projects/" + p.id}>
              Open project <ArrowRight size={15} />
            </Link>
          </article>
        ))}
      </div>
      </AsyncState>
      {showForm&&<ProjectForm onClose={()=>setShowForm(false)} onSaved={()=>{setShowForm(false);load()}}/>}
    </>
  );
}
function Project() {
  const { id } = useParams();
  const nav=useNavigate();const [editing,setEditing]=useState(false);const [toast,setToast]=useState('');
  const [p, setP] = useState(projects.find((x) => x.id === id) || projects[0]);
  const [projectScans, setProjectScans] = useState(scans);
  const [projectFindings, setProjectFindings] = useState(
    seedFindings.slice(0, 4),
  );
  const [loading,setLoading]=useState(/^\d+$/.test(id));const [error,setError]=useState('');
  useEffect(() => {
    if (!/^\d+$/.test(id)) return;
    Promise.all([
      api.getProject(id),
      api.getScans(id),
      api.getFindings({ project_id: id }),
    ])
      .then(([project, s, f]) => {
        setP(uiProject(project));
        setProjectScans(s);
        setProjectFindings(f.slice(0, 4).map(uiFinding));
      })
      .catch(e => setError(e.message)).finally(()=>setLoading(false));
  }, [id]);
  if(loading)return <AsyncState loading/>;
  if(error)return <AsyncState error={error}/>;
  return (
    <>
      <PageHead
        eyebrow="PROJECT / WEB APPLICATION"
        title={p.name}
        desc={p.url}
        action={<div className="actions"><button className="btn" onClick={()=>setEditing(true)}>Edit</button><button className="btn danger" onClick={async()=>{if(!window.confirm(`Delete ${p.name} and all of its scans and findings?`))return;try{await api.deleteProject(id);nav('/projects')}catch(e){setToast(e.message)}}}>Delete</button>
          <Link className="btn primary" to={`/scan/new?project_id=${id}&target=${encodeURIComponent(p.url)}`}>
            <Play size={15} />
            Scan target
          </Link>
        </div>}
      />
      <div className="metrics three">
        <div className="metric">
          <label>Security score</label>
          <strong>{p.score}</strong>
          <small>Moderate exposure</small>
        </div>
        <div className="metric">
          <label>Total scans</label>
          <strong>{String(projectScans.length).padStart(2, "0")}</strong>
          <small>Assessment history</small>
        </div>
        <div className="metric">
          <label>Open findings</label>
          <strong>{String(p.findings).padStart(2, "0")}</strong>
          <small>{p.critical} critical priority</small>
        </div>
      </div>
      <section className="panel table-panel">
        <div className="panel-title">
          <span>Scan history</span>
        </div>
        <ScanTable items={projectScans} />
      </section>
      <Toast message={toast}/>{editing&&<ProjectForm initial={p} onClose={()=>setEditing(false)} onSaved={item=>{setP(uiProject(item));setEditing(false)}}/>}
      <section className="panel table-panel spaced">
        <div className="panel-title">
          <span>Latest findings</span>
          <Link to="/findings">
            View all <ArrowRight size={14} />
          </Link>
        </div>
        <FindingsTable items={projectFindings} />
      </section>
    </>
  );
}

function NewScan() {
  const nav = useNavigate();
  const [params]=useSearchParams();
  const [url, setUrl] = useState(params.get('target')||"https://demo.sentinel.local");
  const [mode, setMode] = useState("Standard");
  const [launchError, setLaunchError] = useState("");
  const targetError=(()=>{try{const parsed=new URL(url);return ['http:','https:'].includes(parsed.protocol)?'':'Only HTTP and HTTPS targets are supported.'}catch{return 'Enter a complete URL such as https://example.com.'}})();
  const [opts, setOpts] = useState({
    httpx: true,
    nuclei: true,
    zap: true,
    ai: true,
  });
  const launchScan = async () => {
    setLaunchError("");
    try {
      const scan = await api.createScan({project_id:params.get('project_id')?Number(params.get('project_id')):null,target_url:url,scan_mode:mode.toLowerCase(),tools:Object.keys(opts).filter((key)=>key!=="ai"&&opts[key])});
      await api.startScan(scan.id);
      nav(`/scans/${scan.id}`);
    } catch (error) { setLaunchError(error.message); }
  };
  return (
    <>
      <PageHead
        eyebrow="SCANNER / CONFIGURE"
        title="New Security Scan"
        desc="Configure an assessment. No traffic is sent in local demo mode."
      />
      <div className="scan-config">
        <section className="panel config-main">
          <div className="form-section">
            <div className="section-index">01</div>
            <div>
              <h3>Target</h3>
              <p>
                Enter the full URL of the application you are authorized to
                test.
              </p>
              <label className="field-label">Target URL</label>
              <div className="target-input">
                <span>URL</span>
                <input aria-label="Target URL" aria-invalid={Boolean(targetError)} value={url} onChange={(e) => setUrl(e.target.value)} />
                <Check size={17} />
              </div>
              <div className={targetError?'form-error':'valid'}>{targetError||<><i/> Target format is valid <span>· server verification follows</span></>}</div>
            </div>
          </div>
          <div className="form-section">
            <div className="section-index">02</div>
            <div>
              <h3>Scan toolchain</h3>
              <p>Select the checks to include in this assessment.</p>
              <div className="option-grid">
                {[
                  [
                    "httpx",
                    "HTTP reconnaissance",
                    "httpx",
                    "Map endpoints and detect technologies",
                  ],
                  [
                    "nuclei",
                    "Vulnerability scanning",
                    "Nuclei",
                    "Run community vulnerability templates",
                  ],
                  [
                    "zap",
                    "Web application scanning",
                    "OWASP ZAP",
                    "Inspect requests and response behavior",
                  ],
                  [
                    "ai",
                    "AI analysis",
                    "Explain findings",
                    "Generate beginner-friendly guidance",
                  ],
                ].map(([key, kicker, name, desc]) => (
                  <button
                    key={key}
                    className={
                      opts[key] ? "tool-option selected" : "tool-option"
                    }
                    onClick={() => setOpts({ ...opts, [key]: !opts[key] })}
                  >
                    <span className="checkbox">
                      {opts[key] && <Check size={14} />}
                    </span>
                    <div>
                      <small>{kicker}</small>
                      <b>{name}</b>
                      <p>{desc}</p>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="form-section">
            <div className="section-index">03</div>
            <div>
              <h3>Scan mode</h3>
              <p>Controls depth and estimated duration.</p>
              <div className="modes">
                {[
                  ["Passive", "Non-invasive checks", "~1 min"],
                  ["Standard", "Balanced coverage", "~3 min"],
                  ["Active", "Full assessment", "~8 min"],
                ].map(([m, d, t]) => (
                  <button
                    onClick={() => setMode(m)}
                    className={mode === m ? "selected" : ""}
                    key={m}
                  >
                    <span className="radio" />
                    <b>{m}</b>
                    <small>{d}</small>
                    <code>{t}</code>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>
        <aside className="panel launch">
          <div className="panel-title">
            <span>Scan summary</span>
          </div>
          <dl>
            <dt>Target</dt>
            <dd>{url.replace("https://", "")}</dd>
            <dt>Mode</dt>
            <dd>{mode}</dd>
            <dt>Tools enabled</dt>
            <dd>{Object.values(opts).filter(Boolean).length} / 4</dd>
            <dt>Estimated time</dt>
            <dd>02–04 min</dd>
          </dl>
          <div className="scope-note">
            <Shield size={17} />
            <p>
              <b>Authorization required</b>
              <br />
              Only scan systems you own or have explicit permission to assess.
            </p>
          </div>
          <button
            className="btn primary launch-btn"
            onClick={launchScan}
            disabled={Boolean(targetError)||!Object.entries(opts).some(([key,value])=>key!=='ai'&&value)}
          >
            <Play size={16} />
            Start security scan
          </button>
          {launchError && <div className="scan-error">{launchError}</div>}
        </aside>
      </div>
    </>
  );
}

function Scan() {
  const { id } = useParams();
  const backendScan = /^\d+$/.test(id);
  const live = backendScan || id.endsWith("002");
  const [progress, setProgress] = useState(live ? 12 : 100);
  const [scanInfo, setScanInfo] = useState(null);
  const [detected, setDetected] = useState(seedFindings);
  const [scanError,setScanError]=useState('');
  useEffect(() => {
    if (backendScan) {
      let active = true;
      let timer;
      const poll = async () => {
        try {
          const scan = await api.getScan(id);
          if (!active) return;
          setScanInfo(scan); setProgress(scan.progress);
          const rows = await api.getFindings({scan_id:id});
          if (active) setDetected(rows.map(uiFinding));
          if (["completed","failed","cancelled"].includes(scan.status)) return;
        } catch (error) { if(active)setScanError(error.message); }
        if (active) timer=setTimeout(poll,1000);
      };
      poll();
      return ()=>{active=false;clearTimeout(timer)};
    }
    if (!live || progress >= 100) return;
    const t = setInterval(() => setProgress((p) => Math.min(100, p + 2)), 500);
    return () => clearInterval(t);
  }, [id, backendScan, live, progress]);
  const stages = [
    "Target validation",
    "HTTP reconnaissance",
    "Technology detection",
    "Nuclei templates",
    "OWASP ZAP scan",
    "Result normalization",
    "AI analysis",
    "Report generation",
  ];
  const active = Math.min(7, Math.floor(progress / 13));
  return (
    <>
      <PageHead
        eyebrow={progress === 100 ? "SCAN / COMPLETED" : "SCAN / RUNNING"}
        title={progress === 100 ? "Assessment complete" : "Scan in progress"}
        desc={`${id} · ${scanInfo?.target_url || "demo.sentinel.local"}`}
        action={<div className="actions"><Status>{scanInfo?.status || (progress === 100 ? "Completed" : "Running")}</Status>{backendScan&&scanInfo?.status==='running'&&<button className="btn danger" onClick={()=>api.cancelScan(id).then(setScanInfo).catch(e=>setScanError(e.message))}>Cancel scan</button>}</div>}
      />
      {(scanError||scanInfo?.error_message)&&<div className="panel state-card error-state" role="alert"><b>Scan error</b><span>{scanError||scanInfo.error_message}</span></div>}
      <section className="panel progress-panel">
        <div className="progress-head">
          <div>
            <label>Overall progress</label>
            <strong>{progress}%</strong>
          </div>
          <code>
            {progress === 100 ? "00:02:41" : "00:01:4" + (progress % 10)}{" "}
            ELAPSED
          </code>
        </div>
        <div className="progress-track">
          <i style={{ width: progress + "%" }} />
        </div>
        <div className="stage-rail">
          {stages.map((s, i) => (
            <div
              key={s}
              className={
                i < active || progress === 100
                  ? "done"
                  : i === active
                    ? "current"
                    : ""
              }
            >
              <span>
                {i < active || progress === 100 ? <Check size={13} /> : i + 1}
              </span>
              <p>{s}</p>
            </div>
          ))}
        </div>
      </section>
      <div className="scan-layout">
        <section className="panel terminal-panel">
          <div className="terminal-head">
            <span>
              <Terminal size={15} /> SCAN OUTPUT
            </span>
            <i />
            <span>LIVE</span>
          </div>
          <pre>
            <b>$ sentinel scan --target {scanInfo?.target_url || "demo.sentinel.local"} --mode {scanInfo?.scan_mode || "standard"}</b>
            {logs
              .slice(0, Math.max(2, Math.floor(progress / 12)))
              .map((l, i) => (
                <div key={l}>
                  <span>[18:21:{String(4 + i * 3).padStart(2, "0")}]</span> {l}
                </div>
              ))}
            {progress < 100 && <em>_</em>}
          </pre>
        </section>
        <section className="panel detected">
          <div className="panel-title">
            <span>Detected findings</span>
            <b>{Math.floor(progress / 25)}</b>
          </div>
          {detected.slice(0, backendScan ? detected.length : Math.floor(progress / 25)).map((f) => (
            <Link to={"/findings/" + f.id} key={f.id}>
              <Severity level={f.severity} />
              <b>{f.name}</b>
              <code>{f.path}</code>
            </Link>
          ))}
          {progress < 25 && (
            <div className="empty">Waiting for scanner output…</div>
          )}
        </section>
      </div>
    </>
  );
}

function Findings() {
  const [q, setQ] = useState("");
  const [severity, setSeverity] = useState("All");
  const [tool, setTool] = useState("All");
  const [status, setStatus] = useState("All");
  const [sourceFindings, setSourceFindings] = useState([]);
  const [loading,setLoading]=useState(true);const [error,setError]=useState('');
  useEffect(() => {
    setLoading(true);setError('');
    const timer=setTimeout(()=>api.getFindings({severity:severity==="Info"?"Informational":severity,tool,status:status==="All"?"All":status.toLowerCase(),search:q}).then(rows=>setSourceFindings(rows.map(uiFinding))).catch(e=>setError(e.message)).finally(()=>setLoading(false)),200);
    return ()=>clearTimeout(timer);
  },[q,severity,tool,status]);
  const filtered = sourceFindings
    .filter(
      (f) =>
        (severity === "All" || f.severity === severity) &&
        (tool === "All" || f.tool === tool) &&
        (status === "All" || f.status === status) &&
        (f.name + f.path + f.target).toLowerCase().includes(q.toLowerCase()),
    )
    .sort((a, b) => sevOrder[b.severity] - sevOrder[a.severity]);
  return (
    <>
      <PageHead
        eyebrow="VULNERABILITY REGISTER"
        title="Findings"
        desc={`${filtered.length} findings across all assessed targets.`}
      />
      <div className="filters">
        <div className="search">
          <Search size={16} />
          <input
            placeholder="Search findings, paths, targets…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </div>
        <Filter
          value={severity}
          set={setSeverity}
          options={["All", "Critical", "High", "Medium", "Low", "Info"]}
        />
        <Filter
          value={tool}
          set={setTool}
          options={["All", "HTTP Scanner", "Nuclei", "OWASP ZAP", "httpx"]}
        />
        <Filter
          value={status}
          set={setStatus}
          options={["All", "Open", "Confirmed", "False_positive", "Resolved"]}
        />
      </div>
      <AsyncState loading={loading} error={error} empty={!filtered.length}><section className="panel table-panel">
        <FindingsTable items={filtered} />
      </section></AsyncState>
    </>
  );
}
const Filter = ({ value, set, options }) => (
  <select value={value} onChange={(e) => set(e.target.value)}>
    {options.map((x) => (
      <option key={x}>{x}</option>
    ))}
  </select>
);
function FindingsTable({ items }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Severity</th>
            <th>Vulnerability</th>
            <th>Target</th>
            <th>Tool</th>
            <th>CWE</th>
            <th>CVSS</th>
            <th>Status</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {items.map((f) => (
            <tr key={f.id}>
              <td>
                <Severity level={f.severity} />
              </td>
              <td>
                <Link to={"/findings/" + f.id}>
                  <b>{f.name}</b>
                  <code>{f.path}</code>
                </Link>
              </td>
              <td>
                <code>{f.target}</code>
              </td>
              <td>{f.tool}</td>
              <td>
                <code>{f.cwe}</code>
              </td>
              <td>
                <b>{f.cvss}</b>
              </td>
              <td>
                <Status>{f.status}</Status>
              </td>
              <td>
                <Link to={"/findings/" + f.id}>
                  <ChevronRight size={16} />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!items.length && (
        <div className="empty">No findings match these filters.</div>
      )}
    </div>
  );
}
function ScanTable({ items = scans }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Scan ID</th>
            <th>Project</th>
            <th>Date</th>
            <th>Status</th>
            <th>Findings</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {items.map((s) => (
            <tr key={s.id}>
              <td>
                <code>{s.id}</code>
              </td>
              <td>{s.project || `Project ${s.project_id || "—"}`}</td>
              <td>{s.date || (s.started_at ? new Date(s.started_at).toLocaleString() : "Pending")}</td>
              <td>
                <Status>{s.status}</Status>
              </td>
              <td>{s.findings ?? s.finding_count ?? "—"}</td>
              <td>
                <Link to={"/scans/" + s.id}>
                  <ChevronRight size={16} />
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Finding() {
  const { id } = useParams();
  const [resolved, setResolved] = useState(false);
  const [toast, setToast] = useState("");
  const [f, setFinding] = useState(seedFindings.find((x) => x.id === id) || seedFindings[0]);
  useEffect(() => { if (/^\d+$/.test(id)) api.getFinding(id).then(row=>{const item=uiFinding(row);setFinding(item);setResolved(item.status==="Resolved")}).catch(()=>{}); },[id]);
  const notify = (m) => {
    setToast(m);
    setTimeout(() => setToast(""), 2500);
  };
  return (
    <>
      <Toast message={toast} />
      <div className="finding-head">
        <Link to="/findings">← All findings</Link>
        <div>
          <Severity level={f.severity} />
          <Status>{resolved ? "Resolved" : f.status}</Status>
        </div>
        <h1>{f.name}</h1>
        <p>
          <code>{f.cwe}</code>
          <span>
            CVSS <b>{f.cvss}</b>
          </span>
          <span>
            Finding <code>{f.id.toUpperCase()}</code>
          </span>
        </p>
        <div className="actions">
          <select aria-label="Finding status" value={(resolved?'resolved':f.status||'open').toLowerCase().replace(' ','_')} onChange={async e=>{try{const row=await api.updateFindingStatus(id,e.target.value);const item=uiFinding(row);setFinding(item);setResolved(item.status==='Resolved');notify('Finding status updated')}catch(error){notify(error.message)}}}>
            <option value="open">Open</option><option value="confirmed">Confirmed</option><option value="false_positive">False positive</option><option value="resolved">Resolved</option>
          </select>
          <button
            className="btn primary"
            onClick={() => {
              setResolved(true);
              notify("Finding marked as resolved");
              if (/^\d+$/.test(id)) api.updateFindingStatus(id,"resolved").catch(error=>notify(error.message));
            }}
          >
            <Check size={16} />
            Mark as resolved
          </button>
          <button
            className="btn"
            onClick={() => notify("Finding export prepared")}
          >
            <Download size={16} />
            Export finding
          </button>
        </div>
      </div>
      <div className="detail-grid">
        <div>
          <Detail title="Overview">
            <p>{f.description||'No scanner description was supplied.'}</p>
          </Detail>
          <Detail title="Affected target">
            <div className="target-box">
              <span>URL</span>
              <code>{f.url||`${f.target}${f.path}`}</code>
              <ExternalLink size={15} />
            </div>
          </Detail>
          <Detail title="Impact">
            <p>{f.impact||'Impact details were not supplied by the scanner.'}</p>
          </Detail>
          <Detail title="Evidence">
            <pre>{f.evidence||'No evidence excerpt was supplied.'}</pre>
          </Detail>
        </div>
        <aside>
          <Detail title="Detection">
            <dl className="detail-dl">
              <dt>Detected by</dt>
              <dd>{f.tool}</dd>
              <dt>Category</dt><dd><code>{f.category||'Uncategorized'}</code></dd>
              <dt>Confidence</dt>
              <dd>High</dd>
              <dt>First seen</dt>
              <dd>
                <code>{f.created_at?new Date(f.created_at).toLocaleString():'Unknown'}</code>
              </dd>
            </dl>
          </Detail>
          <Detail title="Recommendation">
            <p>{f.remediation||'Review the affected behavior and apply vendor security guidance.'}</p>
          </Detail>
          <div className="ai-box">
            <div>
              <Activity size={16} />
              AI security explanation <span>{f.ai_explanation?'AVAILABLE':'OPTIONAL'}</span>
            </div>
            <p>{f.ai_explanation||'No AI explanation was generated. Scanner evidence and remediation remain available above.'}</p>
          </div>
        </aside>
      </div>
    </>
  );
}
const Detail = ({ title, children }) => (
  <section className="detail">
    <h2>{title}</h2>
    {children}
  </section>
);

function Reports() {
  const [toast, setToast] = useState("");
  const [completedScans,setCompletedScans]=useState([]);const [loading,setLoading]=useState(true);const [error,setError]=useState('');const [downloading,setDownloading]=useState('');
  useEffect(()=>{api.getScans().then(rows=>setCompletedScans(rows.filter(s=>s.status==="completed"))).catch(e=>setError(e.message)).finally(()=>setLoading(false))},[]);
  const dl = async (scanId,type) => {
    setDownloading(`${scanId}-${type}`);
    try { await api.downloadReport(scanId,type.toLowerCase()); setToast(`${type} report downloaded`); }
    catch(error) { setToast(error.message); }
    finally { setDownloading(''); }
    setTimeout(() => setToast(""), 2500);
  };
  return (
    <>
      <Toast message={toast} />
      <PageHead
        eyebrow="EXPORTS"
        title="Security Reports"
        desc="Generated assessment summaries ready for review and sharing."
      />
      <AsyncState loading={loading} error={error} empty={!completedScans.length}><div className="reports">
        {completedScans.map((r) => (
          <article className="panel report" key={r.id}>
            <div className="report-icon">
              <FileText />
            </div>
            <div>
              <code>SCN-{String(r.id).padStart(6,'0')}</code>
              <h2>SentinelVAPT Assessment</h2>
              <p>{new URL(r.target_url).host} · {r.completed_at?new Date(r.completed_at).toLocaleDateString():'Completed'}</p>
            </div>
            <div className="report-counts">
              <span>
                <b>{r.finding_count}</b> findings
              </span>
            </div>
            <div className="report-actions">
              <button className="btn" disabled={Boolean(downloading)} onClick={() => dl(r.id,"PDF")}>
                <Download size={15} />
                {downloading===`${r.id}-PDF`?'Preparing…':'PDF'}
              </button>
              <button className="btn" disabled={Boolean(downloading)} onClick={() => dl(r.id,"HTML")}>
                <Download size={15} />
                {downloading===`${r.id}-HTML`?'Preparing…':'HTML'}
              </button>
            </div>
          </article>
        ))}
      </div></AsyncState>
    </>
  );
}
function Settings() {
  const [toast, setToast] = useState("");
  return (
    <>
      <Toast message={toast} />
      <PageHead
        eyebrow="SYSTEM"
        title="Settings"
        desc="Configure local scanner defaults and tool paths."
      />
      <div className="settings-grid">
        {[
          [
            "General",
            [
              ["Application name", "SentinelVAPT"],
              ["Default scan mode", "Standard"],
            ],
          ],
          [
            "Scanning",
            [
              ["Nuclei path", "/usr/local/bin/nuclei"],
              ["httpx path", "/usr/local/bin/httpx"],
              ["ZAP path", "/opt/zaproxy/zap.sh"],
            ],
          ],
          [
            "AI",
            [
              ["Provider", "Local mock provider"],
              ["API status", "Not connected"],
            ],
          ],
          ["Reporting", [["Default format", "PDF + HTML"]]],
        ].map(([name, fields]) => (
          <section className="panel settings-section" key={name}>
            <h2>{name}</h2>
            {fields.map(([label, value]) => (
              <label key={label}>
                <span>{label}</span>
                <input defaultValue={value} />
              </label>
            ))}
          </section>
        ))}
      </div>
      <button
        className="btn primary settings-save"
        onClick={() => {
          setToast("Settings saved locally");
          setTimeout(() => setToast(""), 2500);
        }}
      >
        Save settings
      </button>
    </>
  );
}
function NotFound(){return <div className="not-found"><div className="eyebrow">ERROR / 404</div><h1>Page not found</h1><p>The requested SentinelVAPT workspace route does not exist.</p><Link className="btn primary" to="/dashboard">Return to dashboard</Link></div>}
export default function App() {
  return <Layout />;
}
