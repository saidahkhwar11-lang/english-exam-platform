from pathlib import Path

page = Path("app/page.tsx")
source = page.read_text(encoding="utf-8")

old_type = "type SavedExam = { id: string; name: string; grade: string; assessmentId: string; assessmentType: string; timeAllowed: string; updatedAt: number; content?: ExamContent };"
assert source.count(old_type) == 1
source = source.replace(old_type, old_type.replace("content?: ExamContent", "content?: ExamContent; creatorEmail?: string"), 1)

state = '  const [savedExams, setSavedExams] = useState<SavedExam[]>([]);'
assert source.count(state) == 1
source = source.replace(state, state + '''
  const [olderPersonalExams, setOlderPersonalExams] = useState<SavedExam[]>([]);
  const [libraryGrade, setLibraryGrade] = useState("Grade 7");
  const [libraryLoading, setLibraryLoading] = useState(false);
''', 1)

start = source.index("  const loadSavedExamLibrary = async (teacherEmail: string) => {")
end = source.index("\n\n  const runTrackerQuery", start)
source = source[:start] + '''  const libraryTeacherKey = (teacherEmail: string) => teacherEmail.trim().toLowerCase().replace(/[^A-Za-z0-9_-]/g, "_");
  const libraryGradeKey = (grade: string) => grade.replace(/[^A-Za-z0-9_-]/g, "_");
  const authenticatedLibraryUrl = (path: string) => {
    const raw = localStorage.getItem("examPlatformTeacherSession");
    const session = raw ? JSON.parse(raw) as { idToken?: string } : null;
    if (!session?.idToken) throw new Error("Please sign in again to access the exam library.");
    return `${examDatabase}/examLibrary/${path}.json?auth=${encodeURIComponent(session.idToken)}`;
  };
  const readLibrary = async (path: string) => {
    const response = await fetch(authenticatedLibraryUrl(path));
    if (!response.ok) throw new Error(`Unable to open the exam library (${response.status}). Please sign in again or contact the coordinator.`);
    const data = await response.json() as Record<string, SavedExam> | null;
    return data || {};
  };
  const loadSavedExamLibrary = async (teacherEmail: string) => {
    setLibraryLoading(true);
    try {
      const ownKey = libraryTeacherKey(teacherEmail);
      const [sharedResult, personalResult] = await Promise.allSettled([
        readLibrary("sharedByGrade"),
        readLibrary(ownKey),
      ]);
      const shared = sharedResult.status === "fulfilled" ? sharedResult.value : {};
      const personal = personalResult.status === "fulfilled" ? personalResult.value : {};
      const sharedItems = Object.entries(shared).flatMap(([gradeKey, entries]) =>
        Object.entries((entries || {}) as unknown as Record<string, SavedExam>).map(([id, item]) => ({
          ...item, id, grade: item.grade || gradeTracks.find((grade) => libraryGradeKey(grade) === gradeKey) || gradeKey,
        }))
      );
      setSavedExams(sharedItems.sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0)));
      setOlderPersonalExams(Object.entries(personal).map(([id, item]) => ({ ...item, id }))
        .filter((item) => !!item?.name).sort((a, b) => (b.updatedAt || 0) - (a.updatedAt || 0)));
      setLibraryMessage(sharedResult.status === "rejected"
        ? "The shared library could not be opened. Please contact the coordinator to allow teacher access."
        : personalResult.status === "rejected" ? "Your earlier personal exams could not be opened." : "");
    } catch (error) {
      setLibraryMessage(error instanceof Error ? error.message : "Unable to load the exam library.");
    } finally {
      setLibraryLoading(false);
    }
  };''' + source[end:]

start = source.index("  const saveCurrentExam = async () => {")
end = source.index("\n  const loadSavedExam =", start)
source = source[:start] + '''  const saveSharedExam = async (item: SavedExam) => {
    const path = `sharedByGrade/${libraryGradeKey(item.grade)}/${item.id}`;
    const response = await fetch(authenticatedLibraryUrl(path), {
      method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(item),
    });
    if (!response.ok) throw new Error(`Exam was not saved (${response.status}). Please sign in again or contact the coordinator.`);
    setSavedExams((items) => [item, ...items.filter((saved) => saved.id !== item.id)]);
    setLibraryGrade(item.grade);
  };
  const saveCurrentExam = async () => {
    const teacherEmail = email.trim().toLowerCase();
    if (!teacherEmail) throw new Error("Please sign in before saving.");
    if (!examContent) throw new Error("Upload and process a test file before saving.");
    const id = `exam_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const item: SavedExam = {
      id, name: examName.trim() || "Untitled Exam", grade: selectedGrade, assessmentId: "",
      assessmentType, timeAllowed, updatedAt: Date.now(), content: examContent, creatorEmail: teacherEmail,
    };
    await saveSharedExam(item);
    setLibraryMessage(`Saved “${item.name}” to the shared ${selectedGrade} library.`);
    setLibraryOpen(true);
  };
  const shareOlderExam = async (item: SavedExam) => {
    try {
      const shared: SavedExam = {
        ...item, id: `shared_${libraryTeacherKey(email)}_${item.id}`,
        grade: item.grade || selectedGrade, creatorEmail: email.trim().toLowerCase(), updatedAt: Date.now(),
      };
      await saveSharedExam(shared);
      setLibraryMessage(`Shared “${shared.name}” with all teachers under ${shared.grade}.`);
    } catch (error) {
      setLibraryMessage(error instanceof Error ? error.message : "Unable to share this exam.");
    }
  };''' + source[end:]

