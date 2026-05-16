# Import Streamlit for UI
import streamlit as st
import os

# Import Google Generative AI library
import google.generativeai as genai


# -----------------------------------
# Configure Gemini API Key
# -----------------------------------

# Paste your NEW Gemini API key here
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# -----------------------------------
# Load Gemini model
# -----------------------------------

model = genai.GenerativeModel("models/gemini-2.5-flash")


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
st.title("AI SQL Query Generator")

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

        # Show result
        st.subheader("Generated SQL Query")

        # Display SQL nicely
        st.code(sql_query, language="sql")

    else:
        st.warning("Please enter a question.")