from pathlib import Path

page = Path('app/page.tsx')
source = page.read_text(encoding='utf-8')

# Basic keeps the correct answer and removes only one wrong MCQ choice.
# Existing Basic variants that already have one fewer choice stay unchanged.
anchor = '  const buildLevelQuestions = (requestedLevel: Level) => {'
helper = '''  const basicChoiceSupport = (question: Question, standardQuestion: Question): Question => {
    const originalCount = standardQuestion.options?.length || 0;
    const options = question.options || [];
    if (originalCount < 3 || options.length < 3 || question.responseType === "short") return question;
    const targetCount = Math.max(2, originalCount - 1);
    if (options.length <= targetCount) return question;
    const reduced = [...options];
    let answer = question.answer;
    while (reduced.length > targetCount) {
      let wrong = reduced.length - 1;
      if (wrong === answer) wrong--;
      if (wrong < 0) break;
      reduced.splice(wrong, 1);
      if (wrong < answer) answer--;
    }
    return { ...question, options: reduced, answer };
  };
'''
if source.count(anchor) != 1:
    raise SystemExit('Basic question builder not found; no changes applied')
source = source.replace(anchor, helper + anchor, 1)

spelling = 'return { ...q, prompt: simpleSpellingSentence(expected, basePrompt), hint: undefined };'
regular = 'return { ...q, prompt: `Basic version: ${basePrompt}`, hint: shortClue };'
if source.count(spelling) != 1 or source.count(regular) != 1:
    raise SystemExit('Basic level return paths changed; no changes applied')
source = source.replace(spelling, 'return { ...basicChoiceSupport(q, standardQuestion), prompt: simpleSpellingSentence(expected, basePrompt), hint: undefined };', 1)
source = source.replace(regular, 'return { ...basicChoiceSupport(q, standardQuestion), prompt: `Basic version: ${basePrompt}`, hint: shortClue };', 1)

# Keep teachers informed that a reading passage is optional for choice exams.
source = source.replace('Simplified language · 3 choices · hints', 'One fewer MCQ choice · hints')
source = source.replace('Processed ${content.questions.standard.length} questions. Standard is ready; Basic and Advanced are linked to this exam.', 'Processed ${content.questions.standard.length} questions. Basic shows one fewer incorrect choice per MCQ; Standard keeps the teacher’s original choices.')
page.write_text(source, encoding='utf-8')
print('Basic MCQs show one fewer incorrect choice; passage-free exams remain supported')
