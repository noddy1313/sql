# Import Streamlit for UI
import streamlit as st
import os
import sqlite3
import pandas as pd

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
    background-color: #1E1E1E !important;
    color: white !important;
}

/* Button styling */
.stButton > button {
    background-color: #4CAF50;
    color: white;
    border-radius: 12px;
    height: 3em;
    width: 100%;
    font-size: 16px;
    border: none;
    font-weight: bold;
}

/* Button hover */
.stButton > button:hover {
    background-color: #45a049;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #161B22;
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
    "models/gemini-flash-latest"
)


# -----------------------------------
# Sidebar
# -----------------------------------

st.sidebar.title("⚙️ AI SQL Generator")

st.sidebar.info(
    "Generate SQL queries using Gemini AI 🚀"
)

st.sidebar.markdown("---")


# -----------------------------------
# Upload Database File
# -----------------------------------

uploaded_db = st.sidebar.file_uploader(
    "📁 Upload SQLite Database",
    type=["db", "sqlite", "sqlite3"]
)

# Default database
DB_NAME = "database.db"

# Save uploaded DB
if uploaded_db is not None:

    DB_NAME = uploaded_db.name

    with open(DB_NAME, "wb") as f:
        f.write(uploaded_db.getbuffer())

    st.sidebar.success(
        "✅ Database uploaded successfully."
    )


# -----------------------------------
# Database Connection
# -----------------------------------

conn = sqlite3.connect(
    DB_NAME,
    check_same_thread=False
)

cursor = conn.cursor()


# -----------------------------------
# Session State
# -----------------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "sql_query" not in st.session_state:
    st.session_state.sql_query = ""


# -----------------------------------
# Sidebar Metrics
# -----------------------------------

st.sidebar.metric(
    "Queries Generated",
    len(st.session_state.history)
)


# -----------------------------------
# Database Viewer
# -----------------------------------

st.sidebar.subheader("🛢️ Database Viewer")

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
""")

tables = cursor.fetchall()

# Refresh valid table names only
table_names = []

for table in tables:

    table_name = table[0]

    try:

        cursor.execute(
            f"SELECT 1 FROM {table_name} LIMIT 1"
        )

        table_names.append(table_name)

    except:

        pass

# Avoid empty selectbox error
if not table_names:
    table_names = ["No Tables"]

selected_table = st.sidebar.selectbox(
    "📋 Select Table",
    table_names
)


# -----------------------------------
# Function to Generate SQL Query
# -----------------------------------

def generate_sql(prompt):

    try:

        full_prompt = f"""
You are an SQL generator.

Rules:
1. Return ONLY SQL query
2. No explanation
3. No markdown
4. No comments
5. No extra text

User Request:
{prompt}
"""

        response = model.generate_content(
            full_prompt
        )

        sql = response.text.strip()

        # Remove markdown formatting
        sql = sql.replace("```sql", "")
        sql = sql.replace("```", "")
        sql = sql.strip()

        return sql

    except Exception as e:

        return f"❌ Error: {str(e)}"


# -----------------------------------
# Main Title
# -----------------------------------

st.markdown("""
<h1 style='
text-align: center;
color: #4CAF50;
font-size: 55px;
font-weight: bold;
'>
🤖 AI SQL Query Generator
</h1>
""", unsafe_allow_html=True)

st.markdown(
    """
    <p style='
    text-align:center;
    color:white;
    font-size:18px;
    '>
    Convert natural language into SQL queries instantly 🚀
    </p>
    """,
    unsafe_allow_html=True
)


# -----------------------------------
# User Input
# -----------------------------------

user_prompt = st.text_area(
    "Enter your database question:",
    placeholder="Example: Find employee with second highest salary"
)


# -----------------------------------
# Generate SQL Button
# -----------------------------------

if st.button("🚀 Generate SQL"):

    if user_prompt.strip():

        with st.spinner("Generating SQL query..."):

            st.session_state.sql_query = generate_sql(
                user_prompt
            )

        # Save History
        st.session_state.history.append({
            "question": user_prompt,
            "sql": st.session_state.sql_query
        })

    else:

        st.warning(
            "Please enter a question."
        )


# -----------------------------------
# Show Generated SQL
# -----------------------------------

if st.session_state.sql_query:

    st.subheader("📄 Generated SQL Query")

    st.code(
        st.session_state.sql_query,
        language="sql"
    )

    # Download SQL
    st.download_button(
        label="📥 Download SQL",
        data=st.session_state.sql_query,
        file_name="query.sql",
        mime="text/sql"
    )


# -----------------------------------
# Explain SQL Feature
# -----------------------------------

if st.session_state.sql_query:

    if st.button("🔍 Explain SQL"):

        with st.spinner("Explaining SQL query..."):

            explanation_prompt = f"""
Explain this SQL query in simple English:

{st.session_state.sql_query}
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

if st.session_state.sql_query:

    if st.button("▶️ Execute Query"):

        try:

            cursor.execute(
                st.session_state.sql_query
            )

            conn.commit()

            if st.session_state.sql_query.strip().upper().startswith("SELECT"):

                results = cursor.fetchall()

                column_names = [
                    description[0]
                    for description in cursor.description
                ]

                df = pd.DataFrame(
                    results,
                    columns=column_names
                )

                st.subheader("📊 Query Results")

                st.dataframe(df)

            else:

                st.success(
                    "✅ Query executed successfully."
                )

        except Exception as e:

            st.error(
                f"❌ SQL Error: {str(e)}"
            )


# -----------------------------------
# SQL Verification Feature
# -----------------------------------

if st.session_state.sql_query:

    if st.button("✅ Verify SQL"):

        try:

            cursor.execute(
                f"EXPLAIN QUERY PLAN {st.session_state.sql_query}"
            )

            st.success(
                "✅ SQL Query is valid."
            )

        except Exception as e:

            st.error(
                f"❌ Invalid SQL Query: {str(e)}"
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
# Clear Everything
# -----------------------------------

if st.button("🗑️ Clear Everything"):

    try:

        st.session_state.history.clear()

        st.session_state.sql_query = ""

        # Delete all tables
        cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """)

        all_tables = cursor.fetchall()

        for table in all_tables:

            table_name = table[0]

            cursor.execute(
                f"DROP TABLE IF EXISTS {table_name}"
            )

        conn.commit()

        st.success(
            "✅ History and all database tables cleared."
        )

        st.rerun()

    except Exception as e:

        st.error(
            f"❌ Error clearing database: {str(e)}"
        )


# -----------------------------------
# Database Preview
# -----------------------------------

st.markdown("---")

st.subheader("🛢️ Database Preview")

if selected_table != "No Tables":

    try:

        preview_query = f"""
        SELECT *
        FROM {selected_table}
        LIMIT 5
        """

        preview_df = pd.read_sql_query(
            preview_query,
            conn
        )

        st.dataframe(preview_df)

    except Exception as e:

        st.error(
            f"❌ Error loading preview: {str(e)}"
        )


# -----------------------------------
# Database Tables View
# -----------------------------------

st.markdown("---")

st.header("🗂️ Database Tables")

if selected_table != "No Tables":

    for table in table_names:

        st.subheader(f"📄 {table}")

        try:

            query = f"""
            SELECT *
            FROM {table}
            LIMIT 10
            """

            table_df = pd.read_sql_query(
                query,
                conn
            )

            st.dataframe(table_df)

        except Exception as e:

            st.error(
                f"❌ Error loading {table}: {str(e)}"
            )

else:

    st.warning(
        "⚠️ No tables found in database."
    )