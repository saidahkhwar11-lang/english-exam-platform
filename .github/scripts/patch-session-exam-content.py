from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

# The uploaded/loaded exam is the only valid source of questions. Never fall back
# to the old built-in sample exam, because that makes a new exam show old content.
old_type = 'type JoinedSession = ClassSession & { classId: string; gradeLevel: string; section: string; examName: string };'
new_type = 'type JoinedSession = ClassSession & { classId: string; gradeLevel: string; section: string; examName: string; examContent?: ExamContent; timeAllowed?: string; allowedStudentIds?: Record<string, boolean>; allowedStudentNames?: Record<string, string> };'
if old_type in s:
    s = s.replace(old_type, new_type, 1)

s = s.replace('const current = examContent?.questions[level] || questions[level];', 'const current = examContent?.questions[level] || [];', 1)
s = s.replace('{examContent?.title || "A New Campus"}', '{examContent?.title || "Exam not loaded"}', 1)
s = s.replace('{examContent?.passages[level] || passages[level]}', '{examContent?.passages[level] || ""}', 1)

# Do not let any teacher open a class session without the exact current exam snapshot.
guard = 'if (!selectedAssessment) { setSessionMessage("Choose the exact tracker assessment column first."); return; }'
if guard in s and 'Load or upload the exam content before opening this class.' not in s:
    s = s.replace(guard, guard + '\n    if (!examContent) { setSessionMessage("Load or upload the exam content before opening this class."); return; }', 1)

# The real processor already stores examContent in every class session. Make the
# session label use the teacher's current exam name rather than an older tracker title.
s = s.replace('examName: destination.title, assessmentId: destination.id', 'examName: examName.trim() || destination.title, assessmentId: destination.id', 1)

# Student codes must contain exam content. Old/incomplete codes are rejected rather
# than silently displaying the built-in sample exam.
active_check = 'if (!session?.active) throw new Error("Invalid, expired, or closed exam code. Please check the code with your teacher.");'
if active_check in s and 'This exam code has no exam content.' not in s:
    s = s.replace(active_check, active_check + '\n        if (!session.examContent) throw new Error("This exam code has no exam content. Please ask your teacher to reopen the exam and use a fresh code.");', 1)

# Always replace the current browser exam with the exact snapshot attached to the code.
s = s.replace('if (session.examContent) setExamContent(session.examContent);', 'setExamContent(session.examContent);', 1)

# Teacher preview must not open old/sample questions if nothing is currently loaded.
old_preview = '<button type="button" onClick={() => setActiveTab("student")} className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-3 font-bold text-[#0d2340] hover:bg-cyan-300"><Play size={18} /> Preview {levelMeta[level].label} test</button>'
new_preview = '<button type="button" disabled={!examContent} onClick={() => { if (!examContent) return; setAnswers({}); setSubmitted(false); setCurrentQuestion(0); setActiveTab("student"); }} className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-cyan-400 px-4 py-3 font-bold text-[#0d2340] hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-50"><Play size={18} /> {examContent ? `Preview ${levelMeta[level].label} test` : "Load an exam to preview"}</button>'
if old_preview in s:
    s = s.replace(old_preview, new_preview, 1)

# Level summary also must not report the built-in sample as if it were the new exam.
s = s.replace('(examContent?.questions[item] || questions[item]).length', '(examContent?.questions[item] || []).length')
s = s.replace('(examContent?.questions[item] || questions[item]).reduce((sum,q)=>sum+q.marks,0)', '(examContent?.questions[item] || []).reduce((sum,q)=>sum+q.marks,0)')

p.write_text(s)
print('stale exam fallback removed; exact exam content enforced for preview and student codes')
