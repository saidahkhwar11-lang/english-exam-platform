from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

# Do not calculate correctness while the student is typing. The previous
# universal scorer re-ran answer checking on every keystroke. Keep answers as
# plain state during the attempt and evaluate them only after Submit.
score_rx = re.compile(
    r'  const score = useMemo\(\(\) => current\.reduce\(\(sum, q\) => \{ const value = answers\[q\.id\]; const correct = q\.responseType === "short" \? \(typeof value === "string" && answerMatches\(value, q\.expectedText \|\| ""\)\) : value === q\.answer; return sum \+ \(correct \? q\.marks : 0\); \}, 0\), \[answers, current\]\);'
)
score_repl = '  const score = useMemo(() => { if (!submitted) return 0; return current.reduce((sum, q) => { const value = answers[q.id]; const correct = q.responseType === "short" ? (typeof value === "string" && answerMatches(value, q.expectedText || "")) : value === q.answer; return sum + (correct ? q.marks : 0); }, 0); }, [submitted, answers, current]);'
s, n = score_rx.subn(score_repl, s, count=1)
if n != 1:
    raise SystemExit('score block not found; refusing unsafe change')

# In the spelling layout, correctness was also being evaluated while typing
# even though the CSS result is only shown after submit. Gate those comparisons
# behind submitted as well.
s = s.replace(
    'const correct=typeof value === "string" && answerMatches(value, expected);',
    'const correct=submitted && typeof value === "string" && answerMatches(value, expected);'
)
s = s.replace(
    'const correct = typeof value === "string" && answerMatches(value, expected);',
    'const correct = submitted && typeof value === "string" && answerMatches(value, expected);'
)

# Keep normal exam short-answer correctness dormant until submit too.
s = s.replace(
    'const correct = typeof selected === "string" && answerMatches(selected, q.expectedText || "");',
    'const correct = submitted && typeof selected === "string" && answerMatches(selected, q.expectedText || "");'
)

p.write_text(s, encoding='utf-8')
print('answer checking deferred until submit; typing remains state-only')
