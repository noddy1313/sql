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
# Animated Professional AI Theme
# -----------------------------------

st.markdown("""
<style>

/* Animated Background */
..stApp {

    background: linear-gradient(
        -45deg,
        #FDF2F8,
        #FCE7F3,
        #FBCFE8,
        #FAE8FF
    );

    background-size: 400% 400%;

    animation: gradientBG 12s ease infinite;
}
/* Background Animation */
@keyframes gradientBG {

    0% {
        background-position: 0% 50%;
    }

    50% {
        background-position: 100% 50%;
    }

    100% {
        background-position: 0% 50%;
    }
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
html, body, [class*="css"] {
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
    border-radius: 16px !important;
    border: 1px solid #D1D5DB !important;
    padding: 14px !important;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
}

/* Buttons */
.stButton > button {

    background: linear-gradient(
        to right,
        #22C55E,
        #16A34A
    );

    color: white !important;

    border-radius: 14px;

    border: none;

    font-weight: bold;

    height: 3em;

    transition: 0.3s ease;

    box-shadow: 0px 4px 12px rgba(34,197,94,0.3);
}

/* Hover Effect */
.stButton > button:hover {

    transform: scale(1.02);

    background: linear-gradient(
        to right,
        #16A34A,
        #15803D
    );
}

/* Sidebar */
section[data-testid="stSidebar"] {

    background-color: rgba(255,255,255,0.8);

    backdrop-filter: blur(12px);

    border-right: 1px solid #E5E7EB;
}

/* Sidebar Text */
section[data-testid="stSidebar"] * {
    color: #111827 !important;
}

/* Cards */
[data-testid="metric-container"] {

    background-color: rgba(255,255,255,0.8);

    border-radius: 16px;

    padding: 12px;

    border: 1px solid #E5E7EB;

    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
}

/* Dataframe */
[data-testid="stDataFrame"] {

    border-radius: 16px;

    overflow: hidden;

    background-color: white;
}

/* Code Block */
pre {

    border-radius: 14px !important;

    border: 1px solid #E5E7EB !important;

    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
}

/* Selectbox */
div[data-baseweb="select"] * {
    color: #111827 !important;
}

/* Horizontal Line */
hr {
    border: 1px solid #D1D5DB;
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
    font-weight:500;
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