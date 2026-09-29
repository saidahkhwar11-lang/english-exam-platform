from pathlib import Path

p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")

anchor='  const current = examContent?.questions[level] || questions[level];'
if anchor not in s:
    raise SystemExit("current questions anchor missing")

replacement=r'''  const currentBase = examContent?.questions[level] || questions[level];
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
    if (options.length < 2) return question;
    const keyStart=lines.findIndex((line)=>/answer\s*key/i.test(line));
    let letter="A";
    if(keyStart>=0){
      const keyText=lines.slice(keyStart).join(" ");
      const match=keyText.match(/(?:^|\s)11[.)]\s*([A-D])\b/i);
      if(match) letter=match[1].toUpperCase();
    }
    return {...question, skill:"Multiple Choice", options, answer:Math.max(0,letter.charCodeAt(0)-65)};
  });'''

s=s.replace(anchor,replacement,1)
p.write_text(s,encoding="utf-8")
print("Q11 runtime MCQ repair applied")
