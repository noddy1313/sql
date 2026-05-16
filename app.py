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
    page_icon="🤖"
)


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
# Chat History
# -----------------------------------

if "history" not in st.session_state:
    st.session_state.history = []


# -----------------------------------
# Function to generate SQL query
# -----------------------------------

def generate_sql(prompt):

    try:

        # Better prompt for SQL generation
        full_prompt = f"""
        You are an SQL expert.

        Generate only SQL query.
        Do not explain anything.

        User Request:
        {prompt}
        """

        # Send prompt to Gemini
        response = model.generate_content(full_prompt)

        # Return generated SQL query
        return response.text.strip()

    # Error handling
    except Exception as e:
        return f"❌ Error: {str(e)}"


# -----------------------------------
# Streamlit App UI
# -----------------------------------

# App title
st.title("🤖 AI SQL Query Generator")


# User input box
user_prompt = st.text_area(
    "Enter your database question:",
    placeholder="Example: Show all employees with salary greater than 50000"
)


# Generate button
if st.button("Generate SQL"):

    # Check if input is empty
    if user_prompt.strip():

        # Loading animation
        with st.spinner("Generating SQL query..."):

            # Generate SQL
            sql_query = generate_sql(user_prompt)

        # Save chat history
        st.session_state.history.append({
            "question": user_prompt,
            "sql": sql_query
        })

        # Show result
        st.subheader("📄 Generated SQL Query")

        # Display SQL nicely
        st.code(sql_query, language="sql")

        # Copy button hint
        st.info("💡 Hover over SQL block to copy query.")

        # Download SQL file
        st.download_button(
            label="📥 Download SQL",
            data=sql_query,
            file_name="query.sql",
            mime="text/sql"
        )

    else:
        st.warning("Please enter a question.")


# -----------------------------------
# Chat History Section
# -----------------------------------

st.subheader("🧠 Chat History")

for item in reversed(st.session_state.history):

    st.markdown(f"**Question:** {item['question']}")

    st.code(item['sql'], language="sql")