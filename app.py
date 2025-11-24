
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import pypdf
import json

# --- Configuration ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# --- Helper Functions ---
def safe_json_loads(s):
    """Safely loads a JSON string, stripping backticks and handling errors."""
    try:
        # Remove markdown code block fences and any leading/trailing whitespace
        s = s.strip()
        if s.startswith("```json"):
            s = s[len("```json"):
].strip()
        if s.endswith("```"):
            s = s[:-len("```")].strip()
        
        return json.loads(s)
    except json.JSONDecodeError as e:
        st.error(f"Failed to decode the quiz data from the model. The format was invalid. Error: {e}")
        st.error(f"Attempted to parse: `{s}`")
        return None

def extract_text_from_pdf(pdf_file) -> str | None:
    """Extracts text from an uploaded PDF file."""
    if pdf_file is None:
        return None
    try:
        pdf_reader = pypdf.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except pypdf.errors.PdfReadError as e:
        st.error(f"Could not read the PDF file. It might be corrupted or encrypted. Error: {e}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while reading the PDF: {e}")
        return None

# --- Main Application Logic ---
st.set_page_config(page_title="PDF Study Agent", page_icon="📚", layout="wide")

st.title("📚 PDF Study Agent")
st.markdown("Your smart assistant to summarize PDFs and generate quizzes.")

# --- API Key Configuration ---
if not API_KEY or API_KEY == "YOUR_API_KEY":
    st.warning("Please enter your Google AI API key in the `.env` file to continue.")
    st.markdown("You can get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).")
    st.stop()

try:
    genai.configure(api_key=API_KEY)

    # Dynamically select an available model that supports generateContent
    selected_model_name = None
    all_models = list(genai.list_models())

    # Preference order for models
    preferred_model_names = ["gemini-1.5-pro-latest", "gemini-pro"] # Added 1.5 Pro as preferred if available

    for preferred_name in preferred_model_names:
        for m in all_models:
            if preferred_name in m.name and "generateContent" in m.supported_generation_methods:
                selected_model_name = m.name
                break
        if selected_model_name:
            break
            
    if not selected_model_name:
        st.error("No suitable Gemini model found that supports 'generateContent'. Please check your API key and region. Available models might not support this feature.")
        st.stop()

    model = genai.GenerativeModel(selected_model_name)
    st.success(f"Using Gemini model: **{selected_model_name}**") # Inform user which model is being used

except Exception as e:
    st.error(f"Failed to configure or access Gemini AI. Please check your API key and internet connection. Error: {e}")
    st.stop()

# --- Session State Initialization ---
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = None
if "summary" not in st.session_state:
    st.session_state.summary = None
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

# --- UI: File Upload and Processing ---
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    if st.button("Generate Summary"):
        with st.spinner("Analyzing PDF and generating summary..."):
            # Reset states
            st.session_state.pdf_text = None
            st.session_state.summary = None
            st.session_state.quiz_data = None
            st.session_state.user_answers = {}
            st.session_state.quiz_submitted = False
            
            # Process PDF
            pdf_text = extract_text_from_pdf(uploaded_file)
            if pdf_text:
                if len(pdf_text) < 100: # Simple check for very short or effectively empty PDFs
                    st.warning("The extracted text is very short. Please ensure it's a valid PDF with substantial text.")
                    st.session_state.pdf_text = None # Do not process
                else:
                    st.session_state.pdf_text = pdf_text
                    
                    # Generate Summary
                    summary_prompt = f"Provide a clear, concise, and well-structured summary of the following text. Cover all main ideas and relevant details:\n\n{pdf_text}"
                    try:
                        response = model.generate_content(summary_prompt)
                        if response.text:
                            st.session_state.summary = response.text
                        else:
                            st.error("The Gemini model returned an empty summary. Please try again or with a different PDF.")
                    except genai.types.BlockedPromptException as e:
                        st.error(f"Summary generation blocked by safety filters. Please try again with different content or adjust your prompt. Details: {e}")
                    except Exception as e:
                        st.error(f"Failed to generate summary due to an API error: {e}")
            else:
                st.session_state.pdf_text = None # Ensure it's None if extraction failed

