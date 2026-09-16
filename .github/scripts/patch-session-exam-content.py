from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

# Every class session must carry the exact processed exam snapshot that the teacher opened.
old_type = 'type JoinedSession = ClassSession & { classId: string; gradeLevel: string; section: string; examName: string };'
new_type = 'type JoinedSession = ClassSession & { classId: string; gradeLevel: string; section: string; examName: string; examContent?: ExamContent };'
if old_type in s:
    s = s.replace(old_type, new_type, 1)
elif new_type not in s:
    raise SystemExit('JoinedSession type anchor not found')

old_session = 'const session = { code, active, classId: classroom.id, gradeLevel: classroom.gradeLevel, section: classroom.section, examName: destination.title, assessmentId: destination.id, assessmentTitle: destination.title, maxMark: destination.max, allowedStudentIds, updatedAt: Date.now() };'
new_session = 'const session = { code, active, classId: classroom.id, gradeLevel: classroom.gradeLevel, section: classroom.section, examName: examName.trim() || destination.title, assessmentId: destination.id, assessmentTitle: destination.title, maxMark: destination.max, allowedStudentIds, examContent, updatedAt: Date.now() };'
if old_session in s:
    s = s.replace(old_session, new_session, 1)
elif new_session not in s:
    raise SystemExit('class session anchor not found')

# Do not allow a teacher to open an exam unless its actual uploaded/processed content is present.
old_guard = 'if (!selectedAssessment) { setSessionMessage("Choose the exact tracker assessment column first."); return; }'
new_guard = 'if (!selectedAssessment) { setSessionMessage("Choose the exact tracker assessment column first."); return; }\n    if (!examContent) { setSessionMessage("Load or upload the exam content before opening this class."); return; }'
if new_guard not in s:
    if old_guard not in s:
        raise SystemExit('session guard anchor not found')
    s = s.replace(old_guard, new_guard, 1)

# Student must receive the content snapshot belonging to this exact exam code.
old_join = 'if (!session?.active) throw new Error("Invalid, expired, or closed exam code. Please check the code with your teacher.");'
new_join = 'if (!session?.active) throw new Error("Invalid, expired, or closed exam code. Please check the code with your teacher.");\n        if (!session.examContent) throw new Error("This exam code was created before the latest content update. Please ask your teacher to reopen the exam and use the new code.");'
if new_join not in s:
    if old_join not in s:
        raise SystemExit('student session validation anchor not found')
    s = s.replace(old_join, new_join, 1)

old_set = 'setJoinedSession(session);\n        fullscreenStarted.current = true;'
new_set = 'setJoinedSession(session);\n        setExamContent(session.examContent);\n        setExamName(session.examName || session.assessmentTitle || "Exam");\n        setLevel("standard");\n        fullscreenStarted.current = true;'
if new_set not in s:
    if old_set not in s:
        raise SystemExit('student joined session anchor not found')
    s = s.replace(old_set, new_set, 1)

p.write_text(s)
print('session exam-content isolation applied for every exam type and teacher')
