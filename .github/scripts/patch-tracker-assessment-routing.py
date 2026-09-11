from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

# Fix typo introduced by exam-content upgrade so the build can proceed.
s = s.replace('allowedSudentIds', 'allowedStudentIds')

# Build one deduplicated tracker-assessment list per grade. The selected item is
# only a template (title/type/max); each class is resolved to its own matching
# assessment column when that class is opened.
needle = '  const selectedAssessment = teacherAssessments.find((item) => item.id === selectedAssessmentId);\n'
insert = '''  const selectedAssessment = teacherAssessments.find((item) => item.id === selectedAssessmentId);\n  const trackerAssessmentChoices = useMemo(() => {\n    const classIds = new Set(teacherClasses.filter((classroom) => classroom.gradeLevel === selectedGrade).map((classroom) => classroom.id));\n    const seen = new Set<string>();\n    return teacherAssessments.filter((assessment) => classIds.has(assessment.classId)).filter((assessment) => {\n      const key = `${assessment.title.trim().toLowerCase()}__${assessment.type.trim().toLowerCase()}__${assessment.max}`;\n      if (seen.has(key)) return false;\n      seen.add(key);\n      return true;\n    });\n  }, [teacherAssessments, teacherClasses, selectedGrade]);\n'''
if needle not in s:
    raise SystemExit('selectedAssessment anchor not found')
s = s.replace(needle, insert, 1)

# Replace the duplicated class-by-class destination dropdown with a single
# assessment-name selector. Existing selectedAssessmentId state is preserved
# so saved exams and class routing stay backward compatible.
old = '''<label className="field md:col-span-2"><span>Exact tracker destination</span><div className="input-icon"><Link2 size={17} /><select value={selectedAssessmentId} onChange={(e) => setSelectedAssessmentId(e.target.value)}><option value="">Choose an existing tracker column</option>{teacherAssessments.filter((assessment) => teacherClasses.some((classroom) => classroom.id === assessment.classId && classroom.gradeLevel === selectedGrade)).map((assessment) => <option key={assessment.id} value={assessment.id}>{assessment.title} · {teacherClasses.find((item) => item.id === assessment.classId)?.section}</option>)}</select></div><small>Results are sent only to this selected assessment column.</small></label>'''
new = '''<label className="field md:col-span-2"><span>Tracker assessment</span><div className="input-icon"><Link2 size={17} /><select value={selectedAssessmentId} onChange={(e) => setSelectedAssessmentId(e.target.value)}><option value="">Choose an existing tracker assessment</option>{trackerAssessmentChoices.map((assessment) => <option key={`${assessment.title}-${assessment.type}-${assessment.max}`} value={assessment.id}>{assessment.title} · {assessment.type} · /{assessment.max}</option>)}</select></div><small>Choose the assessment once. When each class opens, the platform automatically finds the matching column in that student’s class using the same assessment name and type.</small></label>'''
if old not in s:
    raise SystemExit('tracker destination dropdown anchor not found')
s = s.replace(old, new, 1)

# Make the missing-column error explicit and safe. Never write to a different
# class when the matching assessment column is absent.
s = s.replace('if (!destination) { setSessionMessage(`${classroom.section}: no matching tracker column named ${selectedAssessment.title}.`); return; }',
'''if (!destination) { setSessionMessage(`${classroom.section}: matching tracker column “${selectedAssessment.title}” (${selectedAssessment.type}) was not found. Create that column in this class before opening the exam.`); return; }''')

# Clarify the class-session mapping in stored data while preserving all old fields.
s = s.replace('assessmentTitle: destination.title, maxMark: destination.max, allowedStudentIds, allowedStudentNames, examContent:',
'''assessmentTitle: destination.title, assessmentType: destination.type, maxMark: destination.max, allowedStudentIds, allowedStudentNames, examContent:''')

p.write_text(s)
print('tracker assessment routing patch applied: one assessment choice, automatic per-class destination, safe missing-column check')