# --- UI: Display Summary and Quiz Button ---
if st.session_state.summary:
    st.subheader("📄 Summary")
    with st.expander("Click to view the summary", expanded=True):
        st.markdown(st.session_state.summary)
    
    # Ensure PDF text is available for quiz generation
    if st.session_state.pdf_text:
        if st.button("Create Quiz"):
            with st.spinner("Generating your quiz... This may take a moment."):
                quiz_prompt = f"""
                Based on the following text, generate a quiz.

                **Instructions:**
                1.  Create exactly 10 multiple-choice questions (MCQs).
                2.  Each MCQ must have exactly 4 answer choices (A, B, C, D).
                3.  Create 5 additional questions of mixed types (True/False or Fill-in-the-Blank).
                4.  The total number of questions should be 15.
                5.  Store the correct answer for each question.
                6.  Output the entire quiz as a single, valid JSON object. Do not include any text or formatting outside of the JSON.

                **JSON Format:**
                ```json
                {{
                  "quiz": [
                    {{
                      "question_number": 1,
                      "type": "multiple_choice",
                      "question": "What is the capital of France?",
                      "options": {{"A": "Berlin", "B": "Madrid", "C": "Paris", "D": "Rome"}},
                      "answer": "C"
                    }},
                    {{
                      "question_number": 11,
                      "type": "true_false",
                      "question": "The sky is blue.",
                      "answer": "True"
                    }},
                    {{
                      "question_number": 12,
                      "type": "fill_in_the_blank",
                      "question": "The sun rises in the ____.",
                      "answer": "East"
                    }}
                  ]
                }}
                ```

                **Source Text:**
                ---
                {st.session_state.pdf_text}
                ---
                """
                try:
                    response = model.generate_content(quiz_prompt)
                    if response.text:
                        quiz_data_json = safe_json_loads(response.text)
                        if quiz_data_json and "quiz" in quiz_data_json and isinstance(quiz_data_json["quiz"], list):
                            if len(quiz_data_json["quiz"]) >= 15: # Check for minimum number of questions
                                st.session_state.quiz_data = quiz_data_json["quiz"]
                                st.session_state.user_answers = {}
                                st.session_state.quiz_submitted = False
                            else:
                                st.warning(f"The model generated {len(quiz_data_json['quiz'])} questions, but at least 15 were requested. Please try again.")
                                st.session_state.quiz_data = None
                        else:
                            st.error("The model did not return valid quiz data in the expected format (JSON with a 'quiz' list). Please try again.")
                            st.session_state.quiz_data = None
                    else:
                        st.error("The Gemini model returned an empty response for quiz generation. Please try again.")
                except genai.types.BlockedPromptException as e:
                    st.error(f"Quiz generation blocked by safety filters. Please try again with different content or adjust your prompt. Details: {e}")
                except Exception as e:
                    st.error(f"An API error occurred while generating the quiz: {e}")
                    st.session_state.quiz_data = None
    else:
        st.error("Cannot create a quiz. The original PDF text was not available or was too short for processing.")

