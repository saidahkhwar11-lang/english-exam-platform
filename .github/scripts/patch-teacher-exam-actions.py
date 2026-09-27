from pathlib import Path

page = Path("app/page.tsx")
source = page.read_text(encoding="utf-8")

state = '  const [libraryOpen, setLibraryOpen] = useState(false);'
assert source.count(state) == 1, "Library state changed"
source = source.replace(state, state + '''
  const [newExamPromptOpen, setNewExamPromptOpen] = useState(false);
  const [examActionMessage, setExamActionMessage] = useState("");
''', 1)

old = '    if ((examName || selectedAssessmentId) && !window.confirm("Start a new exam? Save the current exam first if you want to reuse it later.")) return;'
assert source.count(old) == 1, "New Exam confirmation changed"
source = source.replace(old, '''    setNewExamPromptOpen(false);
    setExamActionMessage("");
    const picker = document.getElementById("teacher-test-file-picker") as HTMLInputElement | null;
    if (picker) picker.value = "";''', 1)

old_button = '''onClick={() => { startNewExam(); setUploadedTestFileName(""); const picker = document.getElementById("teacher-test-file-picker") as HTMLInputElement | null; if (picker) picker.value = ""; }}'''
assert source.count(old_button) == 1, "New Exam button changed"
source = source.replace(old_button, '''onClick={() => { if (examContent || examName.trim()) setNewExamPromptOpen(true); else startNewExam(); }}''', 1)

old_save = '''onClick={saveCurrentExam}><Save size={17}/> Save Exam'''
assert source.count(old_save) == 1, "Save Exam button changed"
source = source.replace(old_save, '''onClick={() => {
          setExamActionMessage("");
          if (!examContent) { setExamActionMessage("Please upload and process a test file before saving."); return; }
          void (async () => {
            try {
              const stored = localStorage.getItem("examPlatformTeacherSession");
              const session = stored ? JSON.parse(stored) as { email: string; idToken: string; refreshToken?: string; expiresAt?: number } : null;
              if (!session?.idToken) throw new Error("Please sign in again before saving.");
              if (Date.now() >= (session.expiresAt || 0) - 60000) {
                if (!session.refreshToken) throw new Error("Your session expired. Please sign in again.");
                const response = await fetch("https://securetoken.googleapis.com/v1/token?key=AIzaSyCUizd7pG4mO9li7MqxjYUN-xNE5DDksxQ", {
                  method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded" },
                  body: new URLSearchParams({ grant_type: "refresh_token", refresh_token: session.refreshToken }),
                });
                const refreshed = await response.json() as { id_token?: string; refresh_token?: string; expires_in?: string };
                if (!response.ok || !refreshed.id_token) throw new Error("Your session expired. Please sign in again.");
                localStorage.setItem("examPlatformTeacherSession", JSON.stringify({
                  ...session, idToken: refreshed.id_token, refreshToken: refreshed.refresh_token || session.refreshToken,
                  expiresAt: Date.now() + Number(refreshed.expires_in || 3600) * 1000,
                }));
              }
              await saveCurrentExam();
              setExamActionMessage("Exam saved successfully.");
            } catch (error) {
              setExamActionMessage(error instanceof Error ? error.message : "Unable to save exam. Please try again.");
            }
          })();
        }}><Save size={17}/> Save Exam''', 1)

anchor = '''<button type="button" className="secondary-button" onClick={() => { if (examContent || examName.trim()) setNewExamPromptOpen(true); else startNewExam(); }}><Plus size={17}/> New Exam</button></div>'''
assert source.count(anchor) == 1, "Exam actions layout changed"
source = source.replace(anchor, anchor + '''{examActionMessage && <p role="status" className="mx-6 mb-4 text-sm font-semibold text-slate-700">{examActionMessage}</p>}
        {newExamPromptOpen && <div role="alertdialog" aria-label="Start a new exam" className="mx-6 mb-5 rounded-xl border border-amber-300 bg-amber-50 p-4">
          <p className="font-semibold text-slate-900">Start a new exam?</p>
          <p className="mt-1 text-sm text-slate-700">Save your current exam first if you want to use it again.</p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button type="button" className="secondary-button" onClick={() => setNewExamPromptOpen(false)}>Keep current exam</button>
            <button type="button" className="primary-button compact" onClick={startNewExam}>Start new exam</button>
          </div>
        </div>}''', 1)

page.write_text(source, encoding="utf-8")
print("Teacher exam actions now show confirmation and save errors in the workspace")
