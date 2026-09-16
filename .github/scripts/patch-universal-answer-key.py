from pathlib import Path
import re

p = Path('app/page.tsx')
s = p.read_text()

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
      const matches = Array.from(line.matchAll(/(?:^|\s)(\d+)\s*(?:[.)]|[:=\-])?\s*([A-H]|[^\d]+?)(?=\s+\d+\s*(?:[.)]|[:=\-])|$)/gi));
      for (const m of matches) if (m[2]?.trim()) answerMap[Number(m[1])] = m[2].trim();
      if (!matches.length) {
        const m = line.match(/^(\d+)\s*(?:[.)]|[:=\-])?\s*(.+)$/);
        if (m && m[2].trim()) answerMap[Number(m[1])] = m[2].trim();
      }
    }
    if (!Object.keys(answerMap).length) throw new Error('The Answer Key is empty or unreadable. Use numbered answers such as “1-B” or “1. community”.');

    const title = (body.find((line) => !/^(part\s*\d+|reading\s*passage|passage|questions?|listening\s*(text|passage|questions?)|answer\s*key)/i.test(line)) || fileName.replace(/\.[^.]+$/, '')).trim();
    const p1Index = body.findIndex((line) => /part\s*1.*listen.*spell/i.test(line));
    const p2Index = body.findIndex((line) => /part\s*2.*(vocabulary|context|fill)/i.test(line));
    if (p1Index >= 0 && p2Index > p1Index) {
      const part1: Array<{n:number;text:string}> = [];
      for (const line of body.slice(p1Index + 1, p2Index)) { const m=line.match(/^(\d+)[.)]\s*(.+)$/); if(m) part1.push({n:Number(m[1]),text:m[2].trim()}); }
      const part2: Array<{n:number,text:string}> = [];
      for (const line of body.slice(p2Index + 1)) { const m=line.match(/^(\d+)[.)]\s*(.+)$/); if(m) part2.push({n:Number(m[1]),text:m[2].trim()}); }
      if (!part1.length || !part2.length) throw new Error('Spelling test sections could not be read. Keep numbered items under Part 1 and Part 2.');
      const missing=part2.filter(q=>!answerMap[q.n]).map(q=>q.n); if(missing.length) throw new Error(`Missing Part 2 answer key for question(s): ${missing.join(', ')}`);
      const qs: Question[]=[...part1.map((item,i)=>({id:i+1,skill:'Spelling Part 1',prompt:`Word ${item.n}`,options:[],answer:0,marks:1,responseType:'short' as const,expectedText:item.text})),...part2.map((item,i)=>({id:part1.length+i+1,skill:'Spelling Part 2',prompt:item.text,options:[],answer:0,marks:1,responseType:'short' as const,expectedText:answerMap[item.n]}))];
      const standard=qs.map((q,i)=>({...q,id:i+1}));
      return {title,passages:{basic:'',standard:'',advanced:''},questions:{basic:standard,standard,advanced:standard},sourceFileName:fileName,sourceText:rawText};
    }

    const qStarts: Array<{idx:number,n:number,prompt:string}> = [];
    body.forEach((line,idx)=>{ const m=line.match(/^(\d+)[.)]\s*(.+)$/); if(m) qStarts.push({idx,n:Number(m[1]),prompt:m[2].trim()}); });
    if(!qStarts.length) throw new Error('No numbered questions were detected. Number questions as 1., 2., 3., etc.');

    const qs: Question[]=[];
    for(let qi=0;qi<qStarts.length;qi++){
      const q0=qStarts[qi]; const next=qi+1<qStarts.length?qStarts[qi+1].idx:body.length;
      const block=body.slice(q0.idx+1,next);
      // DOCX tables sometimes flatten the entire row into: Question.A. optionB. optionC. optionD. option
      // Parse choices from BOTH the question row and following rows, then remove them from the visible prompt.
      const combined=[q0.prompt,...block].join('\n');
      const firstOption=combined.search(/(?:^|\s|[.!?])A[.)]\s*/i);
      const promptText=(firstOption>=0?combined.slice(0,firstOption):q0.prompt).replace(/[\s.]+$/,'').trim();
      const optionSource=firstOption>=0?combined.slice(firstOption).replace(/^\s*[.!?]?\s*/,''):block.join('\n');
      const opts:Array<{letter:string,text:string}>=[];
      const optionRegex=/([A-H])[.)]\s*(.*?)(?=(?:[A-H])[.)]\s*|\n|$)/gi;
      for(const m of optionSource.matchAll(optionRegex)){
        const text=String(m[2]||'').trim(); if(text) opts.push({letter:m[1].toUpperCase(),text});
      }
      const key=answerMap[q0.n]; if(!key) throw new Error(`Missing answer key for question ${q0.n}.`);
      if(opts.length>=2){
        const keyTrim=key.trim(); let answerIndex=-1;
        const letterMatch=keyTrim.match(/^([A-H])(?:\b|[.)\-:])/i)||keyTrim.match(/^([A-H])$/i);
        if(letterMatch) answerIndex=opts.findIndex(o=>o.letter===letterMatch[1].toUpperCase());
        if(answerIndex<0) answerIndex=opts.findIndex(o=>normalizeAnswerValue(o.text)===normalizeAnswerValue(keyTrim.replace(/^[A-H][.)\-:]?\s*/i,'')));
        if(answerIndex<0) throw new Error(`Answer key for question ${q0.n} does not match any option.`);
        qs.push({id:qs.length+1,skill:'Multiple Choice',prompt:promptText||q0.prompt,options:opts.map(o=>o.text),answer:answerIndex,marks:1,responseType:'choice'});
      } else qs.push({id:qs.length+1,skill:'Question',prompt:q0.prompt,options:[],answer:0,marks:1,responseType:'short',expectedText:key});
    }
    const firstQuestionIndex=qStarts[0].idx;
    const preamble=body.slice(0,firstQuestionIndex).filter(line=>!/^(reading\s*test|listening\s*test|extra\s*credit|questions?|reading\s*passage|passage)$/i.test(line));
    const hasRealPassage=preamble.some(line=>/reading\s*(text|passage)|passage/i.test(line)) || preamble.join(' ').length>350;
    const passage=hasRealPassage?preamble.join('\n\n'):'';
    const standard=qs.map((q,i)=>({...q,id:i+1}));
    return {title,passages:{basic:passage,standard:passage,advanced:passage},questions:{basic:standard,standard,advanced:standard},sourceFileName:fileName,sourceText:rawText};
  };