# --- UI: Display and Manage Quiz ---
if st.session_state.quiz_data:
    st.subheader("🧠 Quiz Time!")
    
    with st.form(key='quiz_form'):
        user_answers = {}
        for item in st.session_state.quiz_data:
            q_num = item['question_number']
            q_text = item['question']
            q_type = item['type']
            
            st.markdown(f"**Question {q_num}:** {q_text}")
            
            if q_type == 'multiple_choice':
                options = item['options']
                if not isinstance(options, dict) or len(options) == 0: # Check for empty options too
                    st.warning(f"Question {q_num} (MCQ) has an invalid or empty options format. Skipping.")
                    continue
                
                # Create a list of option strings like "A) Option A Text"
                option_strings = [f"{key}) {value}" for key, value in options.items()]
                
                selected_option_string = st.radio(
                    "Your answer:", option_strings, key=f"q_{q_num}",
                    horizontal=False, label_visibility="collapsed" # Changed to False for better readability with longer options
                )
                # Store the full selected string (e.g., "A) Option A Text")
                user_answers[q_num] = selected_option_string
            
            elif q_type == 'true_false':
                user_choice = st.radio(
                    "Your answer:", ["True", "False", "Not Answered"], key=f"q_{q_num}",
                    horizontal=True, label_visibility="collapsed", index=2 # Default to "Not Answered"
                )
                user_answers[q_num] = user_choice

            elif q_type == 'fill_in_the_blank':
                user_input = st.text_input("Your answer:", key=f"q_{q_num}", label_visibility="collapsed")
                user_answers[q_num] = user_input
            
            st.markdown("---")
            
        submitted = st.form_submit_button("Check Answers")
        if submitted:
            st.session_state.quiz_submitted = True
            
            # Process answers for scoring
            processed_answers = {}
            for item in st.session_state.quiz_data:
                q_num = item['question_number']
                q_type = item['type']
                user_ans_raw = user_answers.get(q_num)
                
                if q_type == 'multiple_choice':
                    # Extract the letter (A, B, C, D) from "A) Option A Text"
                    if user_ans_raw and len(user_ans_raw) > 0 and ')' in user_ans_raw:
                        processed_answers[q_num] = user_ans_raw[0] # Take the first char 'A'
                    else:
                        processed_answers[q_num] = "Not Answered"
                else:
                    processed_answers[q_num] = user_ans_raw

            st.session_state.user_answers = processed_answers


# --- UI: Display Quiz Results ---
if st.session_state.quiz_submitted and st.session_state.quiz_data:
    st.subheader("📈 Results")
    
    score = 0
    total_questions = len(st.session_state.quiz_data)
    
    for item in st.session_state.quiz_data:
        q_num = item['question_number']
        q_text = item['question']
        correct_answer = str(item.get('answer', '')).strip().lower() # Ensure string and lowercase for comparison
        user_answer_raw = st.session_state.user_answers.get(q_num, "Not Answered")

        display_user_answer = user_answer_raw # What to show to the user
        actual_user_answer_for_comparison = str(user_answer_raw).strip().lower() # What to compare with

        is_correct = False
        
        if item['type'] == 'multiple_choice':
            # For MCQs, correct_answer is 'A', 'B', 'C', 'D'
            # user_answer_raw is 'A', 'B', 'C', 'D' (extracted from "A) Option Text")
            is_correct = actual_user_answer_for_comparison == correct_answer
            
            # Find the full option text for display based on the stored user_answer_raw (A,B,C,D)
            # This logic needs to retrieve the full text for the selected option letter
            if user_answer_raw != "Not Answered" and item.get('options'):
                display_user_answer = item['options'].get(user_answer_raw, user_answer_raw)
                display_user_answer = f"{user_answer_raw}) {display_user_answer}"
            else:
                display_user_answer = user_answer_raw


        elif item['type'] in ['true_false', 'fill_in_the_blank']:
            is_correct = actual_user_answer_for_comparison == correct_answer
        
        if is_correct:
            score += 1

        with st.container():
            st.markdown(f"**Question {q_num}:** {q_text}")
            
            # Display user answer vs correct answer
            if is_correct:
                st.success(f"✔️ Your answer: **{display_user_answer}** (Correct)")
            else:
                st.error(f"❌ Your answer: **{display_user_answer}**")
                # For MCQs, also show the full correct option text with its letter
                if item['type'] == 'multiple_choice' and item.get('options'):
                    correct_option_text = item['options'].get(item['answer'], "N/A")
                    st.info(f"💡 Correct answer: **{item['answer']}) {correct_option_text}**")
                else: # For T/F and Fill-in-the-blank
                    st.info(f"💡 Correct answer: **{item['answer']}**")
        
        st.markdown("---")

    st.markdown(f"### Your final score: **{score} / {total_questions}**")
    
    # Add a button to try the quiz again or upload a new file
    if st.button("Try Again or Upload New PDF"):
        # Reset all state to start fresh
        st.session_state.pdf_text = None
        st.session_state.summary = None
        st.session_state.quiz_data = None
        st.session_state.user_answers = {}
        st.session_state.quiz_submitted = False
        st.rerun()

st.sidebar.info("App created by PDF_Study_Agent.")