start = source.index("  const deleteSavedExam = async (item: SavedExam) => {")
end = source.index("\n  const startNewExam", start)
source = source[:start] + '''  const deleteSavedExam = async (item: SavedExam) => {
    if (item.creatorEmail?.toLowerCase() !== email.trim().toLowerCase()) return;
    if (!window.confirm(`Remove “${item.name}” from the shared ${item.grade} library?`)) return;
    try {
      const response = await fetch(authenticatedLibraryUrl(`sharedByGrade/${libraryGradeKey(item.grade)}/${item.id}`), { method: "DELETE" });
      if (!response.ok) throw new Error(`Unable to remove exam (${response.status}).`);
      setSavedExams((items) => items.filter((saved) => saved.id !== item.id));
      setLibraryMessage("Exam removed from the shared library.");
    } catch (error) {
      setLibraryMessage(error instanceof Error ? error.message : "Unable to remove exam.");
    }
  };''' + source[end:]

source = source.replace('    setSavedExams([]);', '    setSavedExams([]);\n    setOlderPersonalExams([]);', 1)

start = source.index('    {access === "teacher" && libraryOpen && <div className="library-overlay">')
end = source.index('\n    {access === "teacher" && showClassAccess', start)
source = source[:start] + '''    {access === "teacher" && libraryOpen && <div className="library-overlay"><section className="exam-library">
      <div className="library-head"><div><small>SHARED EXAM LIBRARY</small><h2>Exams by grade</h2></div><button type="button" className="icon-close" onClick={() => setLibraryOpen(false)} aria-label="Close library">×</button></div>
      <p>Choose a grade, then load an exam for your own class. Your class code and tracker column are set separately.</p>
      <div className="mt-4 flex flex-wrap gap-2">{gradeTracks.map((grade) => <button type="button" key={grade} onClick={() => setLibraryGrade(grade)} className={`secondary-button text-sm ${libraryGrade === grade ? "border-cyan-600 bg-cyan-50 text-cyan-900" : ""}`}>{grade} ({savedExams.filter((item) => item.grade === grade).length})</button>)}</div>
      {libraryMessage && <div role="status" className="session-message mt-3">{libraryMessage}</div>}
      {libraryLoading && <p className="mt-3 text-sm">Loading exams…</p>}
      <div className="library-list">{savedExams.filter((item) => item.grade === libraryGrade).map((item) => <article key={item.id}>
        <div><strong>{item.name}</strong><small>{item.assessmentType} · {item.timeAllowed} · {item.creatorEmail || "Teacher"}</small></div>
        <div className="library-actions"><button type="button" onClick={() => { loadSavedExam(item); setLibraryOpen(false); }}>Use exam</button>
          <button type="button" onClick={() => { duplicateSavedExam(item); setLibraryOpen(false); }}><Copy size={15}/> Make a copy</button>
          {item.creatorEmail?.toLowerCase() === email.trim().toLowerCase() && <button type="button" className="danger-mini" onClick={() => void deleteSavedExam(item)}><Trash2 size={15}/> Remove</button>}</div>
      </article>)}{!libraryLoading && savedExams.filter((item) => item.grade === libraryGrade).length === 0 && <div className="session-empty">No shared exams in {libraryGrade} yet.</div>}</div>
      {olderPersonalExams.length > 0 && <details className="mt-5 rounded-xl border border-slate-200 p-3"><summary className="cursor-pointer font-semibold">My earlier personal exams ({olderPersonalExams.length})</summary>
        <p className="mt-2 text-sm text-slate-600">Your earlier exams remain here. Share one to make it available to all teachers in its grade.</p>
        <div className="library-list">{olderPersonalExams.map((item) => <article key={item.id}><div><strong>{item.name}</strong><small>{item.grade} · {item.assessmentType}</small></div>
          <div className="library-actions"><button type="button" onClick={() => { loadSavedExam(item); setLibraryOpen(false); }}>Use exam</button>
          <button type="button" onClick={() => void shareOlderExam(item)}>Share with grade</button></div></article>)}</div>
      </details>}
    </section></div>}''' + source[end:]

old_button = 'onClick={() => setLibraryOpen(true)}><Library size={17}/> My Exam Library ({savedExams.length})'
assert source.count(old_button) == 1, "Library button changed"
source = source.replace(old_button, '''onClick={() => { setLibraryGrade(selectedGrade); setLibraryOpen(true); void loadSavedExamLibrary(email); }}><Library size={17}/> Shared Exam Library''', 1)

page.write_text(source, encoding="utf-8")
print("Exams save to a shared grade library; earlier personal exams remain available")
