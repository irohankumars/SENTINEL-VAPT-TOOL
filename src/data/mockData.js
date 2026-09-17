export const metrics={scans:18,open:31,critical:2,high:7};
export const projects=[
 {id:'velora',name:'Velora E-Commerce',url:'https://velora.local',last:'17 Aug 2026',findings:12,critical:1,high:3,medium:5,score:68},
 {id:'campus',name:'Campus Connect',url:'https://campus.sentinel.local',last:'15 Aug 2026',findings:8,critical:0,high:2,medium:4,score:79},
 {id:'api-lab',name:'API Security Lab',url:'https://api-lab.local',last:'12 Aug 2026',findings:11,critical:1,high:2,medium:6,score:61}
];
export const findings=[
 {id:'f-001',severity:'Critical',name:'SQL Injection',path:'/api/login',target:'demo.sentinel.local',tool:'Nuclei',cwe:'CWE-89',cvss:'9.8',status:'Open',ago:'2 hours ago'},
 {id:'f-002',severity:'High',name:'Exposed Environment File',path:'/.env',target:'velora.local',tool:'Nuclei',cwe:'CWE-200',cvss:'7.5',status:'Open',ago:'3 hours ago'},
 {id:'f-003',severity:'Medium',name:'Missing Content-Security-Policy',path:'/',target:'demo.sentinel.local',tool:'OWASP ZAP',cwe:'CWE-693',cvss:'5.3',status:'Open',ago:'4 hours ago'},
 {id:'f-004',severity:'Low',name:'Missing HSTS Header',path:'/',target:'campus.sentinel.local',tool:'OWASP ZAP',cwe:'CWE-319',cvss:'3.1',status:'Open',ago:'4 hours ago'},
 {id:'f-005',severity:'Info',name:'Technology Disclosure',path:'/assets/app.js',target:'api-lab.local',tool:'httpx',cwe:'CWE-200',cvss:'0.0',status:'Resolved',ago:'1 day ago'},
 {id:'f-006',severity:'High',name:'Broken Access Control',path:'/api/users/42',target:'velora.local',tool:'OWASP ZAP',cwe:'CWE-284',cvss:'8.1',status:'Open',ago:'1 day ago'}
];
export const scans=[
 {id:'SCN-2026-0817-001',project:'Velora E-Commerce',date:'17 Aug 2026, 18:21',status:'Completed',findings:12,duration:'02m 41s'},
 {id:'SCN-2026-0815-004',project:'Velora E-Commerce',date:'15 Aug 2026, 10:08',status:'Completed',findings:15,duration:'03m 06s'},
 {id:'SCN-2026-0812-003',project:'API Security Lab',date:'12 Aug 2026, 22:46',status:'Failed',findings:'—',duration:'00m 18s'}
];
export const reports=[
 {id:'RPT-0817',title:'SentinelVAPT Assessment',project:'Velora E-Commerce',date:'17 Aug 2026',findings:12,critical:1,high:3},
 {id:'RPT-0815',title:'Web Application Review',project:'Campus Connect',date:'15 Aug 2026',findings:8,critical:0,high:2}
];
export const logs=['Initializing scan...','Target reachable · HTTP 200','Running httpx reconnaissance','Technology detected: Express','Technology detected: React','Starting nuclei scan','Finding detected: missing-csp','Starting OWASP ZAP','Passive scan completed'];
