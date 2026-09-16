from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

# Read the tracker maximum robustly whether Firestore stores it as an integer or double.
s = s.replace(
    'max: Number(doc.fields?.max?.integerValue || 20),',
    'max: Number(doc.fields?.max?.integerValue ?? (doc.fields?.max as { doubleValue?: number } | undefined)?.doubleValue ?? 20),'
)

# The exact tracker column is the authority for the exam maximum mark.
# Keep this derived/read-only: this patch never writes to Assessment Tracker.
anchor = '''  const selectedAssessment = teacherAssessments.find((assessment) => {
    const classroom = teacherClasses.find((item) => item.id === assessment.classId);
    return classroom?.gradeLevel === selectedGrade && assessment.title.trim() === examName.trim() && assessment.type.trim().toLowerCase() === assessmentType.trim().toLowerCase();
  });'''
replacement = anchor + '''
  const trackerMaximumMark = selectedAssessment ? Number(selectedAssessment.max) || 20 : 20;'''
if anchor in s and 'const trackerMaximumMark =' not in s:
    s = s.replace(anchor, replacement, 1)

# New Exam maximum mark display must always mirror the matching Tracker column.
s = s.replace(
    '<label className="field"><span>Maximum mark</span><input value={selectedAssessment?.max || 20} readOnly /></label>',
    '<label className="field"><span>Maximum mark</span><input value={trackerMaximumMark} readOnly /></label>',
)

# Preserve the per-class tracker maximum in the class session. Student result saving
# already scales raw question points to joinedSession.maxMark, so the score sent to
# the tracker is on the tracker column scale.
s = s.replace('maxMark: destination.max,', 'maxMark: Number(destination.max) || trackerMaximumMark,')

p.write_text(s, encoding='utf-8')
print('tracker maximum-mark synchronization applied; tracker remains read-only')
