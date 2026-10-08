from pathlib import Path
p=Path("app/page.tsx")
s=p.read_text()
def replace(a,b):
 global s
 if s.count(a)!=1: raise RuntimeError("Three-part upgrade: source anchor missing or changed: "+a[:65])
 s=s.replace(a,b)
replace('hint?: string; responseType?: "choice" | "short"; expectedText?: string','hint?: string; responseType?: "choice" | "short"; expectedText?: string; bonus?: boolean')
replace('sourceFileName: string; sourceText: string };','sourceFileName: string; sourceText: string; wordBank?: string[]; bonusLimit?: number };')
helper=r'''
  // Opt-in three-part format: leave all existing exam types and records unchanged.
  const parseThreePartTest = (rawText: string, fileName: string): ExamContent | null => {
    const lines=rawText.replace(/\r/g,'').split('\n').map(x=>x.trim()).filter(Boolean);
    const p1=lines.findIndex(x=>/^part\s*(?:one|1)\s*[:.-]?\s*reading\b/i.test(x));
    const p2=lines.findIndex(x=>/^part\s*(?:two|2)\s*[:.-]?\s*grammar\b/i.test(x));
    const p3=lines.findIndex(x=>/^part\s*(?:three|3)\s*[:.-]?\s*(?:maze|vocabulary)\b/i.test(x));
    if(p1<0||p2<=p1||p3<=p2)return null;
    const keyStart=lines.findIndex(x=>/^answer\s*key\s*[:.]?$/i.test(x));
    if(keyStart<=p3)throw new Error('Three-part exam: Answer Key is missing.');
    const key:Record<number,string>={};
    for(const line of lines.slice(keyStart+1)){const m=line.match(/^(\d+)\s*[.)\s:-]+\s*(.+)$/);if(m)key[Number(m[1])]=m[2].trim();}
    if(!Object.keys(key).length)lines.slice(keyStart+1).forEach((x,i)=>{if(x.trim())key[i+1]=x.trim();});
    const bonusLimit=/\b(?:two|2)\s+bonus\s+marks?\b/i.test(lines.slice(0,p1).join(' '))?2:0;
    const bonusStart=lines.findIndex((x,i)=>i>p3&&i<keyStart&&/^bonus\s*(?:questions?|section)\s*[:.-]?$/i.test(x));
    const vocabEnd=bonusStart>=0?bonusStart:keyStart;
    const firstQ=lines.findIndex((x,i)=>i>p1&&/^\d+[.)]\s+/.test(x));
    if(firstQ<0)throw new Error('Reading questions not found.');
    const passage=lines.slice(p1+1,firstQ).filter(x=>!/^read the following/i.test(x)).join('\n\n');
    const bankLines=lines.slice(p3+1,vocabEnd);
    const firstGap=bankLines.findIndex(x=>/^\d+[.)]\s+/.test(x));
    if(firstGap<0)throw new Error('Vocabulary gaps not found.');
    const wordBank=bankLines.slice(0,firstGap).filter(x=>!/^choose the correct|^fill in the gaps/i.test(x)).join(' ').split(/\s*[-–—;,|]\s*/).map(x=>x.trim()).filter(Boolean);
    if(wordBank.length<2)throw new Error('Vocabulary word box could not be read. Separate words with hyphens.');
    const sections=[{from:p1,to:p2,skill:'Reading Comprehension'},{from:p2,to:p3,skill:'Grammar'},{from:p3,to:vocabEnd,skill:'Vocabulary'},...(bonusStart>=0?[{from:bonusStart,to:keyStart,skill:'Bonus'}]:[])];
    const questions:Question[]=[];
    for(const section of sections){
      const source=lines.slice(section.from+1,section.to);
      const starts=source.map((x,i)=>({i,m:x.match(/^(\d+)[.)]\s*(.*)$/)})).filter(x=>x.m);
      for(let j=0;j<starts.length;j++){
        const st=starts[j],n=Number(st.m![1]);
        const block=[st.m![2],...source.slice(st.i+1,j+1<starts.length?starts[j+1].i:source.length)];
        const correct=key[n];if(!correct)throw new Error('Missing answer key for question '+n);
        const text=block.join('\n');
        if(section.skill==='Vocabulary'||(section.skill==='Bonus'&&/_{3,}|\.{3,}/.test(text)&&!/(?:^|\n|\s)A[.)]\s*/i.test(text))){
          const prompt=text.replace(/\s+/g,' ').trim();
          if(!/_{3,}|\.{3,}/.test(prompt))throw new Error('Question '+n+' needs a vocabulary gap.');
          if(section.skill==='Vocabulary'&&!wordBank.some(w=>w.toLowerCase()===correct.toLowerCase()))throw new Error('Answer '+n+' is missing from the word box.');
          questions.push({id:n,skill:section.skill,prompt,options:[],answer:0,marks:1,responseType:'short',expectedText:correct,bonus:section.skill==='Bonus'});
        }else{
          const options:Array<{letter:string;text:string}>=[];
          const firstOption=text.search(/(?:^|\n|\s)A[.)]\s*/i);
          const prompt=(firstOption>=0?text.slice(0,firstOption):block[0]).replace(/\s+/g,' ').trim();
          for(const m of text.matchAll(/(?:^|\n|\s)([A-D])[.)]\s*(.*?)(?=(?:\n|\s)[A-D][.)]\s*|$)/gis)){
            const val=m[2].replace(/\s+/g,' ').trim();if(val)options.push({letter:m[1].toUpperCase(),text:val});
          }
          // Word documents sometimes use automatic list numbering, omitted from extracted text.
          if(!options.length&&block.length>=5){const last=block.slice(-4).map(x=>x.trim());if(last.every(Boolean))last.forEach((value,i)=>options.push({letter:String.fromCharCode(65+i),text:value}));}
          if(options.length!==4)throw new Error('Question '+n+' needs four readable MCQ choices.');
          const letter=correct.match(/^([A-D])\b/i)?.[1]?.toUpperCase();
          const answer=options.findIndex(o=>o.letter===letter);
          if(answer<0)throw new Error('Answer key does not match question '+n);
          questions.push({id:n,skill:section.skill,prompt,options:options.map(o=>o.text),answer,marks:1,responseType:'choice',bonus:section.skill==='Bonus'});
        }
      }
    }
    // If the paper states its regular maximum, every additional one-mark
    // question at the end is a bonus question. Never mutate stored exams.
    // The actual regular maximum comes from the matching Assessment Tracker
    // column when a class session opens. Do not infer it from the Word file.
    questions.forEach(q=>{q.bonus=false;});
    const computedBonusLimit=0;
    if(!questions.length||questions.some((q,i)=>i>0&&q.id<=questions[i-1].id))throw new Error('Questions must be numbered in order.');
    if(!['Reading Comprehension','Grammar','Vocabulary'].every(skill=>questions.some(q=>q.skill===skill)))throw new Error('All three parts must contain questions.');
    const title=lines.slice(0,p1).find(x=>/test|assessment|exam/i.test(x))||fileName.replace(/\.[^.]+$/,'');
    const standard=questions.map(q=>({...q}));
    return {title,passages:{basic:passage,standard:passage,advanced:passage},questions:{basic:standard,standard,advanced:standard},sourceFileName:fileName,sourceText:rawText,wordBank,bonusLimit:computedBonusLimit};
  };
'''
replace('  const parseTeacherTest = (rawText: string, fileName: string): ExamContent => {',helper+'\n  const parseTeacherTest = (rawText: string, fileName: string): ExamContent => {\n    const threePart=parseThreePartTest(rawText,fileName);\n    if(threePart)return threePart;')
replace('      if (docxReading.passage) {','      if (docxReading.passage && !content.wordBank) {')
replace('  const total = current.reduce((sum, question) => sum + question.marks, 0);','  const total = current.reduce((sum, question) => sum + question.marks, 0);\n  // Bonus allocation is resolved against the per-class Tracker maximum on submission.')
replace('        const roundedScore = Math.round((Number(score) / safeTotal) * safeMax);','        const awardedBonus = Math.min(bonusEarned, Number(joinedSession.examContent?.bonusLimit || 0));\n        const roundedScore = Math.round(((Number(score)-bonusEarned) / safeTotal) * safeMax) + awardedBonus;')
replace('score: roundedScore, max: safeMax, rawScore: Number(score) || 0, rawMax: safeTotal, violations,','score: roundedScore, max: safeMax, bonusScore: awardedBonus, rawScore: Number(score) || 0, rawMax: safeTotal, violations,')
replace('{q.hint && <p className="question-hint">','{q.skill === "Vocabulary" && examContent?.wordBank?.length ? <div className="rounded-lg border border-cyan-200 bg-cyan-50 p-3 mb-3"><strong>Word Box: </strong>{examContent.wordBank.join("  ·  ")}</div> : null}{q.hint && <p className="question-hint">')
replace('placeholder="Type your answer exactly"','placeholder={q.skill === "Vocabulary" ? "Choose a word from the box" : "Type your answer exactly"}')

p.write_text(s)
print('Three-part Reading / Grammar / Vocabulary + explicit bonus marking installed')
