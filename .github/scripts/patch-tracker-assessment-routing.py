from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

# Fix previous upgrade typos/type gaps so the production build can proceed.
s = s.replace('allowedSudentIds', 'allowedStudentIds')
s = s.replace(
    'type JoinedSession = ClassSession & { classId: string; gradeLevel: string; section: string; examName: string };',
    'type JoinedSession = ClassSession & { classId: string; gradeLevel: string; section: string; examName: string; examContent?: ExamContent; timeAllowed?: string; assessmentType?: string };'
)

# The exam name itself is now the tracker column name. No class-by-class tracker
# destination dropdown is shown in exam creation. Class Access controls which
# classes receive the exam, and each opened class resolves its own matching
# assessment column by exact exam name + assessment type.
needle = '  const selectedAssessment = teacherAssessments.find((item) => item.id === selectedAssessmentId);\n'
if needle in s:
    s = s.replace(needle, '''  const selectedAssessment = teacherAssessments.find((assessment) => {\n    const classroom = teacherClasses.find((item) => item.id === assessment.classId);\n    return classroom?.gradeLevel === selectedGrade && assessment.title.trim() === examName.trim() && assessment.type.trim().toLowerCase() === assessmentType.trim().toLowerCase();\n  });\n''', 1)

# Remove the deduplicated assessment-choice helper inserted by the previous routing patch.
start = s.find('  const trackerAssessmentChoices = useMemo(() => {')
if start != -1:
    end_marker = '  }, [teacherAssessments, teacherClasses, selectedGrade]);\n'
    end = s.find(end_marker, start)
    if end != -1:
        s = s[:start] + s[end + len(end_marker):]

# Route each class using the exact exam name and assessment type.
old = '''    if (!selectedAssessment) { setSessionMessage("Choose the exact tracker assessment column first."); return; }\n    const destination = selectedAssessment.classId === classroom.id\n      ? selectedAssessment\n      : teacherAssessments.find((item) => item.classId === classroom.id && item.title === selectedAssessment.title && item.type === selectedAssessment.type);\n    if (!destination) { setSessionMessage(`${classroom.section}: matching tracker column “${selectedAssessment.title}” (${selectedAssessment.type}) was not found. Create that column in this class before opening the exam.`); return; }'''
new = '''    const destination = teacherAssessments.find((item) => item.classId === classroom.id && item.title.trim() === examName.trim() && item.type.trim().toLowerCase() === assessmentType.trim().toLowerCase());\n    if (!examName.trim()) { setSessionMessage("Enter the exam name first. The exam name must exactly match the tracker column name."); return; }\n    if (!destination) { setSessionMessage(`${classroom.section}: tracker column “${examName.trim()}” (${assessmentType}) was not found. Create that exact column in this class before opening the exam.`); return; }'''
if old in s:
    s = s.replace(old, new, 1)
else:
    # Fallback for the pre-routing form.
    old2 = '''    if (!selectedAssessment) { setSessionMessage("Choose the exact tracker assessment column first."); return; }\n    const destination = selectedAssessment.classId === classroom.id\n      ? selectedAssessment\n      : teacherAssessments.find((item) => item.classId === classroom.id && item.title === selectedAssessment.title && item.type === selectedAssessment.type);\n    if (!destination) { setSessionMessage(`${classroom.section}: no matching tracker column named ${selectedAssessment.title}.`); return; }'''
    if old2 in s:
        s = s.replace(old2, new, 1)

# Replace either tracker dropdown version with a read-only exact-name mapping.
old_dropdown = '''<label className="field md:col-span-2"><span>Tracker assessment</span><div className="input-icon"><Link2 size={17} /><select value={selectedAssessmentId} onChange={(e) => setSelectedAssessmentId(e.target.value)}><option value="">Choose an existing tracker assessment</option>{trackerAssessmentChoices.map((assessment) => <option key={`${assessment.title}-${assessment.type}-${assessment.max}`} value={assessment.id}>{assessment.title} · {assessment.type} · /{assessment.max}</option>)}</select></div><small>Choose the assessment once. When each class opens, the platform automatically finds the matching column in that student’s class using the same assessment name and type.</small></label>'''
old_original = '''<label className="field md:col-span-2"><span>Exact tracker destination</span><div className="input-icon"><Link2 size={17} /><select value={selectedAssessmentId} onChange={(e) => setSelectedAssessmentId(e.target.value)}><option value="">Choose an existing tracker column</option>{teacherAssessments.filter((assessment) => teacherClasses.some((classroom) => classroom.id === assessment.classId && classroom.gradeLevel === selectedGrade)).map((assessment) => <option key={assessment.id} value={assessment.id}>{assessment.title} · {teacherClasses.find((item) => item.id === assessment.classId)?.section}</option>)}</select></div><small>Results are sent only to this selected assessment column.</small></label>'''
new_field = '''<label className="field md:col-span-2"><span>Tracker column name</span><div className="input-icon"><Link2 size={17} /><input value={examName} readOnly placeholder="Same as Exam name" /></div><small>This exact exam name is used as the tracker column name. Choose which classes can access the exam from Class Access; each class is matched automatically.</small></label>'''
if old_dropdown in s:
    s = s.replace(old_dropdown, new_field, 1)
elif old_original in s:
    s = s.replace(old_original, new_field, 1)
else:
    raise SystemExit('tracker destination field anchor not found')

# New exams no longer depend on a stored class-specific assessment id.
s = s.replace('assessmentId: selectedAssessmentId, assessmentType, timeAllowed, updatedAt:', 'assessmentId: "", assessmentType, timeAllowed, updatedAt:')
s = s.replace('setSelectedAssessmentId(item.assessmentId || "");', 'setSelectedAssessmentId("");')

# Keep maximum mark display useful by deriving it from the exact-name match when available.
s = s.replace('<label className="field"><span>Maximum mark</span><input value={selectedAssessment?.max || 20} readOnly /></label>', '<label className="field"><span>Maximum mark</span><input value={selectedAssessment?.max || 20} readOnly /></label>')

p.write_text(s)
print('exam-name tracker routing applied: one exact column name, classes chosen only through Class Access, automatic per-class matching')
