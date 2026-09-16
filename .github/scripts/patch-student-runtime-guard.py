from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text()

current_candidates = [
    '  const current = examContent?.questions[level] || [];',
    '  const current = examContent?.questions[level] || questions[level];',
]
current_anchor = next((x for x in current_candidates if x in s), None)
if not current_anchor:
    raise SystemExit('Current question-list anchor not found; refusing unsafe runtime patch.')

if 'const safeCurrentQuestion =' not in s:
    s = s.replace(current_anchor, current_anchor + '\n  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));', 1)

if 'current[currentQuestion]' in s:
    s = s.replace('current[currentQuestion]', 'current[safeCurrentQuestion]')
elif 'current[safeCurrentQuestion]' not in s:
    raise SystemExit('No current question access found; refusing unsafe runtime patch.')

reset_guard = '''\n  useEffect(() => {\n    if (current.length > 0 && currentQuestion !== safeCurrentQuestion) {\n      setCurrentQuestion(safeCurrentQuestion);\n    }\n  }, [current.length, safeCurrentQuestion, currentQuestion]);\n'''
if 'currentQuestion !== safeCurrentQuestion' not in s:
    s = s.replace('  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));', '  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));' + reset_guard, 1)

# Spelling layout wraps the normal exam grid in: {isSpellingTest ? ... : <> NORMAL </>}
# Guard that normal branch when no exact exam content is loaded. This avoids dereferencing
# current[0] on the home/teacher screen while preserving the dedicated spelling layout.
normal_branch = '} : <>\n          <div className={`student-exam-grid ${textMaximized ? "text-is-max" : ""}`}'
guarded_branch = '} : current.length > 0 ? <>\n          <div className={`student-exam-grid ${textMaximized ? "text-is-max" : ""}`}'
if guarded_branch not in s:
    if normal_branch in s:
        s = s.replace(normal_branch, guarded_branch, 1)
        # Close the added ternary at the end of the normal fragment.
        close_anchor = '          </>}\n          {isSpellingTest && <div className="spelling-submit-row">'
        close_replacement = '          </> : null}\n          {isSpellingTest && <div className="spelling-submit-row">'
        if close_anchor not in s:
            raise SystemExit('Spelling normal-branch close anchor not found; refusing unsafe runtime patch.')
        s = s.replace(close_anchor, close_replacement, 1)
    else:
        # Compatibility for non-spelling layouts.
        pat = r'\{!textIsMaximized\s*&&\s*\(\s*<section className="question-panel">'
        s2, count = re.subn(pat, '{current.length > 0 && !textIsMaximized && (\n              <section className="question-panel">', s, count=1)
        if not count:
            raise SystemExit('No compatible empty-exam render guard anchor found; refusing unsafe runtime patch.')
        s = s2

p.write_text(s)
print('student runtime guard applied after spelling layout: empty exam cannot render normal question UI')
