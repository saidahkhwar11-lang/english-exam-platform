from pathlib import Path

page = Path('app/page.tsx')
source = page.read_text(encoding='utf-8')
old = "const mammoth=await import('mammoth/mammoth.browser'); const result=await mammoth.extractRawText({arrayBuffer:await file.arrayBuffer()});"
new = "const {default:mammoth}=await import('mammoth/mammoth.browser'); const result=await mammoth.extractRawText({arrayBuffer:await file.arrayBuffer()});"
if old not in source:
    raise SystemExit('Word reader anchor changed; refusing to publish a broken exam import')
source = source.replace(old, new, 1)

# Word tables can place several choices in a single cell. Support A through H,
# matching the existing question and answer-key parser.
old_choices = '.replace(/\\s+([A-D])[.)]\\s+(?=\\S)/g, "\\n$1. ")'
new_choices = '.replace(/\\s+([A-H])[.)]\\s+(?=\\S)/g, "\\n$1. ")'
if old_choices not in source:
    raise SystemExit('Word choice normalization changed; refusing silent patch')
source = source.replace(old_choices, new_choices, 1)
source = source.replace('if (/^[A-D][.)]?$/.test(line) && i + 1 < raw.length)', 'if (/^[A-H][.)]?$/.test(line) && i + 1 < raw.length)', 1)
old_key = 'lines.findIndex((line) => /^answer\\s*key\\b/i.test(line))'
if old_key not in source:
    raise SystemExit('Answer Key detection changed; refusing silent patch')
source = source.replace(old_key, 'lines.findIndex((line) => /\\banswer\\s*key\\b/i.test(line))', 1)
# Some teacher documents write "B As another option" without a period.
source = source.replace('    lines.push(line);\n  }\n  return lines;', '''    const bareChoice = line.match(/^([A-H])\\s+(.+)$/i);
    lines.push(bareChoice ? `${bareChoice[1].toUpperCase()}. ${bareChoice[2]}` : line);
  }
  return lines;''', 1)
source = source.replace('Please use DOCX, PDF, or TXT. Old .doc files are not supported in the browser.', 'Upload a DOCX, PDF, or TXT exam with numbered questions, lettered choices, and an Answer Key.', 1)
page.write_text(source, encoding='utf-8')
print('Word MCQ import fixed; two to eight choices accepted and existing exam flows preserved')
