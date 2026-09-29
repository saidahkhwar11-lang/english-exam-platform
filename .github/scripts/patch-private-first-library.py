from pathlib import Path

page = Path("app/page.tsx")
s = page.read_text(encoding="utf-8")

# New exams save privately first.
old = '''    await saveSharedExam(item);
    setLibraryMessage(`Saved “${item.name}” to the shared ${selectedGrade} library.`);
    setLibraryOpen(true);'''
new = '''    const response = await fetch(authenticatedLibraryUrl(`${libraryTeacherKey(teacherEmail)}/${id}`), {
      method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(item),
    });
    if (!response.ok) throw new Error(`Exam was not saved (${response.status}). Please sign in again.`);
    setOlderPersonalExams((items) => [item, ...items.filter((saved) => saved.id !== id)]);
    setEditingPersonalExamId(id);
    setLibraryMessage(`Saved “${item.name}” to My Library.`);
    setLibraryOpen(true);'''
if old not in s:
    raise SystemExit("private-save anchor missing")
s = s.replace(old, new, 1)

# Saving language must no longer imply automatic sharing.
s = s.replace('{personalCopyDraft ? "Save my copy" : editingPersonalExamId ? "Save changes to my library" : "Save & share with grade"}',
              '{personalCopyDraft ? "Save my copy" : editingPersonalExamId ? "Save changes to my library" : "Save to My Library"}')

# Allow the owner to choose a destination grade when sharing a private exam.
anchor = '  const shareOlderExam = async (item: SavedExam) => {'
if anchor not in s:
    raise SystemExit("share function anchor missing")
start=s.index(anchor)
end=s.index("\n  };", start)+5
replacement='''  const shareOlderExam = async (item: SavedExam, targetGrade?: string) => {
    try {
      const chosenGrade = targetGrade || item.grade || selectedGrade;
      const shared: SavedExam = {
        ...item, id: `shared_${libraryTeacherKey(email)}_${item.id}_${libraryGradeKey(chosenGrade)}`,
        grade: chosenGrade, creatorEmail: email.trim().toLowerCase(), updatedAt: Date.now(),
      };
      await saveSharedExam(shared);
      setLibraryMessage(`Shared “${shared.name}” with all teachers under ${chosenGrade}.`);
    } catch (error) {
      setLibraryMessage(error instanceof Error ? error.message : "Unable to share this exam.");
    }
  };'''
s=s[:start]+replacement+s[end:]

# Replace the personal-library block with explicit private actions + grade selector.
old_block='''<p className="mt-2 text-sm text-slate-600">Your earlier exams remain here. Share one to make it available to all teachers in its grade.</p>
        <div className="library-list">{olderPersonalExams.map((item) => <article key={item.id}><div><strong>{item.name}</strong><small>{item.grade} · {item.assessmentType}</small></div>
          <div className="library-actions"><button type="button" onClick={() => { loadSavedExam(item); setLibraryOpen(false); }}>Use exam</button>
          <button type="button" onClick={() => editPersonalExam(item)}>Edit</button>
          <button type="button" onClick={() => void shareOlderExam(item)}>Share with grade</button>
          <button type="button" className="danger-mini" onClick={() => void deletePersonalExam(item)}><Trash2 size={15}/> Delete</button></div></article>)}</div>'''
new_block='''<p className="mt-2 text-sm text-slate-600">Private exams saved by you. Edit, copy, delete, or share a copy with any grade library.</p>
        <div className="library-list">{olderPersonalExams.map((item) => <article key={item.id}><div><strong>{item.name}</strong><small>{item.grade} · {item.assessmentType}</small></div>
          <div className="library-actions"><button type="button" onClick={() => editPersonalExam(item)}>Use & edit</button>
          <button type="button" onClick={() => duplicateSavedExam(item)}><Copy size={15}/> Make a copy</button>
          <select aria-label={`Share ${item.name} with grade`} defaultValue={item.grade || selectedGrade} id={`share-grade-${item.id}`}>{gradeTracks.map((grade) => <option key={grade} value={grade}>{grade}</option>)}</select>
          <button type="button" onClick={() => { const picker=document.getElementById(`share-grade-${item.id}`) as HTMLSelectElement | null; void shareOlderExam(item, picker?.value || item.grade || selectedGrade); }}>Share</button>
          <button type="button" className="danger-mini" onClick={() => void deletePersonalExam(item)}><Trash2 size={15}/> Delete</button></div></article>)}</div>'''
if old_block not in s:
    raise SystemExit("personal library UI anchor missing")
s=s.replace(old_block,new_block,1)

# Shared exams are consumed as personal copies; wording should be explicit.
s=s.replace('>Use and edit</button>', '>Use & edit copy</button>')
s=s.replace('<Copy size={15}/> Make a copy</button>', '<Copy size={15}/> Save copy to My Library</button>', 1)

page.write_text(s, encoding="utf-8")
print("Private-first exam library workflow applied")
