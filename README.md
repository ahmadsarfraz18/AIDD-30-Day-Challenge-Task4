# PDF Summarizer & Quiz Generator

This project is an AI agent that summarizes PDF documents and generates quizzes from their content. It is built with Python, Streamlit, and the OpenAgents SDK.

## Features

- **PDF Summarizer**: Upload a PDF file to receive a concise summary (5-7 lines), a list of 5 key points, and 3 study questions.
- **Quiz Generator**: Automatically creates a quiz based on the PDF's content, including 5 multiple-choice questions and 3 short-answer questions. The quiz is returned in a clean JSON format.

## Project Structure

```
project/
│── agent.py
│── streamlit_app.py
│── requirements.txt
│── README.md
```

- **agent.py**: Contains the core logic for text extraction, summarization, and quiz generation.
- **streamlit_app.py**: Provides the web-based user interface using Streamlit.
- **requirements.txt**: Lists all the necessary Python libraries for the project.
- **README.md**: This file, providing an overview and instructions.

## How to Run the Project

1. **Install Dependencies**:
   Open your terminal and navigate to the `project` directory. Then, install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Streamlit App**:
   Once the dependencies are installed, you can start the application with the following command:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Use the Application**:
   Open your web browser and go to the local URL provided by Streamlit (usually `http://localhost:8501`). Upload a PDF file, and the agent will generate the summary and quiz for you.
