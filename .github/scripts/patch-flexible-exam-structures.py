from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

# Flexible exam structures: passage/text is optional; MCQ and True/False may be
# used alone or mixed; spelling may contain Part 1, Part 2, or both.
# This patch only changes Exam Platform parsing/validation. It never writes to
# Assessment Tracker data or marks.

# A missing passage must never invalidate an otherwise valid question-only exam.
for old in [
    'if (!passage.trim()) throw new Error("No reading passage was found in the uploaded exam.");',
    'if (!passage.trim()) throw new Error("No passage was found in the uploaded exam.");',
    'if (!passage) throw new Error("No reading passage was found in the uploaded exam.");',
]:
    s = s.replace(old, '')

# Do not require a specific question family when valid auto-marked questions exist.
for old in [
    'if (!mcqQuestions.length) throw new Error("No multiple choice questions were found.");',
    'if (mcqQuestions.length === 0) throw new Error("No multiple choice questions were found.");',
    'if (!questions.length) throw new Error("No multiple choice questions were found.");',
]:
    s = s.replace(old, 'if (!questions.length) throw new Error("No supported questions were found. Add MCQ, True/False, or spelling questions.");')

# Recognize common True/False option styles as a two-choice auto-marked question.
# Insert this normalization before parsed questions are returned, when the processor
# exposes a question options array.
anchor = 'const normalizeLines = (text: string) =>'
if anchor in s and 'const normalizeTrueFalseOptions =' not in s:
    helper = '''const normalizeTrueFalseOptions = (options: string[]) => {\n  const cleaned = (options || []).map((x) => String(x || "").trim()).filter(Boolean);\n  if (cleaned.length === 2) {\n    const vals = cleaned.map((x) => x.toLowerCase().replace(/[.():-]/g, "").trim());\n    const tf = vals.every((x) => ["true","false","t","f"].includes(x));\n    if (tf) return ["True", "False"];\n  }\n  return cleaned;\n};\n\n'''
    s = s.replace(anchor, helper + anchor, 1)

# Permit empty passage values throughout generated ExamContent. Question-only exams
# deliberately use an empty string instead of sample/old passage content.
s = s.replace('passage: passage || samplePassage', 'passage: passage || ""')
s = s.replace('passage: passage || passages.standard', 'passage: passage || ""')
s = s.replace('passage: passage.trim() || passages.standard', 'passage: passage.trim() || ""')

# Spelling sections are independent. Remove validation that insists both parts exist.
for old in [
    'if (!part1.length || !part2.length) throw new Error("Spelling test must include Part 1 and Part 2.");',
    'if (part1.length === 0 || part2.length === 0) throw new Error("Spelling test must include Part 1 and Part 2.");',
    'if (!spellingPart1.length || !spellingPart2.length) throw new Error("Spelling test must include Part 1 and Part 2.");',
]:
    s = s.replace(old, 'if (!part1.length && !part2.length) throw new Error("No spelling questions were found.");' if 'part1' in old and 'spellingPart1' not in old else 'if (!spellingPart1.length && !spellingPart2.length) throw new Error("No spelling questions were found.");')

p.write_text(s, encoding='utf-8')
print('Flexible exam structures enabled: MCQ/T-F with optional text; spelling Part 1/Part 2 independently supported')
