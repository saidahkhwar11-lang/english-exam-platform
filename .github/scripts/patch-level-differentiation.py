from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text()

anchor = '  const current = examContent?.questions[level] || questions[level];'
if anchor not in s:
    raise SystemExit('level question list anchor not found')

replacement = r'''  const buildLevelQuestions = (requestedLevel: Level) => {
    const source = examContent?.questions[requestedLevel] || questions[requestedLevel];
    if (requestedLevel === "standard") return source;

    const spellingMode = /spelling/i.test(joinedSession?.examName || examName || "") || Boolean(
      examContent?.sourceText &&
      /Part\s*1\s*[–-]\s*Listen\s*&\s*Spell/i.test(examContent.sourceText) &&
      /Part\s*2\s*[–-]\s*Vocabulary\s*in\s*Context/i.test(examContent.sourceText)
    );

    const standardSource = examContent?.questions.standard || questions.standard;
    const simpleSpellingSentence = (word: string, fallback: string) => {
      const key = word.trim().toLowerCase();
      const simple: Record<string, string> = {
        attend: "Students _____ school every day.",
        privacy: "Keep your _____ safe online.",
        community: "Our _____ includes many people.",
        attitude: "A good _____ helps you learn.",
        challenges: "Students face _____ at school.",
        relate: "I can _____ to her story.",
        features: "The school has many useful _____.",
        survive: "People need water to _____.",
        major: "She chose her university _____ carefully.",
        variety: "The restaurant has a _____ of food.",
      };
      return simple[key] || fallback;
    };

    const advancedSpellingSentence = (word: string, fallback: string) => {
      const key = word.trim().toLowerCase();
      const advanced: Record<string, string> = {
        attend: "Students are expected to _____ all scheduled lectures throughout the semester.",
        privacy: "Users should protect their _____ when sharing personal information online.",
        community: "The university _____ brings together students from many cultures and backgrounds.",
        attitude: "Her positive _____ helped her overcome the difficulties of studying abroad.",
        challenges: "International students may face unexpected _____ while adapting to a new environment.",
        relate: "Readers often _____ to characters whose experiences reflect their own lives.",
        features: "The modern campus offers several useful _____ designed to support independent learning.",
        survive: "Some plants can _____ for long periods with very little water.",
        major: "Choosing a university _____ requires careful thought about future goals and interests.",
        variety: "The international festival offered a wide _____ of traditional dishes and activities.",
      };
      return advanced[key] || fallback;
    };

    return source.map((q, index) => {
      // Spelling Part 1 must stay exactly the teacher's uploaded word list at every level.
      if (spellingMode && index < 10) return { ...standardSource[index], id: q.id };

      const standardQuestion = standardSource[index] || q;
      const basePrompt = String(standardQuestion.prompt || q.prompt || "").trim();
      const expected = String((standardQuestion as any).expectedText || (q as any).expectedText || "").trim();

      if (requestedLevel === "basic") {
        // Basic spelling: one short simple sentence only.
        if (spellingMode) {
          return { ...q, prompt: simpleSpellingSentence(expected, basePrompt), hint: undefined };
        }
        const shortClue = expected
          ? `Hint: the answer starts with “${expected.charAt(0).toUpperCase()}”.`
          : "Look for the clearest detail.";
        return { ...q, prompt: `Basic version: ${basePrompt}`, hint: shortClue };
      }

      // Advanced spelling: keep the difficulty in the sentence itself. Do not repeat
      // instructions or explanations inside every question card.
      if (spellingMode) {
        return { ...q, prompt: advancedSpellingSentence(expected, basePrompt), hint: undefined };
      }

      const prompt = `Advanced version: Use precise evidence, careful inference and close attention to possible distractors before answering. ${basePrompt}`;
      return { ...q, prompt, hint: undefined };
    });
  };
  const current = buildLevelQuestions(level);'''

s = s.replace(anchor, replacement, 1)
p.write_text(s)
print('level differentiation applied: Basic and Advanced spelling use clean sentences; Standard untouched')
