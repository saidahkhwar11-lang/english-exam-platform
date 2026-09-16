from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

# Word documents often place quiz questions/options/answer keys inside tables.
# Mammoth convertToHtml preserves those cells, but parsers that only split on <p>
# can miss them. Normalize Word-table HTML into line-oriented text before parsing.
# This is Exam Platform only; Assessment Tracker data/marks are untouched.

# Strengthen any Mammoth HTML-to-text conversion so table rows/cells become lines.
repls = [
    ('.replace(/<br\\s*\\/?\\s*>/gi, "\\n")', '.replace(/<br\\s*\\/?\\s*>/gi, "\\n").replace(/<\\/t[dh]>/gi, "\\n").replace(/<\\/tr>/gi, "\\n")'),
    ('.replace(/<\\/p>/gi, "\\n")', '.replace(/<\\/p>/gi, "\\n").replace(/<\\/t[dh]>/gi, "\\n").replace(/<\\/tr>/gi, "\\n")'),
]
for old,new in repls:
    if old in s and '<\\/t[dh]>' not in s:
        s = s.replace(old,new,1)

# If DOCX extraction uses mammoth.extractRawText, keep it: raw text includes table
# cell text. Normalize tabs/table separators into new lines so numbered questions,
# A-D choices, and answer-key rows are individually visible to the parser.
for anchor in [
    'const rawText = result.value;',
    'const rawText = result.value || "";',
    'const text = result.value;',
    'const text = result.value || "";',
]:
    if anchor in s:
        var = 'rawText' if 'rawText' in anchor else 'text'
        replacement = anchor + f'\n      const tableSafeText = {var}.replace(/\\t+/g, "\\n").replace(/\\u00a0/g, " ");'
        s = s.replace(anchor,replacement,1)
        # Redirect the first nearby parser call when it consumes the original variable.
        tail_start = s.find(replacement)
        tail = s[tail_start:tail_start+2500]
        for call in [f'parseExamText({var}', f'parseTeacherExam({var}', f'parseExam({var}', f'parseUploadedExam({var}']:
            if call in tail:
                newtail = tail.replace(call, call.replace(var,'tableSafeText'),1)
                s = s[:tail_start] + newtail + s[tail_start+len(tail):]
                break
        break

# General normalization used by many parser revisions: tabs must be treated as
# structural line breaks, not swallowed as spaces.
for old in [
    'text.replace(/\\r/g, "").split("\\n")',
    'rawText.replace(/\\r/g, "").split("\\n")',
]:
    if old in s:
        base = 'text' if old.startswith('text') else 'rawText'
        s = s.replace(old, f'{base}.replace(/\\t+/g, "\\n").replace(/\\r/g, "").split("\\n")', 1)

p.write_text(s, encoding='utf-8')
print('DOCX table compatibility applied: table MCQs and table answer keys are parser-visible')
