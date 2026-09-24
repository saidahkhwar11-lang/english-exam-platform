from pathlib import Path

page = Path('app/page.tsx')
source = page.read_text(encoding='utf-8')

# A numbered Answer Key and an ordered list of single letters are both valid.
# The latter is used by the uploaded Spelling 1 teacher copy.
anchor = '''    if (!Object.keys(answerMap).length) throw new Error('The Answer Key is empty or unreadable. Use numbered answers such as “1-B” or “1. community”.');'''
replacement = '''    if (!Object.keys(answerMap).length) {
      // Read the original Word lines here: table-cell normalization can join
      // adjacent single letters into a false option such as "B. C".
      const rawKeyLines = rawText.replace(/\\r/g, "").split("\\n");
      const rawKeyStart = rawKeyLines.findIndex((line) => /\\banswer\\s*key\\b/i.test(line));
      const orderedLetters = rawKeyLines.slice(rawKeyStart + 1).map((line) => line.trim()).filter(Boolean);
      if (orderedLetters.length && orderedLetters.every((line) => /^[A-H][.)]?$/i.test(line))) {
        orderedLetters.forEach((letter, index) => { answerMap[index + 1] = letter.charAt(0).toUpperCase(); });
      }
    }
    if (!Object.keys(answerMap).length) throw new Error('The Answer Key is empty or unreadable. Use numbered answers (1. B) or list one answer letter per line.');'''
if source.count(anchor) != 1:
    raise SystemExit('Answer Key parser changed; no changes applied')
source = source.replace(anchor, replacement, 1)

# A question-only file may begin immediately with question 1. Use its filename
# as the exam title instead of showing the first question as the title.
old = '''const title = (body.find((line) => !/^(part\\s*\\d+|reading\\s*passage|passage|questions?|listening\\s*(text|passage|questions?)|answer\\s*key)/i.test(line)) || fileName.replace(/\\.[^.]+$/, '')).trim();'''
new = '''const title = (body.find((line) => !/^(part\\s*\\d+|reading\\s*passage|passage|questions?|listening\\s*(text|passage|questions?)|answer\\s*key)/i.test(line) && !/^\\d+[.)]\\s+/.test(line) && !/^[A-H][.)]\\s+/.test(line)) || fileName.replace(/\\.[^.]+$/, '')).trim();'''
if source.count(old) != 1:
    raise SystemExit('Exam title parser changed; no changes applied')
source = source.replace(old, new, 1)

page.write_text(source, encoding='utf-8')
print('Numbered and one-letter-per-line answer keys accepted; question-only titles use filenames')
