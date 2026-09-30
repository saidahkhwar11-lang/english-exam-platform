from pathlib import Path

p=Path("app/page.tsx")
s=p.read_text(encoding="utf-8")

anchor='  const current = currentBase.map((question, index) => {'
if anchor not in s:
    raise SystemExit("current mapped question list anchor missing")

# Insert a source-exact option recovery helper before current mapping.
helper=r'''  const sourceExactOptions = (questionNumber: number) => {
    if (!examContent?.sourceText) return null;
    const lines=examContent.sourceText.replace(/\r/g,"").replace(/\t+/g,"\n").split("\n").map((line)=>line.trim()).filter(Boolean);
    const start=lines.findIndex((line)=>new RegExp("^"+questionNumber+"[.)]\\s+").test(line));
    if(start<0) return null;
    const found:string[]=[];
    for(let i=start+1;i<lines.length;i++){
      if(/^\d+[.)]\s+/.test(lines[i]) || /^(?:reading\s+)?(?:text|passage)\s*\d+\b/i.test(lines[i]) || /answer\s*key/i.test(lines[i])) break;
      const m=lines[i].match(/^[A-H][.)]\s+(.+)$/i);
      if(m) found.push(m[1].trim());
    }
    return found.length>=2 ? found : null;
  };
'''
if 'const sourceExactOptions =' not in s:
    s=s.replace(anchor,helper+anchor,1)

# For every choice question, prefer the complete wording from sourceText.
old='''  const current = currentBase.map((question, index) => {
    if (index !== 10 || !examContent?.sourceText) return question;'''
new='''  const current = currentBase.map((question, index) => {
    const exactOptions=sourceExactOptions(index+1);
    if (exactOptions && question.responseType !== "short") question={...question,options:exactOptions};
    if (index !== 10 || !examContent?.sourceText) return question;'''
if old in s:
    s=s.replace(old,new,1)

p.write_text(s,encoding="utf-8")
print("MCQ option wording now restored from complete uploaded source text")
