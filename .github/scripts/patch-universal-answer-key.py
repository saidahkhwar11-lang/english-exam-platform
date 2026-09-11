from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text()

# Replace the teacher-test parser with a universal parser that supports mixed
# MCQ + fill-in-the-gap/short-answer questions as long as a clear Answer Key exists.
start = s.find('  const parseTeacherTest = ')
end = s.find('  const processTeacherFile = ', start)
if start == -1 or end == -1:
    raise SystemExit('parseTeacherTest block not found')

parser = r'''  const normalizeAnswerValue = (value: string) => value
    .normalize("NFKC")
    .replace(/[\u00A0\u2007\u202F]/g, " ")
    .replace(/[’‘]/g, "'")
    .replace(/[“”]/g, '"')
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();

  const acceptedAnswers = (expected: string) => expected
    .split(/\s*\|\s*|\s*;\s*|\s+\/\s+/)
    .map((item) => normalizeAnswerValue(item))
    .filter(Boolean);

  const answerMatches = (value: string, expected: string) => {
    const actual = normalizeAnswerValue(value);
    return acceptedAnswers(expected).includes(actual);
  };

  const parseTeacherTest = (rawText: string, fileName: string): ExamContent => {
    const lines = normalizeLines(rawText);
    const keyIndex = lines.findIndex((line) => /^answer\s*key\b/i.test(line));
    if (keyIndex < 0) throw new Error('Answer Key not found. Add a clear “Answer Key” section so the platform can mark safely.');

    const body = lines.slice(0, keyIndex);
    const keyLines = lines.slice(keyIndex + 1);
    const answerMap: Record<number, string> = {};
    for (const line of keyLines) {
      const m = line.match(/^(\d+)[.)]\s*(?:[:=\-]\s*)?(.+)$/);
      if (m) answerMap[Number(m[1])] = m[2].trim();
    }
    if (!Object.keys(answerMap).length) throw new Error('The Answer Key is empty or unreadable. Use numbered answers such as “1. B” or “1. community”.');

    const title = (body.find((line) => !/^(part\s*\d+|reading\s*passage|passage|questions?|listening\s*(text|passage|questions?)|answer\s*key)/i.test(line)) || fileName.replace(/\.[^.]+$/, '')).trim();

    // Dedicated spelling format: Part 1 words are their own keys; Part 2 uses Answer Key – Part 2.
    const p1Index = body.findIndex((line) => /part\s*1.*listen.*spell/i.test(line));
    const p2Index = body.findIndex((line) => /part\s*2.*(vocabulary|context|fill)/i.test(line));
    if (p1Index >= 0 && p2Index > p1Index) {
      const part1: Array<{n:number;text:string}> = [];
      for (const line of body.slice(p1Index + 1, p2Index)) {
        const m = line.match(/^(\d+)[.)]\s*(.+)$/);
        if (m) part1.push({n:Number(m[1]), text:m[2].trim()});
      }
      const part2: Array<{n:number,text:string}> = [];
      for (const line of body.slice(p2Index + 1)) {
        const m = line.match(/^(\d+)[.)]\s*(.+)$/);
        if (m) part2.push({n:Number(m[1]), text:m[2].trim()});
      }
      if (!part1.length || !part2.length) throw new Error('Spelling test sections could not be read. Keep numbered items under Part 1 and Part 2.');
      const missing = part2.filter((q) => !answerMap[q.n]).map((q) => q.n);
      if (missing.length) throw new Error(`Missing Part 2 answer key for question(s): ${missing.join(', ')}`);
      const qs: Question[] = [
        ...part1.map((item, i) => ({id:i+1, skill:'Spelling Part 1', prompt:`Word ${item.n}`, options:[], answer:0, marks:1, responseType:'short' as const, expectedText:item.text})),
        ...part2.map((item, i) => ({id:part1.length+i+1, skill:'Spelling Part 2', prompt:item.text, options:[], answer:0, marks:1, responseType:'short' as const, expectedText:answerMap[item.n]})),
      ];
      const standard = qs.map((q, i) => ({...q, id:i+1}));
      return {title, passages:{basic:'',standard:'',advanced:''}, questions:{basic:standard,standard,advanced:standard}, sourceFileName:fileName, sourceText:rawText};
    }

    // General parser for Reading, Listening, Extra Credit, and other tests.
    // Each numbered question may be MCQ (A/B/C/D etc.) or a short/fill-in answer.
    const qStarts: Array<{idx:number,n:number,prompt:string}> = [];
    body.forEach((line, idx) => {
      const m = line.match(/^(\d+)[.)]\s*(.+)$/);
      if (m) qStarts.push({idx, n:Number(m[1]), prompt:m[2].trim()});
    });
    if (!qStarts.length) throw new Error('No numbered questions were detected. Number questions as 1., 2., 3., etc.');

    const qs: Question[] = [];
    for (let qi=0; qi<qStarts.length; qi++) {
      const q0 = qStarts[qi];
      const next = qi + 1 < qStarts.length ? qStarts[qi+1].idx : body.length;
      const block = body.slice(q0.idx + 1, next);
      const opts: Array<{letter:string,text:string}> = [];
      for (const line of block) {
        const om = line.match(/^([A-H])[.)]\s*(.+)$/i);
        if (om) opts.push({letter:om[1].toUpperCase(), text:om[2].trim()});
      }
      const key = answerMap[q0.n];
      if (!key) throw new Error(`Missing answer key for question ${q0.n}.`);

      if (opts.length >= 2) {
        const keyTrim = key.trim();
        let answerIndex = -1;
        const letterMatch = keyTrim.match(/^([A-H])(?:\b|[.)\-:])/i) || keyTrim.match(/^([A-H])$/i);
        if (letterMatch) answerIndex = opts.findIndex((o) => o.letter === letterMatch[1].toUpperCase());
        if (answerIndex < 0) answerIndex = opts.findIndex((o) => normalizeAnswerValue(o.text) === normalizeAnswerValue(keyTrim.replace(/^[A-H][.)\-:]?\s*/i, '')));
        if (answerIndex < 0) throw new Error(`Answer key for question ${q0.n} does not match any option.`);
        qs.push({id:qs.length+1, skill:'Question', prompt:q0.prompt, options:opts.map((o)=>o.text), answer:answerIndex, marks:1, responseType:'choice'});
      } else {
        qs.push({id:qs.length+1, skill:'Question', prompt:q0.prompt, options:[], answer:0, marks:1, responseType:'short', expectedText:key});
      }
    }

    const firstQuestionIndex = qStarts[0].idx;
    const passage = body.slice(0, firstQuestionIndex)
      .filter((line) => !/^(reading\s*test|listening\s*test|extra\s*credit|questions?|reading\s*passage|passage)$/i.test(line))
      .join('\n\n');
    const standard = qs.map((q, i) => ({...q, id:i+1}));
    return {title, passages:{basic:passage,standard:passage,advanced:passage}, questions:{basic:standard,standard,advanced:standard}, sourceFileName:fileName, sourceText:rawText};
  };
'''

