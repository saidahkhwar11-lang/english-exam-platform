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
    return source.map((q, index) => {
      // Spelling Part 1 must stay exactly the teacher's uploaded word list at every level.
      if (spellingMode && index < 10) return { ...standardSource[index], id: q.id };

      const standardQuestion = standardSource[index] || q;
      const basePrompt = String(standardQuestion.prompt || q.prompt || "").trim();
      const expected = String((standardQuestion as any).expectedText || (q as any).expectedText || "").trim();

      if (requestedLevel === "basic") {
        const shortClue = expected
          ? ` Hint: the answer starts with “${expected.charAt(0).toUpperCase()}” and has ${expected.length} letters.`
          : " Look for the clearest key word or detail before answering.";
        const prompt = spellingMode
          ? `Complete the sentence with the correct vocabulary word.${shortClue} ${basePrompt}`
          : `Basic version: Read the question carefully and focus on the clearest detail. ${basePrompt}${shortClue}`;
        return { ...q, prompt, hint: shortClue.trim() };
      }

      // Advanced keeps the same skill, answer, marks and tracker mapping, but removes
      // scaffolding and places the item in a more demanding linguistic frame.
      const prompt = spellingMode
        ? `Using the most precise vocabulary item, complete this sentence after interpreting the full context: ${basePrompt.replace(/[.!?]+$/, "")}, particularly where the meaning must be inferred rather than taken from an obvious clue.`
        : `Advanced version: Use precise evidence, careful inference and close attention to possible distractors before answering. ${basePrompt}`;
      return { ...q, prompt, hint: undefined };
    });
  };
  const current = buildLevelQuestions(level);'''

s = s.replace(anchor, replacement, 1)
p.write_text(s)
print('level differentiation applied: Standard untouched; Basic scaffolded; Advanced reframed; Spelling Part 1 preserved and Part 2 differentiated')
