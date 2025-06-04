import streamlit as st
import sqlite3
import pandas as pd
import openai

# Set your OpenAI API key
openai.api_key = "Xyz123"
def get_sql_from_openai(prompt, question):
    try:
        full_prompt = f"{prompt}\n\nUser question: {question}\nSQL:"
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"OpenAI error: {e}")
        return None

def query_db(sql, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return pd.DataFrame(rows, columns=columns)
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

# Correct schema prompt
prompt = """
You are an expert SQL assistant.

The SQLite table is named 'Employee' and has the following columns:
- id (INTEGER)
- name (TEXT)
- age (INTEGER)
- department (TEXT)
- email (TEXT)

Translate the user's English question into a valid SQLite SQL query.
Only return the SQL query — no explanations, comments, or markdown.
Never use columns that are not listed.
"""

# Streamlit UI
st.set_page_config(page_title="NL to SQL with OpenAI")
st.title("Natural Language to SQL (using GPT-4)")

question = st.text_input("Ask your question about the Employee data:", key="user_input")
submit = st.button("Submit")

if submit and question:
    with st.spinner("Generating SQL..."):
        sql_query = get_sql_from_openai(prompt, question)

    if sql_query:
        st.subheader("Generated SQL Query:")
        st.code(sql_query, language="sql")

        with st.spinner("Executing SQL query..."):
            result_df = query_db(sql_query, "Employee.db")

        if result_df is not None and not result_df.empty:
            st.subheader("Results")
            st.dataframe(result_df)
        else:
            st.warning("No results found or query returned nothing.")