s = s[:start] + parser + s[end:]

# Make all short-answer marking use the same safe normalizer. This ignores
# accidental leading/trailing spaces, Enter/new lines, repeated spaces, and case.
score_pattern = re.compile(r'  const score = useMemo\(\(\) => current\.reduce\(\(sum, q, index\) => \{.*?\}, 0\), \[answers, current, isSpellingTest\]\);')
score_repl = '  const score = useMemo(() => current.reduce((sum, q) => { const value = answers[q.id]; const correct = q.responseType === "short" ? (typeof value === "string" && answerMatches(value, q.expectedText || "")) : value === q.answer; return sum + (correct ? q.marks : 0); }, 0), [answers, current]);'
s, n = score_pattern.subn(score_repl, s, count=1)
if n != 1:
    raise SystemExit('universal score anchor not found')

s = s.replace('typeof selected === "string" && selected.trim() === (q.expectedText || "").trim()', 'typeof selected === "string" && answerMatches(selected, q.expectedText || "")')
s = s.replace('value.trim().toLowerCase() === expected.trim().toLowerCase()', 'answerMatches(value, expected)')
s = s.replace('spellingCloseEnough(value, expected)', 'answerMatches(value, expected)')

# Remove the fixed 10+10 assumption. Prefer parser tags; fall back to half/half
# for older already-saved spelling exams.
old_split = '  const spellingPart1 = isSpellingTest ? current.slice(0, 10) : [];\n  const spellingPart2 = isSpellingTest ? current.slice(10, 20) : [];'
new_split = '''  const taggedSpellingPart1 = isSpellingTest ? current.filter((q) => /Spelling Part 1/i.test(q.skill || "")) : [];
  const taggedSpellingPart2 = isSpellingTest ? current.filter((q) => /Spelling Part 2/i.test(q.skill || "")) : [];
  const spellingBoundary = Math.ceil(current.length / 2);
  const spellingPart1 = !isSpellingTest ? [] : (taggedSpellingPart1.length ? taggedSpellingPart1 : current.slice(0, spellingBoundary));
  const spellingPart2 = !isSpellingTest ? [] : (taggedSpellingPart2.length ? taggedSpellingPart2 : current.slice(spellingBoundary));'''
if old_split in s:
    s = s.replace(old_split, new_split, 1)

s = s.replace('<b>/10</b></div>\n              <p className="spelling-instruction">Listen carefully.', '<b>/{spellingPart1.length}</b></div>\n              <p className="spelling-instruction">Listen carefully.', 1)
s = s.replace('<b>/10</b></div>\n              <p className="spelling-instruction">Use the vocabulary', '<b>/{spellingPart2.length}</b></div>\n              <p className="spelling-instruction">Use the vocabulary', 1)

p.write_text(s)
print('universal answer-key parser and safe marking applied')
