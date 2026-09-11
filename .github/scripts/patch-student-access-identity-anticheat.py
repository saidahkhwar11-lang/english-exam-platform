from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

repls = [
(
'  const [studentId, setStudentId] = useState("");\n',
'  const [studentId, setStudentId] = useState("");\n  const [studentName, setStudentName] = useState("");\n'
),
(
'    const allowedStudentIds = Object.fromEntries(teacherStudents.filter((student) => student.classId === classroom.id).map((student) => [student.studentId.trim().replace(/[^A-Za-z0-9_-]/g, "_"), true]));\n    const session = { code, active, classId: classroom.id, gradeLevel: classroom.gradeLevel, section: classroom.section, examName: destination.title, assessmentId: destination.id, assessmentTitle: destination.title, maxMark: destination.max, allowedStudentIds, updatedAt: Date.now() };',
'    const classStudents = teacherStudents.filter((student) => student.classId === classroom.id);\n    const allowedStudentIds = Object.fromEntries(classStudents.map((student) => [student.studentId.trim().replace(/[^A-Za-z0-9_-]/g, "_"), true]));\n    const allowedStudentNames = Object.fromEntries(classStudents.map((student) => [student.studentId.trim().replace(/[^A-Za-z0-9_-]/g, "_"), student.name || ""]));\n    const session = { code, active, classId: classroom.id, gradeLevel: classroom.gradeLevel, section: classroom.section, examName: destination.title, assessmentId: destination.id, assessmentTitle: destination.title, maxMark: destination.max, allowedStudentIds, allowedStudentNames, updatedAt: Date.now() };'
),
(
'        const session = await response.json() as (JoinedSession & { allowedStudentIds?: Record<string, boolean> }) | null;',
'        const session = await response.json() as (JoinedSession & { allowedStudentIds?: Record<string, boolean>; allowedStudentNames?: Record<string, string> }) | null;'
),
(
'        setJoinedSession(session);\n        setLevel("standard"); setCurrentQuestion(0); setTextMaximized(false);',
'        setJoinedSession(session);\n        setStudentName(session.allowedStudentNames?.[safeId] || "");\n        setLevel("standard"); setCurrentQuestion(0); setTextMaximized(false);'
),
(
'        if (next >= 2) { setLocked(true); setWarning(""); }\n        else setWarning(reason);',
'        if (next >= 1) { setLocked(true); setWarning(""); }\n        else setWarning(reason);'
),
(
'{access === "student" && !submitted && <div className="anti-status"><ShieldCheck size={17} /> Anti-cheating active <b>Violations: {violations}/2</b></div>}',
'{access === "student" && !submitted && <div className="anti-status"><ShieldCheck size={17} /> Anti-cheating active <b>Violations: {violations}/1</b></div>}'
),
(
'<div className="mx-auto max-w-[1500px] px-4 py-5 lg:px-8 lg:py-7"><Tabs value={activeTab} onValueChange={setActiveTab} className="gap-5"><TabsList className="h-11 rounded-xl border border-slate-200 bg-white p-1 shadow-sm"><TabsTrigger value="teacher" className="h-8 px-5"><FileText /> Teacher workspace</TabsTrigger><TabsTrigger value="student" className="h-8 px-5"><GraduationCap /> Student test</TabsTrigger></TabsList>',
'<div className="mx-auto max-w-[1500px] px-4 py-5 lg:px-8 lg:py-7"><Tabs value={activeTab} onValueChange={setActiveTab} className="gap-5">{access === "teacher" && <TabsList className="h-11 rounded-xl border border-slate-200 bg-white p-1 shadow-sm"><TabsTrigger value="teacher" className="h-8 px-5"><FileText /> Teacher workspace</TabsTrigger><TabsTrigger value="student" className="h-8 px-5"><GraduationCap /> Student test</TabsTrigger></TabsList>}'
),
(
'          <div className="level-change-row"><span>All students start on <b>Standard Level</b>. A teacher must approve any change.</span>',
'          {access === "student" && <div className="student-identity-row"><span><UserRound size={17}/> Student: <b>{studentName || "—"}</b></span><span>Student ID: <b>{studentId}</b></span></div>}\n          <div className="level-change-row"><span>All students start on <b>Standard Level</b>. A teacher must approve any change.</span>'
),
]

for old, new in repls:
    if old not in s:
        raise SystemExit(f'missing expected source: {old[:90]}')
    s = s.replace(old, new, 1)

s = s.replace('Violation {violations} of 2: {warning}', 'Violation {violations}: {warning}')
s = s.replace('You have {2 - violations} {2 - violations === 1 ? "chance" : "chances"} remaining. The test will lock on the second violation.', 'The test locks immediately after a violation and requires teacher approval to continue.')
p.write_text(s)

css_path = Path('app/globals.css')
c = css_path.read_text()
if '.student-identity-row' not in c:
    c += '''\n.student-identity-row{display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:flex-start;border:1px solid #cfe3f7;background:#f8fbff;border-radius:14px;padding:12px 16px;color:#17324d}.student-identity-row span{display:flex;align-items:center;gap:7px}.student-identity-row b{color:#0d2340}\n'''
css_path.write_text(c)
print('student access, identity, and first-violation lock patch applied')
