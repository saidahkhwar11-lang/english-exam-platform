from pathlib import Path

p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")

anchor='  const current = buildLevelQuestions(level);'
if anchor not in s:
    raise SystemExit("current question builder anchor missing")

replacement=r'''  const currentBase = buildLevelQuestions(level);
  const current = currentBase.map((question, index) => {
    if (index !== 10 || !examContent?.sourceText) return question;
    const lines = examContent.sourceText.replace(/\r/g, "").split("\n").map((line) => line.trim()).filter(Boolean);
    const q11 = lines.findIndex((line) => /^11[.)]\s+/.test(line));
    if (q11 < 0) return question;
    const options: string[] = [];
    for (let i=q11+1; i<lines.length && options.length<4; i++) {
      const match=lines[i].match(/^[A-D][.)]\s+(.+)$/i);
      if (!match) break;
      options.push(match[1].trim());
    }
    if (options.length !== 4) return question;
    const keyStart=lines.findIndex((line)=>/answer\s*key/i.test(line));
    let answer=question.answer;
    if(keyStart>=0){
      const keyText=lines.slice(keyStart).join(" ");
      const match=keyText.match(/(?:^|\s)11[.)]\s*([A-D])\b/i);
      if(match) answer=match[1].toUpperCase().charCodeAt(0)-65;
    }
    return {...question, skill:"Multiple Choice", options, answer, responseType:"choice" as const, expectedText:undefined};
  });'''

s=s.replace(anchor,replacement,1)
p.write_text(s,encoding="utf-8")
print("Focused Q11 MCQ runtime repair applied")
