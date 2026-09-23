from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()
old = 'const spellingMode = /spelling/i.test(joinedSession?.examName || examName || "") || Boolean('
if old not in s:
    raise SystemExit('Spelling level mode anchor missing')
s = s.replace(old, 'const spellingMode = Boolean(examContent?.questions.standard.some((q) => /Spelling Part [12]/i.test(q.skill || ""))) || Boolean(', 1)
old = 'if (spellingMode && index < 10 && standardSource[index])'
s = s.replace(old, 'if (spellingMode && /Spelling Part 1/i.test(standardSource[index]?.skill || "") && standardSource[index])', 1)
old = 'const isSpellingTest = /spelling/i.test(joinedSession?.examName || examName || "") || Boolean(examContent?.sourceText && /Part\\s*1\\s*[–-]\\s*Listen\\s*&\\s*Spell/i.test(examContent.sourceText) && /Part\\s*2\\s*[–-]\\s*Vocabulary\\s*in\\s*Context/i.test(examContent.sourceText));'
new = 'const isSpellingTest = current.length > 0 && current.every((q) => q.responseType === "short" && /Spelling Part [12]/i.test(q.skill || ""));'
if old not in s:
    raise SystemExit('Spelling layout anchor missing')
s = s.replace(old, new, 1)
p.write_text(s)
print('Spelling layout now depends on typed spelling questions; spelling MCQs use normal choice UI')
