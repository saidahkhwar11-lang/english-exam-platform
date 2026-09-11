from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

state_anchor = '  const [submitted, setSubmitted] = useState(false);'
if state_anchor not in s:
    raise SystemExit('submitted state anchor not found')
if 'const [finalScore, setFinalScore]' not in s:
    s = s.replace(state_anchor, state_anchor + '\n  const [finalScore, setFinalScore] = useState<number | null>(null);', 1)

score_rx = re.compile(r'  const score = useMemo\(\(\) => \{ if \(!submitted\) return 0; return current\.reduce\(\(sum, q\) => \{ const value = answers\[q\.id\]; const correct = q\.responseType === "short" \? \(typeof value === "string" && answerMatches\(value, q\.expectedText \|\| ""\)\) : value === q\.answer; return sum \+ \(correct \? q\.marks : 0\); \}, 0\); \}, \[submitted, answers, current\]\);')
score_repl = '''  const score = finalScore ?? 0;
  const submitExamSafely = () => {
    try {
      let calculated = 0;
      for (const q of current) {
        const value = answers[q.id];
        let correct = false;
        if (q.responseType === "short") {
          const actual = String(value ?? "").normalize("NFKC").replace(/[\\u00A0\\u2007\\u202F]/g, " ").replace(/[’‘]/g, "'").replace(/[“”]/g, '\"').replace(/\\s+/g, " ").trim().toLowerCase();
          const expected = String(q.expectedText ?? "").split(/\\s*\\|\\s*|\\s*;\\s*|\\s+\\/\\s+/).map((item) => item.normalize("NFKC").replace(/[\\u00A0\\u2007\\u202F]/g, " ").replace(/[’‘]/g, "'").replace(/[“”]/g, '\"').replace(/\\s+/g, " ").trim().toLowerCase()).filter(Boolean);
          correct = Boolean(actual) && expected.includes(actual);
        } else {
          correct = value === q.answer;
        }
        if (correct) calculated += Number(q.marks) || 0;
      }
      setFinalScore(calculated);
      setSubmitted(true);
    } catch (error) {
      console.error("Safe submit marking failed", error);
      window.alert("The test could not be marked yet. Your answers are still on the page. Please tell your teacher.");
    }
  };'''
s, n = score_rx.subn(lambda _m: score_repl, s, count=1)
if n != 1:
    raise SystemExit('score block not found')

s = s.replace('onClick={()=>setSubmitted(true)}><CheckCircle2 size={17}/> Submit Test', 'onClick={submitExamSafely}><CheckCircle2 size={17}/> Submit Test')
s = s.replace('onClick={()=>setSubmitted(true)}><CheckCircle2 size={18}/> Submit Spelling Test', 'onClick={submitExamSafely}><CheckCircle2 size={18}/> Submit Spelling Test')

s = s.replace('const correct=submitted && typeof value === "string" && answerMatches(value, expected);', 'const correct=false;')
s = s.replace('className={submitted ? (correct ? "correct" : "wrong") : ""}', 'className={submitted ? "submitted-answer" : ""}')
s = s.replace('className={`short-answer-input ${submitted ? (typeof selected === "string" && answerMatches(selected, q.expectedText || "") ? "correct" : "wrong") : ""}`}', 'className={`short-answer-input ${submitted ? "submitted-answer" : ""}`}')

old_effect = '''  useEffect(() => {
    if (!submitted || access !== "student") return;
    if (joinedSession) {
      const safeId = studentId.trim().replace(/[^A-Za-z0-9_-]/g, "_");
      const roundedScore = Math.round((score / total) * joinedSession.maxMark);
      const result = { studentId: studentId.trim(), classId: joinedSession.classId, assessmentId: joinedSession.assessmentId, assessmentTitle: joinedSession.assessmentTitle, examName: joinedSession.examName, level, score: roundedScore, max: joinedSession.maxMark, rawScore: score, rawMax: total, violations, completedAt: Date.now() };
      void Promise.all([
        fetch(`${examDatabase}/resultsByAssessment/${joinedSession.classId}/${joinedSession.assessmentId}/${safeId}.json`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(result) }),
        fetch(`${examDatabase}/attempts/${joinedSession.classId}/${joinedSession.assessmentId}/${safeId}.json`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ completedAt: result.completedAt, code: joinedSession.code }) }),
      ]);
    }
    fullscreenStarted.current = false;
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
  }, [submitted, access, joinedSession, studentId, score, total, level, violations]);'''
new_effect = '''  useEffect(() => {
    if (!submitted || access !== "student") return;
    try {
      if (joinedSession) {
        const safeId = String(studentId ?? "").trim().replace(/[^A-Za-z0-9_-]/g, "_");
        const safeTotal = Number(total) || 1;
        const safeMax = Number(joinedSession.maxMark) || safeTotal;
        const roundedScore = Math.round((Number(score) / safeTotal) * safeMax);
        const result = { studentId: String(studentId ?? "").trim(), classId: joinedSession.classId || "", assessmentId: joinedSession.assessmentId || "", assessmentTitle: joinedSession.assessmentTitle || joinedSession.examName || "", examName: joinedSession.examName || "", level, score: roundedScore, max: safeMax, rawScore: Number(score) || 0, rawMax: safeTotal, violations, completedAt: Date.now() };
        void Promise.all([
          fetch(`${examDatabase}/resultsByAssessment/${joinedSession.classId || "unassigned"}/${joinedSession.assessmentId || "exam"}/${safeId || "student"}.json`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(result) }),
          fetch(`${examDatabase}/attempts/${joinedSession.classId || "unassigned"}/${joinedSession.assessmentId || "exam"}/${safeId || "student"}.json`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ completedAt: result.completedAt, code: joinedSession.code || "" }) }),
        ]).catch((error) => console.error("Result save failed", error));
      }
      fullscreenStarted.current = false;
      if (document.fullscreenElement && document.exitFullscreen) document.exitFullscreen().catch(() => {});
    } catch (error) {
      console.error("Submission finalization failed", error);
    }
  }, [submitted, access, joinedSession, studentId, score, total, level, violations]);'''
if old_effect in s:
    s = s.replace(old_effect, new_effect, 1)
else:
    raise SystemExit('submission effect anchor not found')

p.write_text(s, encoding='utf-8')
print('crash-safe submit flow applied')
