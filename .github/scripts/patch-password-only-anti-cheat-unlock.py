from pathlib import Path

p = Path("app/page.tsx")
s = p.read_text(encoding="utf-8")

# FINAL student privacy + anti-cheat patch.
# This script runs after all other exam-platform patches.

# 1) Link every newly opened/reset exam code to its teacher account.
session_patterns = [
    ("allowedStudentNames, updatedAt: Date.now()", 'allowedStudentNames, teacherEmail: email.trim().toLowerCase(), updatedAt: Date.now()'),
    ("allowedStudentIds, updatedAt: Date.now()", 'allowedStudentIds, teacherEmail: email.trim().toLowerCase(), updatedAt: Date.now()'),
]
for old, new in session_patterns:
    if old in s and "teacherEmail: email.trim().toLowerCase()" not in s:
        s = s.replace(old, new, 1)
        break

# 2) Student join reads the teacher identity from the exam code and keeps it hidden.
s = s.replace(
    "allowedStudentNames?: Record<string, string> }) | null",
    "allowedStudentNames?: Record<string, string>; teacherEmail?: string }) | null",
)
s = s.replace(
    "allowedStudentIds?: Record<string, boolean> }) | null",
    "allowedStudentIds?: Record<string, boolean>; teacherEmail?: string }) | null",
)
join_anchor = "        setJoinedSession(session);"
if join_anchor in s and "setApprovalEmail(session.teacherEmail ||" not in s:
    s = s.replace(
        join_anchor,
        join_anchor + '\n        setApprovalEmail(session.teacherEmail || "");',
        1,
    )

# 3) Unlock requires ONLY the teacher password. Email is never requested from the student page.
s = s.replace(
    "await verifyTeacherCredentials(teacherEmail || approvalEmail, approvalPassword);",
    "await verifyTeacherCredentials(approvalEmail, approvalPassword);",
)
for old_field in [
    '<label className="field"><span>Teacher email</span><input type="email" value={approvalEmail} onChange={(e)=>setApprovalEmail(e.target.value)} /></label>',
    '<label className="field"><span>Email</span><input type="email" value={approvalEmail} onChange={(e)=>setApprovalEmail(e.target.value)} /></label>',
    '<label className="field"><span>Teacher email</span><input type="email" value={approvalEmail} onChange={(e) => setApprovalEmail(e.target.value)} /></label>',
    '<label className="field"><span>Email</span><input type="email" value={approvalEmail} onChange={(e) => setApprovalEmail(e.target.value)} /></label>',
]:
    s = s.replace(old_field, "")

# 4) Hard privacy boundary after submission: render confirmation only.
# No score, mark, answer correctness, passage, questions, or answer review can remain visible.
if 'className="student-submit-success"' not in s:
    anchors = ['  if (access === "teacher") {', '  if (access === "home") return']
    confirmation = '''  if (access === "student" && submitted) {
    return <main className="student-submit-success">
      <section className="submit-success-card">
        <div className="submit-success-icon">✓</div>
        <h1>Submitted successfully</h1>
        <p>Thank you. Your exam has been submitted successfully.</p>
        <p className="submit-success-note">Your responses have been saved. You may now close this page.</p>
      </section>
    </main>;
  }

'''
    for anchor in anchors:
        if anchor in s:
            s = s.replace(anchor, confirmation + anchor, 1)
            break

p.write_text(s, encoding="utf-8")

css = Path("app/globals.css")
c = css.read_text(encoding="utf-8")
style = '''
.student-submit-success{min-height:100vh;display:grid;place-items:center;padding:24px;background:linear-gradient(180deg,#eef8f7,#f8fbfc)}.submit-success-card{width:min(520px,100%);background:#fff;border:1px solid #d8e8e7;border-radius:24px;padding:42px 32px;text-align:center;box-shadow:0 18px 50px rgba(23,60,85,.10)}.submit-success-icon{width:70px;height:70px;border-radius:50%;display:grid;place-items:center;margin:0 auto 18px;background:#dff3ed;color:#087b83;font-size:38px;font-weight:900}.submit-success-card h1{margin:0 0 12px;color:#173c55;font-size:28px}.submit-success-card p{margin:0;color:#526b7b;line-height:1.65}.submit-success-card .submit-success-note{margin-top:10px;font-size:14px;color:#728694}
'''
if ".student-submit-success{" not in c:
    css.write_text(c + style, encoding="utf-8")

print("Final submit privacy and password-only anti-cheat unlock applied")

# The active session object contains examContent between the student-name map
# and updatedAt; earlier patterns therefore missed the actual session record.
s=p.read_text(encoding="utf-8")
session_anchor="allowedStudentNames, examContent, timeAllowed, updatedAt: Date.now()"
if session_anchor in s:
    s=s.replace(session_anchor,
      'allowedStudentNames, teacherEmail: email.trim().toLowerCase(), examContent, timeAllowed, updatedAt: Date.now()',1)
if 'teacherEmail: email.trim().toLowerCase(), examContent' not in s:
    raise RuntimeError("Teacher email not bound to newly created exam session")
# Unlock ONLY the current exam teacher's password, never a student-entered email.
old='await verifyTeacherCredentials(unlockEmail, unlockPassword);'
if old not in s: raise RuntimeError("Unlock credential call not found")
s=s.replace(old,
  'if (!joinedSession?.teacherEmail) throw new Error("Ask your teacher to reset the exam code before unlocking.");\n      await verifyTeacherCredentials(joinedSession.teacherEmail, unlockPassword);',1)
old_field='<label className="field"><span>Teacher email</span><input type="email" value={unlockEmail} onChange={(e) => setUnlockEmail(e.target.value)} placeholder="Teacher email" /></label>'
if old_field not in s: raise RuntimeError("Locked screen teacher-email field not found")
s=s.replace(old_field,"",1)
p.write_text(s,encoding="utf-8")
print("Locked student screen now requests teacher password only; teacher identity bound to active exam session")
