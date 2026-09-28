from pathlib import Path
import zipfile, html
from datetime import datetime

out=Path("public/Multi-Text-Reading-Exam-Template.docx")
out.parent.mkdir(parents=True,exist_ok=True)
paras=[
("MULTI-TEXT READING EXAM TEMPLATE","title"),
("Use this format when one Reading exam contains two or more separate texts.","italic"),
("IMPORTANT FORMAT RULES","head"),
("• Start every passage with the exact heading: Text 1, Text 2, Text 3 …","normal"),
("• Put the passage directly under its Text heading and keep paragraph breaks.","normal"),
("• Put only that text’s questions after its passage. Continue question numbering across the whole exam.","normal"),
("• MCQs may use A–C or A–D choices. Keep one Answer Key at the end.","normal"),
]
for n,start,end in [(1,1,3),(2,4,6),(3,7,9)]:
    paras += [(f"Text {n}","head"),(f"[Title of Text {n}]","bold"),
              (f"[Paragraph 1 of Text {n}. Paste the reading passage here.]","normal"),
              (f"[Paragraph 2 of Text {n}. Keep each paragraph separate.]","normal"),
              (f"Questions {start}–{end}","bold")]
    for q in range(start,end+1):
        paras.append((f"{q}. [Question related to Text {n}]","bold"))
        for L in "ABCD": paras.append((f"{L}. [Option {L}]","normal"))
paras += [("ANSWER KEY","head"),("1. B   2. C   3. A   4. D   5. B   6. C   7. A   8. D   9. B","normal"),
          ("Teacher note: You may use any number of texts and questions. Example: Text 1 = Questions 1–10, Text 2 = Questions 11–20, Text 3 = Questions 21–30.","normal")]

def pxml(text,kind):
    text=html.escape(text)
    props=""
    rprops=""
    if kind=="title": props='<w:jc w:val="center"/>'; rprops='<w:b/><w:sz w:val="34"/>'
    elif kind=="head": rprops='<w:b/><w:sz w:val="28"/>'
    elif kind=="bold": rprops='<w:b/>'
    elif kind=="italic": rprops='<w:i/>'
    return f'<w:p><w:pPr>{props}<w:spacing w:after="120"/></w:pPr><w:r><w:rPr>{rprops}<w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="21"/></w:rPr><w:t xml:space="preserve">{text}</w:t></w:r></w:p>'

body="".join(pxml(t,k) for t,k in paras)
document=f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{body}<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720"/></w:sectPr></w:body></w:document>'''
content_types='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'''
rels='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml",content_types)
    z.writestr("_rels/.rels",rels)
    z.writestr("word/document.xml",document)
print("Generated",out)