'''
s=s[:start]+parser+s[end:]
score_pattern=re.compile(r'  const score = useMemo\(\(\) => current\.reduce\(\(sum, q, index\) => \{.*?\}, 0\), \[answers, current, isSpellingTest\]\);')
score_repl='  const score = useMemo(() => current.reduce((sum, q) => { const value = answers[q.id]; const correct = q.responseType === "short" ? (typeof value === "string" && answerMatches(value, q.expectedText || "")) : value === q.answer; return sum + (correct ? q.marks : 0); }, 0), [answers, current]);'
s,n=score_pattern.subn(score_repl,s,count=1)
if n!=1: raise SystemExit('universal score anchor not found')
s=s.replace('typeof selected === "string" && selected.trim() === (q.expectedText || "").trim()','typeof selected === "string" && answerMatches(selected, q.expectedText || "")')
s=s.replace('value.trim().toLowerCase() === expected.trim().toLowerCase()','answerMatches(value, expected)').replace('spellingCloseEnough(value, expected)','answerMatches(value, expected)')
old_split='  const spellingPart1 = isSpellingTest ? current.slice(0, 10) : [];\n  const spellingPart2 = isSpellingTest ? current.slice(10, 20) : [];'
new_split='''  const taggedSpellingPart1 = isSpellingTest ? current.filter((q) => /Spelling Part 1/i.test(q.skill || "")) : [];
  const taggedSpellingPart2 = isSpellingTest ? current.filter((q) => /Spelling Part 2/i.test(q.skill || "")) : [];
  const spellingBoundary = Math.ceil(current.length / 2);
  const spellingPart1 = !isSpellingTest ? [] : (taggedSpellingPart1.length ? taggedSpellingPart1 : current.slice(0, spellingBoundary));
  const spellingPart2 = !isSpellingTest ? [] : (taggedSpellingPart2.length ? taggedSpellingPart2 : current.slice(spellingBoundary));'''
if old_split in s: s=s.replace(old_split,new_split,1)
s=s.replace('<b>/10</b></div>\n              <p className="spelling-instruction">Listen carefully.','<b>/{spellingPart1.length}</b></div>\n              <p className="spelling-instruction">Listen carefully.',1)
s=s.replace('<b>/10</b></div>\n              <p className="spelling-instruction">Use the vocabulary','<b>/{spellingPart2.length}</b></div>\n              <p className="spelling-instruction">Use the vocabulary',1)
p.write_text(s)
print('universal parser applied: flattened Word-table A-D choices parsed from question rows as MCQ')
