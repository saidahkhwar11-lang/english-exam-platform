from pathlib import Path

page = Path("app/page.tsx")
source = page.read_text(encoding="utf-8")

state = '  const [editingPersonalExamId, setEditingPersonalExamId] = useState<string | null>(null);'
assert source.count(state) == 1
source = source.replace(state, state + '''
  const [personalCopyDraft, setPersonalCopyDraft] = useState(false);
  const [sharedExamSourceName, setSharedExamSourceName] = useState<string | null>(null);
''', 1)

old = '    setOlderPersonalExams((items) => [item, ...items.filter((saved) => saved.id !== id)]);\n    setLibraryMessage(`Updated “${item.name}” in your personal library. The shared grade copy was not changed.`);'
assert source.count(old) == 1
source = source.replace(old, '''    setOlderPersonalExams((items) => [item, ...items.filter((saved) => saved.id !== id)]);
    setLibraryMessage(personalCopyDraft
      ? `Saved “${item.name}” as your personal copy. The shared exam was not changed.`
      : `Updated “${item.name}” in your personal library. The shared grade copy was not changed.`);
    setPersonalCopyDraft(false);''', 1)

old = '    setEditingPersonalExamId(item.id);\n    setLibraryOpen(false);'
assert source.count(old) == 1
source = source.replace(old, '    setEditingPersonalExamId(item.id);\n    setPersonalCopyDraft(false);\n    setSharedExamSourceName(null);\n    setLibraryOpen(false);', 1)

old = '  const loadSavedExam = (item: SavedExam) => { setEditingPersonalExamId(null);'
assert source.count(old) == 1
source = source.replace(old, '  const loadSavedExam = (item: SavedExam) => { setEditingPersonalExamId(null); setPersonalCopyDraft(false); setSharedExamSourceName(null);', 1)

old = '  const duplicateSavedExam = async (item: SavedExam) => { setExamName(`${item.name} Copy`); loadSavedExam({ ...item, name: `${item.name} Copy` }); setLibraryMessage("Copy loaded. Edit it and click Save Exam to keep it as a new library item."); };'
assert source.count(old) == 1
source = source.replace(old, '''  const customizeSharedExam = (item: SavedExam, copy = false) => {
    loadSavedExam({ ...item, name: copy ? `${item.name} Copy` : item.name });
    setEditingPersonalExamId(`exam_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`);
    setPersonalCopyDraft(true);
    setSharedExamSourceName(item.name);
    setLibraryOpen(false);
    setExamActionMessage("Choose the exact name of your tracker column, then open the exam for your class. Save my copy if you want to reuse your changes.");
  };
  const duplicateSavedExam = (item: SavedExam) => customizeSharedExam(item, true);''', 1)

old = '  const startNewExam = () => {\n    setEditingPersonalExamId(null);'
assert source.count(old) == 1
source = source.replace(old, '  const startNewExam = () => {\n    setEditingPersonalExamId(null);\n    setPersonalCopyDraft(false);\n    setSharedExamSourceName(null);', 1)

old = '    setEditingPersonalExamId(null);\n    setClassSessions({});'
assert source.count(old) == 1
source = source.replace(old, '    setEditingPersonalExamId(null);\n    setPersonalCopyDraft(false);\n    setSharedExamSourceName(null);\n    setClassSessions({});', 1)

old = '<button type="button" onClick={() => { loadSavedExam(item); setLibraryOpen(false); }}>Use exam</button>\n          <button type="button" onClick={() => { duplicateSavedExam(item); setLibraryOpen(false); }}>'
assert source.count(old) == 1, "Shared library buttons changed"
source = source.replace(old, '<button type="button" onClick={() => customizeSharedExam(item)}>Use and edit</button>\n          <button type="button" onClick={() => duplicateSavedExam(item)}>', 1)

old = 'const wasEditingPersonal = !!editingPersonalExamId;\n              await saveCurrentExam();\n              setExamActionMessage(wasEditingPersonal ? "Changes saved to your personal library." : "Exam saved to the shared grade library.");'
assert source.count(old) == 1
source = source.replace(old, '''const wasEditingPersonal = !!editingPersonalExamId;
              const wasPersonalDraft = personalCopyDraft;
              await saveCurrentExam();
              setExamActionMessage(wasPersonalDraft ? "Personal copy saved; the shared exam is unchanged." : wasEditingPersonal ? "Changes saved to your personal library." : "Exam saved to the shared grade library.");''', 1)

old = '{editingPersonalExamId ? "Save changes to my library" : "Save Exam"}'
assert source.count(old) == 1
source = source.replace(old, '{personalCopyDraft ? "Save my copy" : editingPersonalExamId ? "Save changes to my library" : "Save Exam"}', 1)

anchor = '<div className="grid gap-5 p-6 md:grid-cols-2"><div className="field md:col-span-2">'
assert source.count(anchor) == 1, "Teacher builder changed"
banner = '''{sharedExamSourceName && <div className="mx-6 mt-5 rounded-xl border border-cyan-200 bg-cyan-50 p-4 text-sm text-slate-800">
          <strong>Using a copy of “{sharedExamSourceName}”</strong>
          <p className="mt-1">Choose your tracker column name below or type its exact name in Exam name. Changes here will not alter the shared exam.</p>
          <label className="field mt-3"><span>My tracker column</span><select value={teacherAssessments.some((assessment) => assessment.title === examName) ? examName : ""} onChange={(event) => { if (event.target.value) setExamName(event.target.value); }}>
            <option value="">Choose a column from my classes</option>
            {Array.from(new Set(teacherAssessments.filter((assessment) =>
              teacherClasses.some((classroom) => classroom.id === assessment.classId && classroom.gradeLevel === selectedGrade)
              && assessment.type.trim().toLowerCase() === assessmentType.trim().toLowerCase()
            ).map((assessment) => assessment.title))).map((title) => <option key={title} value={title}>{title}</option>)}
          </select></label>
          <p className="mt-2">To reuse your renamed version, click Save my copy. You can open Class Access after choosing the exact tracker name.</p>
        </div>}
        '''
source = source.replace(anchor, banner + anchor, 1)

page.write_text(source, encoding="utf-8")
print("Shared exams open as editable personal copies with tracker column selection")
