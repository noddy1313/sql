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
# Professional White Theme
# -----------------------------------

st.markdown("""
<style>

/* Main App */
.stApp {
    background: linear-gradient(
        to bottom right,
        #F9FAFB,
        #E5E7EB
    );
}

/* Main Title */
h1 {
    color: #16A34A !important;
    text-align: center;
    font-weight: 800;
}

/* Subheaders */
h2, h3 {
    color: #111827 !important;
}

/* General Text */
html, body, [class*="css"]  {
    color: #111827 !important;
}

/* Paragraph Text */
p, label, div {
    color: #111827 !important;
}

/* Text Area */
textarea {
    background-color: white !important;
    color: #111827 !important;
    border-radius: 14px !important;
    border: 1px solid #D1D5DB !important;
    padding: 12px !important;
}

.stButton > button {

    background: linear-gradient(
        to right,
        #ec4899,
        #a855f7
    );

    color: white !important;

    border-radius: 14px;

    border: none;

    font-weight: bold;

    height: 3em;

    transition: 0.3s ease;
}


/* Hover */
.stButton > button:hover {

    transform: scale(1.02);

    background: linear-gradient(
        to right,
        #db2777,
        #9333ea
    );
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: white;
    border-right: 1px solid #E5E7EB;
}

/* Sidebar Text */
section[data-testid="stSidebar"] * {
    color: #111827 !important;
}

/* Cards */
[data-testid="metric-container"] {
    background-color: white;
    border-radius: 12px;
    padding: 10px;
    border: 1px solid #E5E7EB;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}

/* Code Block */
pre {
    border-radius: 12px !important;
}

/* Input text */
input, textarea {
    color: #111827 !important;
}

/* Selectbox */
div[data-baseweb="select"] * {
    color: #111827 !important;
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


# -----------------------------------
# Database Setup
# -----------------------------------

DB_NAME = "database.db"

# Create DB if not exists
if not os.path.exists(DB_NAME):

    temp_conn = sqlite3.connect(DB_NAME)

    temp_conn.close()

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

try:

    conn = sqlite3.connect(
        DB_NAME,
        check_same_thread=False
    )

    cursor = conn.cursor()

except Exception as e:

    st.error(
        f"❌ Database Connection Error: {str(e)}"
    )

    st.stop()


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

try:

    cursor.execute("""
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    """)

    tables = cursor.fetchall()

except:

    tables = []

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
'>
🤖 AI SQL Query Generator
</h1>
""", unsafe_allow_html=True)

st.markdown(
    """
    <p style='
    text-align:center;
    color:#111827;
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

            except Exception:

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

st.markdown("---")

if st.button("🗑️ Clear Everything"):

    st.session_state.history = []

    st.session_state.sql_query = ""

    st.rerun()