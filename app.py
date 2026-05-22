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