# -----------------------------------
# Explain SQL Feature
# -----------------------------------

if "sql_query" in locals():

    if st.button("🔍 Explain SQL"):

        with st.spinner("Explaining SQL query..."):

            explanation_prompt = f"""
            Explain this SQL query in simple English:

            {sql_query}
            """

            explanation = model.generate_content(
                explanation_prompt
            )

            st.subheader("🧠 SQL Explanation")

            st.write(explanation.text)


# -----------------------------------
# Execute SQL Query Feature
# -----------------------------------

if "sql_query" in locals():

    if st.button("▶️ Execute Query"):

        try:

            # Execute query
            cursor.execute(sql_query)

            # Fetch results
            results = cursor.fetchall()

            # Show results
            st.subheader("📊 Query Results")

            st.dataframe(results)

        except Exception as e:

            st.error(f"❌ SQL Error: {str(e)}")


# -----------------------------------
# Clear Chat History Button
# -----------------------------------

st.markdown("---")

if st.button("🗑️ Clear History"):

    st.session_state.history.clear()

    st.success("✅ History cleared successfully.")