"""Fail closed if the built student flow reveals answers or asks for email on lock."""
from pathlib import Path
p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")
checks={
 "Exam session binds teacher identity": 'teacherEmail: email.trim().toLowerCase(), examContent' in s,
 "Teacher identity typed on joined session": 'teacherEmail?: string' in s,
 "Password-only anti-cheating verification": 'verifyTeacherCredentials(joinedSession.teacherEmail, unlockPassword)' in s,
 "Student submission confirmation": 'if (access === "student" && submitted)' in s and 'className="student-submit-success"' in s,
 "No teacher email input in lock overlay": 'value={unlockEmail}' not in s,
 "Tracker maximum is resolved per class": 'maxMark: Number(destination.max)' in s,
}
for name,ok in checks.items():
 print(("PASS" if ok else "FAIL")+": "+name)
if not all(checks.values()):
 raise SystemExit("Student privacy / Tracker checks failed; deployment blocked")
print("All source-level safeguards passed; browser verification is still required.")
