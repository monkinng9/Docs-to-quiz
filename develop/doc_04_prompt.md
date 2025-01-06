## Instruction
Please extract:
1. Key concepts and main ideas
2. Supporting details and examples
3. Technical terms and definitions
4. Important relationships and connections between concepts
5. Any numerical data or specific facts
Organize the information by sections as they appear in the document.

## Expected Output
A dictionary containing extracted information with the following structure:
{
  'main_concepts': [list of key concepts],
  'supporting_details': {concept: [related details]},
  'technical_terms': {term: definition},
  'relationships': [list of concept relationships],
  'facts': [list of important facts and data]
}

---
## Instruction
Create a comprehensive summary of the document based on the extracted information.
The summary should include:
1. A high-level overview (2-3 paragraphs)
2. Key takeaways (bullet points)
3. Detailed section-by-section breakdown
Format the summary for clarity and readability.
Output should be in markdown format starting with '# Summary' heading.

## Expected Output
A markdown formatted summary starting with '# Summary' heading, containing overview,
key takeaways, and detailed section breakdowns. Do not include markdown code blocks.

---
## Instruction
Create a comprehensive study guide that helps readers master the content.
Include:
1. Learning objectives for each major section
2. Key concepts with explanations
3. Important terms and definitions
4. Example scenarios or applications
5. Review notes and tips
Format the study guide in markdown format starting with '# Study Guide' heading.

## Expected Output
A markdown formatted study guide starting with '# Study Guide' heading, with clear sections for objectives, 
concepts, terms, examples, notes, and review questions. Do not include markdown code blocks.

---
## Instruction
Create an assessment quiz to test understanding of the material.
Include a mix of question types following these specifications:
Determine appropriate number of questions for each type based on the content complexity 
and importance of different topics. Aim for a comprehensive assessment that can be 
completed in 30-45 minutes.

Question types:
1. Multiple choice questions
2. True/False statements
3. Short answer questions
4. Scenario-based questions
Focus on:
- Covering key concepts from the document
- Testing deep understanding, not just recall
- Varying difficulty levels
Format the quiz in markdown starting with '# Quiz Questions' heading.
Do NOT include answer explanations in this task.

## Expected Output
A markdown formatted quiz starting with '# Quiz Questions' heading, containing:
- Clear, concise questions
- Placeholders for answers
- Sections for multiple choice, true/false, short answer, and scenario questions
Questions should be numbered and clearly formatted and do not include markdown code blocks

---
## Instruction
Create comprehensive answer keys and explanations for the previously generated quiz.
For each question type:
1. Provide correct answers
2. Write detailed explanations
3. Reference specific parts of the source document
4. Explain why other options are incorrect (for multiple choice)
5. Provide additional context or learning insights
Ensure answers are:
- Thorough and educational
- Directly linked to the source material
- Helpful for understanding, not just grading
Format the answers in markdown starting with '# Quiz Answers' heading.

## Expected Output
A markdown formatted answer key starting with '# Quiz Answers' heading, containing:
- Correct answers for each question
- Detailed explanations
- References to source material
- Additional learning insights
Answers should be clearly linked to the corresponding quiz questions.
Do not include markdown code blocks.