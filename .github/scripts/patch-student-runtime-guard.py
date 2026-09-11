from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

current_anchor = '  const current = examContent?.questions[level] || questions[level];'
if current_anchor not in s:
    raise SystemExit('Current question-list anchor not found; refusing unsafe runtime patch.')

if 'const safeCurrentQuestion =' not in s:
    s = s.replace(
        current_anchor,
        current_anchor + '\n  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));',
        1,
    )

# The crash seen after student login can happen when currentQuestion still points
# to a position from a previous preview/exam while the newly joined exam has fewer
# questions. Clamp every render-time access to the current list.
if 'current[currentQuestion]' in s:
    s = s.replace('current[currentQuestion]', 'current[safeCurrentQuestion]')
else:
    raise SystemExit('No current[currentQuestion] access found; refusing unsafe runtime patch.')

# Reset the page index whenever a new exam/session is loaded or the level changes.
# Insert once next to the existing current-list calculation.
reset_guard = '''\n  useEffect(() => {\n    if (current.length > 0 && currentQuestion !== safeCurrentQuestion) {\n      setCurrentQuestion(safeCurrentQuestion);\n    }\n  }, [current.length, safeCurrentQuestion, currentQuestion]);\n'''
if 'currentQuestion !== safeCurrentQuestion' not in s:
    s = s.replace('  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));', '  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));' + reset_guard, 1)

p.write_text(s)
print('student exam runtime guard applied: stale question index is clamped safely')
