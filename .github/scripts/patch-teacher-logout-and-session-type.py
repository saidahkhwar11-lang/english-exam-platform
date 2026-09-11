from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

# Ensure the joined exam session type includes the uploaded exam content/time.
s = s.replace(
'''const session = await response.json() as (JoinedSession & { allowedStudentIds?: Record<string, boolean>; allowedStudentNames?: Record<string, string> }) | null;''',
'''const session = await response.json() as (JoinedSession & { allowedStudentIds?: Record<string, boolean>; allowedStudentNames?: Record<string, string>; examContent?: ExamContent; timeAllowed?: string }) | null;'''
)

# Add a real teacher logout action. It clears the persistent refresh session and
# teacher-specific UI data, then returns to the sign-in screen.
anchor = '  if (access === "home") return <main className="access-shell">'
if anchor not in s:
    raise SystemExit('home access anchor not found')
logout_fn = '''  const signOutTeacher = () => {\n    localStorage.removeItem("examPlatformTeacherSession");\n    setPassword("");\n    setLoginError("");\n    setTeacherClasses([]);\n    setTeacherStudents([]);\n    setTeacherAssessments([]);\n    setSavedExams([]);\n    setClassSessions({});\n    setLibraryOpen(false);\n    setShowClassAccess(false);\n    setSelectedAssessmentId("");\n    setSessionMessage("");\n    setEmail("");\n    setAccess("home");\n    setActiveTab("teacher");\n  };\n\n'''
if 'const signOutTeacher = () =>' not in s:
    s = s.replace(anchor, logout_fn + anchor, 1)

old_header = '''<div className="hidden items-center gap-2 text-sm text-slate-300 sm:flex"><ShieldCheck size={17} className="text-cyan-300" />Automatic marking · Tracker-ready</div>'''
new_header = '''<div className="flex items-center gap-3"><div className="hidden items-center gap-2 text-sm text-slate-300 sm:flex"><ShieldCheck size={17} className="text-cyan-300" />Automatic marking · Tracker-ready</div>{access === "teacher" && <button type="button" onClick={signOutTeacher} className="rounded-lg border border-white/30 px-3 py-2 text-sm font-semibold text-white transition hover:bg-white/10">Log out</button>}</div>'''
if old_header not in s:
    raise SystemExit('header status anchor not found')
s = s.replace(old_header, new_header, 1)

p.write_text(s)
print('teacher logout + joined-session content type patch applied')
