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
# Sidebar
# -----------------------------------

st.sidebar.title("⚙️ AI SQL Generator")

st.sidebar.info(
    "Generate SQL queries using Gemini AI 🚀"
)

st.sidebar.markdown("---")


# -----------------------------------
# Theme Selector
# -----------------------------------

theme_mode = st.sidebar.selectbox(
    "🎨 Select Theme",
    ["Dark", "Light"]
)


# -----------------------------------
# Dynamic Theme CSS
# -----------------------------------

if theme_mode == "Dark":

    st.markdown("""
    <style>

    .stApp {
        background-color: #0E1117;
    }

    textarea {
        border-radius: 10px !important;
        background-color: #1E1E1E !important;
        color: white !important;
    }

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

    .stButton > button:hover {
        background-color: #45a049;
    }

    section[data-testid="stSidebar"] {
        background-color: #161B22;
    }

    </style>
    """, unsafe_allow_html=True)

else:

    st.markdown("""
    <style>

    .stApp {
        background-color: white;
    }

    textarea {
        border-radius: 10px !important;
        background-color: #F5F5F5 !important;
        color: black !important;
    }

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

    .stButton > button:hover {
        background-color: #45a049;
    }

    section[data-testid="stSidebar"] {
        background-color: #EAEAEA;
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

if not table_names:
    table_names = ["No Tables"]

selected_table = st.sidebar.selectbox(
    "📋 Select Table",
    table_names
)


# -----------------------------------
# Generate SQL Function
# -----------------------------------

def generate_sql(prompt):

    try:

        cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        """)

        existing_tables = [
            table[0]
            for table in cursor.fetchall()
        ]

        full_prompt = f"""
You are an SQL generator.

Rules:
1. Return ONLY SQL query
2. No explanation
3. No markdown
4. No comments
5. No extra text

Database Tables:
{existing_tables}

Instructions:
- If required table already exists, DO NOT generate CREATE TABLE query.
- Generate only the required SQL query.

User Request:
{prompt}
"""

        response = model.generate_content(
            full_prompt
        )

        sql = response.text.strip()

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
font-size: 55px;
font-weight: bold;
color: #4CAF50;
'>
🤖 AI SQL Query Generator
</h1>
""", unsafe_allow_html=True)

st.markdown(
    """
    <p style='
    text-align:center;
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

    st.download_button(
        label="📥 Download SQL",
        data=st.session_state.sql_query,
        file_name="query.sql",
        mime="text/sql"
    )


# -----------------------------------
# Explain SQL
# -----------------------------------

if st.session_state.sql_query:

    if not st.session_state.sql_query.startswith("❌"):

        if st.button("🔍 Explain SQL"):

            try:

                with st.spinner(
                    "Explaining SQL query..."
                ):

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

            except Exception as e:

                st.error(
                    "❌ Gemini API quota exceeded."
                )


# -----------------------------------
# Execute Query
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
# Verify SQL
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
# Database Preview
# -----------------------------------

st.markdown("---")

st.subheader("🛢️ Database Preview")

try:

    if (
        st.session_state.sql_query
        and st.session_state.sql_query.strip().upper().startswith("SELECT")
    ):

        query_df = pd.read_sql_query(
            st.session_state.sql_query,
            conn
        )

        st.dataframe(query_df)

    elif selected_table != "No Tables":

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
# Download Table
# -----------------------------------

if selected_table != "No Tables":

    try:

        download_query = f"""
        SELECT *
        FROM {selected_table}
        """

        download_df = pd.read_sql_query(
            download_query,
            conn
        )

        csv = download_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label=f"📥 Download {selected_table} Table",
            data=csv,
            file_name=f"{selected_table}.csv",
            mime="text/csv"
        )

    except Exception as e:

        st.error(
            f"❌ Download Error: {str(e)}"
        )


# -----------------------------------
# Database Tables
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


# -----------------------------------
# Chat History
# -----------------------------------

st.markdown("---")

st.subheader("🧠 Chat History")

for item in reversed(st.session_state.history):

    st.markdown(
       f"### 💬 {item['question']}"
    )

    st.code(
        item['sql'],
        language="sql"
    )


# -----------------------------------
# Clear Everything
# -----------------------------------

if st.button("🗑️ Clear Everything"):

    st.session_state.history = []

    st.session_state.sql_query = ""

    st.rerun()