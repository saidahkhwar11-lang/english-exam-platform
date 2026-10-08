"""Generate a reusable three-part exam Word template for teachers."""
from pathlib import Path
from docx import Document
from docx.shared import Pt
out=Path("public/Three-Part-English-Exam-Template.docx")
out.parent.mkdir(parents=True,exist_ok=True)
d=Document()
sec=d.sections[0]
sec.header.paragraphs[0].text="Al Reyadah School | English Department"
d.add_heading("English Reading Test 2",0)
d.add_paragraph("Term 1 - Academic year 2026-2027")
d.add_paragraph("Two bonus marks!!")
d.add_paragraph("Teacher note: The matching Assessment Tracker assessment maximum is authoritative. When the exam has more one-mark questions than the Tracker maximum, the last extra questions are bonus questions. This sample has 22 questions for a Tracker assessment out of 20; questions 21 and 22 are bonus.")
d.add_heading("Part One: Reading: Read the following article and answer questions 1 – 8:",level=1)
d.add_heading("A Visit to the Science Garden",level=2)
d.add_paragraph("On Friday, Mariam and her classmates visited a science garden. The guide showed them how plants grow in different environments. Some plants needed plenty of sunlight, while others grew best in the shade.")
d.add_paragraph("The students watched a demonstration about saving water. The guide explained that collecting rainwater can help gardens during dry months. Mariam took notes because she wanted to share the ideas with her family.")
d.add_paragraph("At the end of the visit, each group designed a small garden plan. Mariam's group chose local plants because they need less water. The teacher praised the students for working together.")
reading=[
("Where did the class go?",["A. A shopping mall","B. A science garden","C. A sports stadium","D. A library"],"B"),
("When did they visit?",["A. Monday","B. Tuesday","C. Friday","D. Sunday"],"C"),
("Who showed the students around?",["A. A guide","B. A driver","C. A chef","D. A nurse"],"A"),
("What did the demonstration teach?",["A. Making bread","B. Saving water","C. Playing sports","D. Painting walls"],"B"),
("Why did Mariam take notes?",["A. To win a prize","B. To finish homework","C. To share ideas with family","D. To write a song"],"C"),
("Which plants did Mariam's group choose?",["A. Local plants","B. Plastic plants","C. Tropical trees","D. Sea plants"],"A"),
("Why did the group choose those plants?",["A. They grow in snow","B. They are very tall","C. They smell sweet","D. They need less water"],"D"),
("What is the main idea of the text?",["A. A class learns about gardens and water","B. A family goes shopping","C. A student wins a race","D. A guide opens a restaurant"],"A")]
grammar=[
("_____ is your English teacher?",["A. Who","B. Where","C. When","D. Why"],"A"),
("She _____ to school every day.",["A. walk","B. walks","C. walking","D. walked"],"B"),
("They have lived here _____ 2020.",["A. for","B. at","C. since","D. on"],"C"),
("This is the book _____ I borrowed.",["A. who","B. where","C. when","D. that"],"D"),
("We _____ our homework yesterday.",["A. finished","B. finish","C. finishes","D. finishing"],"A"),
("I enjoy _____ stories.",["A. read","B. reading","C. reads","D. to reading"],"B"),
("There _____ many flowers in the garden.",["A. is","B. was","C. are","D. be"],"C")]
vocab=[
("The garden needs clean __________ to grow.", "water"),
("We should __________ paper instead of throwing it away.", "recycle"),
("A good __________ helps students learn.", "teacher"),
("The students visited the science __________.", "museum"),
("The room was very __________ after the lights were switched on.", "bright"),
("My sister likes to __________ stories in her notebook.", "write"),
("The group worked __________ to finish the project.", "together")]
answers=[]
for i,(q,options,key) in enumerate(reading+grammar,1):
    if i==9:d.add_heading("Part Two: Grammar: Circle the letter of the correct answer:",level=1)
    d.add_paragraph(f"{i}. {q}")
    for option in options:d.add_paragraph(option)
    answers.append((i,key))
d.add_heading("Part Three: Maze:",level=1)
d.add_paragraph("Choose the correct word from the box to fill in the gaps:")
d.add_paragraph("water - recycle - teacher - museum - bright - write - together - garden - paper")
for i,(q,ans) in enumerate(vocab,16):
    d.add_paragraph(f"{i}. {q}")
    answers.append((i,ans))
d.add_page_break()
d.add_heading("Answer key:",level=1)
for i,ans in answers:d.add_paragraph(f"{i}. {ans}")
d.add_paragraph("Teacher reminder: Replace all example content and update every answer-key entry. Keep numbered questions in order, MCQs with A–D choices, and vocabulary options separated by hyphens. Match the exam name/type to the Tracker assessment.")
d.save(out)
print("Generated",out,"with",len(answers),"questions")
