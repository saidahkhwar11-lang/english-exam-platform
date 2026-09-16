from pathlib import Path

p = Path("app/page.tsx")
s = p.read_text()

# The exact exam content is the only allowed source of questions.
current_candidates = [
    "  const current = examContent?.questions[level] || [];",
    "  const current = examContent?.questions[level] || questions[level];",
]

current_anchor = next((x for x in current_candidates if x in s), None)

if not current_anchor:
    raise SystemExit(
        "Current question-list anchor not found; refusing unsafe runtime patch."
    )

# Never fall back to the old/sample exam.
if "examContent?.questions[level] || questions[level]" in s:
    s = s.replace(
        "examContent?.questions[level] || questions[level]",
        "examContent?.questions[level] || []",
        1,
    )

# Keep the selected question number inside the available question range.
if "const safeCurrentQuestion =" not in s:
    s = s.replace(
        "  const current = examContent?.questions[level] || [];",
        """  const current = examContent?.questions[level] || [];
  const safeCurrentQuestion = Math.min(
    currentQuestion,
    Math.max(0, current.length - 1)
  );""",
        1,
    )

# Use the safe question index everywhere.
s = s.replace("current[currentQuestion]", "current[safeCurrentQuestion]")

# IMPORTANT:
# Do not allow the question panel to render when there are no questions.
# This prevents the black-screen crash caused by current[0] being undefined.
question_panel_patterns = [
    '{!textMaximized && <section className="question-panel">',
    '{!textMaximized && (\n              <section className="question-panel">',
    '{!textMaximized && (\n            <section className="question-panel">',
]

guard_applied = False

for old in question_panel_patterns:
    if old in s:
        new = old.replace(
            "!textMaximized",
            "current.length > 0 && !textMaximized",
            1,
        )
        s = s.replace(old, new, 1)
        guard_applied = True
        break

# The spelling layout may wrap the normal exam UI in its own conditional.
# In that case, guard the normal branch itself.
if not guard_applied:
    old = "} : <>\n" + '          <div className={`student-exam-grid ${textMaximized ? "text-is-max" : ""}`}>'
    new = "} : current.length > 0 ? <>\n" + '          <div className={`student-exam-grid ${textMaximized ? "text-is-max" : ""}`}>'

    if old in s:
        s = s.replace(old, new, 1)

        close_old = (
            '          </>}\n'
            '          {isSpellingTest && <div className="spelling-submit-row">'
        )
        close_new = (
            '          </> : null}\n'
            '          {isSpellingTest && <div className="spelling-submit-row">'
        )

        if close_old in s:
            s = s.replace(close_old, close_new, 1)

        guard_applied = True

if not guard_applied:
    print("WARNING: exact question-panel wrapper was not found.")
    print("The build will continue instead of failing.")
    print("Search locations:")
    for needle in ["question-panel", "student-exam-grid", "isSpellingTest ?"]:
        pos = s.find(needle)
        print(f"--- {needle}: {pos} ---")
        if pos >= 0:
            print(s[max(0, pos - 1000):pos + 2000])

# Keep currentQuestion synchronized if the number of questions changes.
if "currentQuestion !== safeCurrentQuestion" not in s:
    anchor = """  const safeCurrentQuestion = Math.min(
    currentQuestion,
    Math.max(0, current.length - 1)
  );"""

    effect = anchor + """

  useEffect(() => {
    if (current.length > 0 && currentQuestion !== safeCurrentQuestion) {
      setCurrentQuestion(safeCurrentQuestion);
    }
  }, [current.length, safeCurrentQuestion, currentQuestion]);"""

    if anchor in s:
        s = s.replace(anchor, effect, 1)

p.write_text(s)

print("Student runtime safety patch applied.")
print("Old/sample question fallback disabled.")
print("Empty exam question rendering protected where compatible.")
