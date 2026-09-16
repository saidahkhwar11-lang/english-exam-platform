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
    s = s.replace(
        current_anchor,
        current_anchor + '\n  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));',
        1,
    )

if 'current[currentQuestion]' in s:
    s = s.replace('current[currentQuestion]', 'current[safeCurrentQuestion]')
elif 'current[safeCurrentQuestion]' not in s:
    raise SystemExit('No current question access found; refusing unsafe runtime patch.')

reset_guard = '''\n  useEffect(() => {\n    if (current.length > 0 && currentQuestion !== safeCurrentQuestion) {\n      setCurrentQuestion(safeCurrentQuestion);\n    }\n  }, [current.length, safeCurrentQuestion, currentQuestion]);\n'''
if 'currentQuestion !== safeCurrentQuestion' not in s:
    s = s.replace(
        '  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));',
        '  const safeCurrentQuestion = Math.min(currentQuestion, Math.max(0, current.length - 1));' + reset_guard,
        1,
    )

# The live artifact proved the non-spelling question panel still rendered while current=[]
# and then evaluated current[safeCurrentQuestion].id. Guard the whole panel, tolerating
# whitespace/layout changes introduced by earlier patches.
if 'current.length > 0 && !textIsMaximized' not in s:
    patterns = [
        r'\{!textIsMaximized\s*&&\s*\(\s*<section className="question-panel">',
        r'\{\(!textIsMaximized\)\s*&&\s*\(\s*<section className="question-panel">',
    ]
    changed = False
    for pat in patterns:
        s2, count = re.subn(pat, '{current.length > 0 && !textIsMaximized && (\n              <section className="question-panel">', s, count=1)
        if count:
            s = s2
            changed = True
            break
    if not changed:
        raise SystemExit('Question panel wrapper not found; refusing to deploy a build that can still crash on empty exam content.')

p.write_text(s)
print('student runtime guard applied: empty exam content cannot render question panel')
