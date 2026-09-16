from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

# Exam Library is part of the Exam Platform RTDB, not Assessment Tracker.
# Use the already-authenticated teacher Firebase ID token for library reads/writes.
helper_anchor = '  const loadLibrary = async (email:string) => {'
helper = '''  const getExamLibraryAuthToken = () => {\n    try {\n      const raw = localStorage.getItem("examPlatformTeacherSession");\n      const session = raw ? JSON.parse(raw) : null;\n      return String(session?.idToken || "");\n    } catch { return ""; }\n  };\n  const examLibraryUrl = (path:string) => {\n    const token = getExamLibraryAuthToken();\n    return `${EXAM_DB}/examLibrary/${path}.json${token ? `?auth=${encodeURIComponent(token)}` : ""}`;\n  };\n'''
if helper_anchor in s and 'const examLibraryUrl =' not in s:
    s = s.replace(helper_anchor, helper + helper_anchor, 1)

# The generated source currently uses these exact RTDB requests.
s = s.replace('fetch(`${EXAM_DB}/examLibrary/${safeEmail}.json`)', 'fetch(examLibraryUrl(safeEmail))')
s = s.replace('fetch(`${EXAM_DB}/examLibrary/${safeEmail}/${id}.json`, { method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(item) })', 'fetch(examLibraryUrl(`${safeEmail}/${id}`), { method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(item) })')
s = s.replace('fetch(`${EXAM_DB}/examLibrary/${safeEmail}/${item.id}.json`, {method:"DELETE"})', 'fetch(examLibraryUrl(`${safeEmail}/${item.id}`), {method:"DELETE"})')

# Some source revisions use spacing around object literals. Cover those too.
s = s.replace('fetch(`${EXAM_DB}/examLibrary/${safeEmail}/${id}.json`, {method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(item)})', 'fetch(examLibraryUrl(`${safeEmail}/${id}`), {method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(item)})')

# Never report success when Firebase rejected the save.
old = 'await fetch(examLibraryUrl(`${safeEmail}/${id}`), { method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(item) });'
new = 'const saveResponse = await fetch(examLibraryUrl(`${safeEmail}/${id}`), { method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(item) }); if (!saveResponse.ok) throw new Error(`Unable to save exam (${saveResponse.status}). Please sign in again and retry.`);'
if old in s:
    s = s.replace(old, new, 1)
old2 = 'await fetch(examLibraryUrl(`${safeEmail}/${id}`), {method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(item)});'
new2 = 'const saveResponse = await fetch(examLibraryUrl(`${safeEmail}/${id}`), {method:"PUT", headers:{"Content-Type":"application/json"}, body:JSON.stringify(item)}); if (!saveResponse.ok) throw new Error(`Unable to save exam (${saveResponse.status}). Please sign in again and retry.`);'
if old2 in s:
    s = s.replace(old2, new2, 1)

p.write_text(s, encoding='utf-8')
print('Exam Library save/read/delete now use teacher authentication; Assessment Tracker untouched')
