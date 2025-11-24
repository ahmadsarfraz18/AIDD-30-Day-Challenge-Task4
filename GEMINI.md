Gemini CLI Project Prompt: PDF Summarizer & Quiz Generator Agent
Project Objective

Build a fully functional agent capable of summarizing PDFs and generating quizzes, leveraging the required technologies and workflow structure.

Agent Identity

Core Agent Name: PDF_Study_Agent

Initial Setup & Context Retention (IMPORTANT REQUIREMENT) Documentation Setup
Immediately create or overwrite a file named GEMINI.md in the project’s root directory.

Context Injection

Insert the entire contents of this prompt (starting from the “Project Objective” section and ending at the “Final Instruction”) into the GEMINI.md file. This ensures the agent and LLM always retain the project’s operational context and guidelines. 2. Tech Stack & Environment Configuration Model & Execution

Use Gemini CLI, ideally with a strong model such as gemini-2.5-pro or an equivalent model variant.

MCP Integration

Use Context7 as the required MCP server environment for tool execution.

Agent Logic

Implement the agent using the OpenAI Agents SDK (Python) for defining actions, tool usage, and reasoning steps.

Frontend

Develop the user interface in Streamlit, providing an interactive and clean experience for uploading PDFs, generating summaries, and taking quizzes.

PDF Text Extraction

Use PyPDF (pypdf) to extract clean text from PDF uploads with full support for multi-page parsing. 3. Agent Feature (A) — PDF Summarization User Input

Allow the user to upload one PDF file using the Streamlit file uploader.

Extraction Process

Implement a tool using PyPDF to pull all textual content from the uploaded PDF.

Properly handle multi-page PDFs and common extraction issues.

LLM Processing

Send the raw extracted text to the Gemini model and instruct it to produce:

A clear

Concise

Well-structured summary covering all main ideas and relevant details.

Frontend Output

Display the generated summary in the Streamlit UI using any preferred layout style such as cards, blocks, containers, or expanders. 4. Agent Feature (B) — Quiz Generation Trigger Condition

Enable a button named "Create Quiz" only after the summary has been successfully generated.

Source Material

The quiz must be generated exclusively from the original extracted PDF text, not from the summary.

Question Generation Rules Multiple Choice

Produce at least 10 MCQs.

Each question must contain exactly 4 answer choices (A, B, C, D).

The correct answer must be stored internally (hidden from user view).

Mixed Questions

Generate additional question types (e.g., True/False, Fill-in-the-Blank) to reach a total of 15–20 questions.

Frontend Quiz Display

Show all quiz questions clearly in Streamlit.

Allow users to select or enter their answers.

Include a "Check Answers" button for final evaluation. 5. Technical Requirements & Best Practices

All agent functionality must follow OpenAI Agents SDK standards and Python best practices.

Include a full dependency list (e.g., requirements.txt).

Implement strong input validation and error handling (e.g., invalid file types, failed text extraction).

Ensure the entire app can be executed through a simple command: streamlit run app.py

Final Instruction

Generate the complete, self-contained Python code for the entire PDF_Study_Agent project, including:

Streamlit frontend (app.py)

OpenAI Agents SDK agent implementation

PyPDF extraction logic

The fully populated GEMINI.md file

Only the phrasing has been changed — all project instructions, meaning, and structure remain identical.