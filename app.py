# Import Streamlit for UI
import streamlit as st
import os
import sqlite3

# Import Google Generative AI library
import google.generativeai as genai


# -----------------------------------
# Configure Page
# -----------------------------------

st.set_page_config(
    page_title="AI SQL Query Generator",
    page_icon="🤖",
    layout="centered"
)


# -----------------------------------
# Custom UI Design
# -----------------------------------

st.markdown("""
<style>

/* Main background */
.stApp {
    background-color: #0E1117;
    color: white;
}

/* Text area */
textarea {
    border-radius: 10px !important;
}

/* Button styling */
.stButton > button {
    background-color: #4CAF50;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    border: none;
}

/* Button hover */
.stButton > button:hover {
    background-color: #45a049;
}

/* Code block */
code {
    font-size: 15px;
}

</style>
""", unsafe_allow_html=True)


# -----------------------------------
# Configure Gemini API Key
# -----------------------------------

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)


# -----------------------------------
# Load Gemini model
# -----------------------------------

model = genai.GenerativeModel(
    "models/gemini-2.5-flash"
)


# -----------------------------------
# Database Connection
# -----------------------------------

conn = sqlite3.connect("database.db")
cursor = conn.cursor()


# -----------------------------------
# Create Example Table
# -----------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY,
    name TEXT,
    marks INTEGER
)
""")

conn.commit()


# -----------------------------------
# Chat History
# -----------------------------------

if "history" not in st.session_state:
    st.session_state.history = []


# -----------------------------------
# Function to Generate SQL Query
# -----------------------------------

def generate_sql(prompt):

    try:

        full_prompt = f"""
        You are an SQL expert.

        Generate only SQL query.
        Do not explain anything.

        User Request:
        {prompt}
        """

        response = model.generate_content(
            full_prompt
        )

        return response.text.strip()

    except Exception as e:

        return f"❌ Error: {str(e)}"


# -----------------------------------
# Sidebar
# -----------------------------------

st.sidebar.title("⚙️ AI SQL Generator")

st.sidebar.info(
    "Generate SQL queries using Google Gemini AI."
)

st.sidebar.markdown("---")

st.sidebar.metric(
    "Queries Generated",
    len(st.session_state.history)
)


# -----------------------------------
# Main Title
# -----------------------------------

st.markdown("""
<h1 style='text-align: center;
color: #4CAF50;'>
🤖 AI SQL Query Generator
</h1>
""", unsafe_allow_html=True)

st.markdown(
    "<p style='text-align:center;'>Convert natural language into SQL queries instantly 🚀</p>",
    unsafe_allow_html=True
)


# -----------------------------------
# User Input
# -----------------------------------

user_prompt = st.text_area(
    "Enter your database question:",
    placeholder="Example: Show all employees with salary greater than 50000"
)


# -----------------------------------
# Generate SQL Button
# -----------------------------------

sql_query = ""

if st.button("🚀 Generate SQL"):

    if user_prompt.strip():

        with st.spinner("Generating SQL query..."):

            sql_query = generate_sql(
                user_prompt
            )

        # Save History
        st.session_state.history.append({
            "question": user_prompt,
            "sql": sql_query
        })

        # Show SQL
        st.subheader("📄 Generated SQL Query")

        st.code(
            sql_query,
            language="sql"
        )

        st.info(
            "💡 Hover over SQL block to copy query."
        )

        # Download SQL
        st.download_button(
            label="📥 Download SQL",
            data=sql_query,
            file_name="query.sql",
            mime="text/sql"
        )

    else:

        st.warning(
            "Please enter a question."
        )


# -----------------------------------
# Explain SQL Feature
# -----------------------------------

if sql_query:

    if st.button("🔍 Explain SQL"):

        with st.spinner("Explaining SQL query..."):

            explanation_prompt = f"""
Explain this SQL query in simple English:

{sql_query}
"""

            explanation = model.generate_content(
                explanation_prompt
            )

            st.subheader(
                "🧠 SQL Explanation"
            )

            st.write(
                explanation.text
            )


# -----------------------------------
# Execute SQL Query Feature
# -----------------------------------

if sql_query:

    if st.button("▶️ Execute Query"):

        try:

            cursor.execute(sql_query)

            results = cursor.fetchall()

            st.subheader(
                "📊 Query Results"
            )

            st.dataframe(results)

        except Exception as e:

            st.error(
                f"❌ SQL Error: {str(e)}"
            )


# -----------------------------------
# Chat History
# -----------------------------------

st.subheader("🧠 Chat History")

for item in reversed(st.session_state.history):

    st.markdown(
        f"### ❓ {item['question']}"
    )

    st.code(
        item['sql'],
        language="sql"
    )


# -----------------------------------
# Clear History Button
# -----------------------------------

if st.button("🗑️ Clear History"):

    st.session_state.history.clear()

    st.success(
        "✅ History cleared successfully."
    )