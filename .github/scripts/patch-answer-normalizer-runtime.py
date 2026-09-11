from pathlib import Path

p = Path('app/page.tsx')
s = p.read_text(encoding='utf-8')

old = '''  const normalizeAnswerValue = (value: string) => value
    .normalize("NFKC")
    .replace(/[\\u00A0\\u2007\\u202F]/g, " ")
    .replace(/[’‘]/g, "'")
    .replace(/[“”]/g, '\"')
    .replace(/\\s+/g, " ")
    .trim()
    .toLowerCase();

  const acceptedAnswers = (expected: string) => expected
    .split(/\\s*\\|\\s*|\\s*;\\s*|\\s+\\/\\s+/)
    .map((item) => normalizeAnswerValue(item))
    .filter(Boolean);

  const answerMatches = (value: string, expected: string) => {
    const actual = normalizeAnswerValue(value);
    return acceptedAnswers(expected).includes(actual);
  };
'''

new = '''  const normalizeAnswerValue = (value: unknown) => String(value ?? "")
    .normalize("NFKC")
    .replace(/[\\u00A0\\u2007\\u202F]/g, " ")
    .replace(/[’‘]/g, "'")
    .replace(/[“”]/g, '\"')
    .replace(/\\s+/g, " ")
    .trim()
    .toLowerCase();

  const acceptedAnswers = (expected: unknown) => String(expected ?? "")
    .split(/\\s*\\|\\s*|\\s*;\\s*|\\s+\\/\\s+/)
    .map((item) => normalizeAnswerValue(item))
    .filter(Boolean);

  const answerMatches = (value: unknown, expected: unknown) => {
    const actual = normalizeAnswerValue(value);
    if (!actual) return false;
    return acceptedAnswers(expected).includes(actual);
  };
'''

if new in s:
    print('runtime-safe answer normalization already present')
elif old in s:
    s = s.replace(old, new, 1)
    p.write_text(s, encoding='utf-8')
    print('runtime-safe answer normalization applied')
else:
    raise SystemExit('answer normalizer block not found; refusing unsafe patch')
