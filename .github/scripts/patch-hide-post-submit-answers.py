"""Hide all answers and exam content after a student submits successfully."""
from pathlib import Path
p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")

# Student submission must end on a neutral confirmation screen. No score,
# correctness colors, correct answers, passage, questions, or selected answers.
anchor='''  if (access === "teacher") {'''
confirmation='''  if (access === "student" && submitted) {
    return <main className="student-submit-success">
      <section className="submit-success-card">
        <div className="submit-success-icon">✓</div>
        <h1>Submitted successfully</h1>
        <p>Thank you, {studentName || "student"}. Your exam has been submitted successfully.</p>
        <p className="submit-success-note">Your responses have been saved. You may now close this page.</p>
      </section>
    </main>;
  }

'''
if 'className="student-submit-success"' not in s:
    if anchor not in s: raise SystemExit("teacher/student render boundary not found")
    s=s.replace(anchor,confirmation+anchor,1)

p.write_text(s,encoding="utf-8")

css=Path("app/globals.css")
style='''
.student-submit-success{min-height:100vh;display:grid;place-items:center;padding:24px;background:linear-gradient(180deg,#eef8f7,#f8fbfc)}.submit-success-card{width:min(520px,100%);background:#fff;border:1px solid #d8e8e7;border-radius:24px;padding:42px 32px;text-align:center;box-shadow:0 18px 50px rgba(23,60,85,.10)}.submit-success-icon{width:70px;height:70px;border-radius:50%;display:grid;place-items:center;margin:0 auto 18px;background:#dff3ed;color:#087b83;font-size:38px;font-weight:900}.submit-success-card h1{margin:0 0 12px;color:#173c55;font-size:28px}.submit-success-card p{margin:0;color:#526b7b;line-height:1.65}.submit-success-card .submit-success-note{margin-top:10px;font-size:14px;color:#728694}
'''
if '.student-submit-success{' not in css.read_text(encoding="utf-8"):
    css.write_text(css.read_text(encoding="utf-8")+style,encoding="utf-8")
print("Student post-submit answers hidden; confirmation screen enabled")
