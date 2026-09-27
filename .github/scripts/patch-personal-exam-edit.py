from pathlib import Path

page = Path("app/page.tsx")
source = page.read_text(encoding="utf-8")

anchor = '  const [olderPersonalExams, setOlderPersonalExams] = useState<SavedExam[]>([]);'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n  const [editingPersonalExamId, setEditingPersonalExamId] = useState<string | null>(null);', 1)

anchor = '  const saveCurrentExam = async () => {'
assert source.count(anchor) == 1
source = source.replace(anchor, '''  const savePersonalExamChanges = async (id: string) => {
    const teacherEmail = email.trim().toLowerCase();
    if (!teacherEmail) throw new Error("Please sign in before saving.");
    if (!examContent) throw new Error("This earlier exam has no stored questions. Upload its test file before saving changes.");
    const item: SavedExam = {
      id, name: examName.trim() || "Untitled Exam", grade: selectedGrade, assessmentId: "",
      assessmentType, timeAllowed, updatedAt: Date.now(), content: examContent,
    };
    const response = await fetch(authenticatedLibraryUrl(`${libraryTeacherKey(teacherEmail)}/${id}`), {
      method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(item),
    });
    if (!response.ok) throw new Error(`Changes were not saved (${response.status}). Please sign in again.`);
    setOlderPersonalExams((items) => [item, ...items.filter((saved) => saved.id !== id)]);
    setLibraryMessage(`Updated “${item.name}” in your personal library. The shared grade copy was not changed.`);
    setLibraryOpen(true);
  };
  const editPersonalExam = (item: SavedExam) => {
    loadSavedExam(item);
    setEditingPersonalExamId(item.id);
    setLibraryOpen(false);
    setExamActionMessage(`Editing “${item.name}” in your personal library. Save changes when finished.`);
  };
  const deletePersonalExam = async (item: SavedExam) => {
    if (!window.confirm(`Delete “${item.name}” from your personal library? Any shared grade copy will remain available.`)) return;
    try {
      const response = await fetch(authenticatedLibraryUrl(`${libraryTeacherKey(email)}/${item.id}`), { method: "DELETE" });
      if (!response.ok) throw new Error(`Unable to delete personal exam (${response.status}).`);
      setOlderPersonalExams((items) => items.filter((saved) => saved.id !== item.id));
      if (editingPersonalExamId === item.id) setEditingPersonalExamId(null);
      setLibraryMessage(`Deleted “${item.name}” from your personal library. Shared grade copies remain available.`);
    } catch (error) {
      setLibraryMessage(error instanceof Error ? error.message : "Unable to delete personal exam.");
    }
  };
  const saveCurrentExam = async () => {
    if (editingPersonalExamId) {
      await savePersonalExamChanges(editingPersonalExamId);
      return;
    }''', 1)

anchor = '  const loadSavedExam = (item: SavedExam) => {'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + ' setEditingPersonalExamId(null);', 1)

anchor = '  const startNewExam = () => {'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n    setEditingPersonalExamId(null);', 1)

anchor = '    setOlderPersonalExams([]);'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n    setEditingPersonalExamId(null);', 1)

old = '<button type="button" onClick={() => { loadSavedExam(item); setLibraryOpen(false); }}>Use exam</button>\n          <button type="button" onClick={() => void shareOlderExam(item)}>Share with grade</button>'
assert source.count(old) == 1, "Personal exam actions changed"
source = source.replace(old, '''<button type="button" onClick={() => { loadSavedExam(item); setLibraryOpen(false); }}>Use exam</button>
          <button type="button" onClick={() => editPersonalExam(item)}>Edit</button>
          <button type="button" onClick={() => void shareOlderExam(item)}>Share with grade</button>
          <button type="button" className="danger-mini" onClick={() => void deletePersonalExam(item)}><Trash2 size={15}/> Delete</button>''', 1)

old = 'await saveCurrentExam();\n              setExamActionMessage("Exam saved successfully.");'
assert source.count(old) == 1
source = source.replace(old, '''const wasEditingPersonal = !!editingPersonalExamId;
              await saveCurrentExam();
              setExamActionMessage(wasEditingPersonal ? "Changes saved to your personal library." : "Exam saved to the shared grade library.");''', 1)

old = '<Save size={17}/> Save Exam</button>'
assert source.count(old) == 1
source = source.replace(old, '<Save size={17}/> {editingPersonalExamId ? "Save changes to my library" : "Save Exam"}</button>', 1)

page.write_text(source, encoding="utf-8")
print("Personal exams can be edited and deleted independently of shared grade copies")
