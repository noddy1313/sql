# -----------------------------------
# RGB Gradient Main Title
# -----------------------------------

st.markdown("""
<h1 style='
text-align: center;
font-size: 55px;
font-weight: bold;
background: linear-gradient(
90deg,
rgb(255,0,0),
rgb(255,127,0),
rgb(255,255,0),
rgb(0,255,0),
rgb(0,0,255),
rgb(75,0,130),
rgb(148,0,211)
);
-webkit-background-clip: text;
-webkit-text-fill-color: transparent;
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