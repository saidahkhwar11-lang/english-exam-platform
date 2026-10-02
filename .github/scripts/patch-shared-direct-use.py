from pathlib import Path

page = Path("app/page.tsx")
s = page.read_text(encoding="utf-8")

# Shared Library: teachers may run the shared exam immediately.
# Loading it must NOT create a personal draft or require saving to My Library.
old = '<button type="button" onClick={() => customizeSharedExam(item)}>Use & edit copy</button>'
new = '<button type="button" onClick={() => { loadSavedExam(item); setLibraryOpen(false); setExamActionMessage("Shared exam loaded. Open Class Access when you are ready to use it with your class."); }}>Use exam</button>'
if old not in s:
    raise SystemExit("shared direct-use button anchor missing")
s = s.replace(old, new, 1)

# Keep an optional copy action only for teachers who want their own editable version.
s = s.replace('<Copy size={15}/> Save copy to My Library</button>', '<Copy size={15}/> Save editable copy</button>', 1)

page.write_text(s, encoding="utf-8")
print("Shared Library exams can now be used directly without copying to My Library")
