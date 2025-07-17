import streamlit as st
import mysql.connector
import subprocess
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()


# Function to get DB Schema
def get_db_schema():
    return """
Table: actor
 - actor_id (INT)
 - first_name (VARCHAR)
 - last_name (VARCHAR)
 - last_update (TIMESTAMP)

Table: film
 - film_id (INT)
 - title (VARCHAR)
 - description (TEXT)
 - release_year (YEAR)
 - language_id (INT)
 - rental_duration (INT)
 - rental_rate (DECIMAL)
 - length (INT)
 - replacement_cost (DECIMAL)
 - rating (ENUM)
 - special_features (SET)
 - last_update (TIMESTAMP)

Table: film_actor
 - actor_id (INT)
 - film_id (INT)
 - last_update (TIMESTAMP)

Table: customer
 - customer_id (INT)
 - store_id (INT)
 - first_name (VARCHAR)
 - last_name (VARCHAR)
 - email (VARCHAR)
 - address_id (INT)
 - active (BOOLEAN)
 - create_date (DATETIME)
 - last_update (TIMESTAMP)

Table: rental
 - rental_id (INT)
 - rental_date (DATETIME)
 - inventory_id (INT)
 - customer_id (INT)
 - return_date (DATETIME)
 - staff_id (INT)
 - last_update (TIMESTAMP)

Table: payment
 - payment_id (INT)
 - customer_id (INT)
 - staff_id (INT)
 - rental_id (INT)
 - amount (DECIMAL)
 - payment_date (DATETIME)
"""




# Function to call Ollama via subprocess
def generate_sql_via_ollama(nl_query, schema):
    prompt = f"""
You are a MySQL SQL generator and query assistant.

Instructions:
1. Generate an accurate, syntactically correct MySQL query for the user request below.
2. Output only the final SQL query. No explanations, markdown, or wrapping.
3. If the user asks for a DROP TABLE command, output it as plain text but ask user to confirm.

### Database Schema:
{schema}

### User Request:
{nl_query}

### SQL Query:
"""

    result = subprocess.run(
        ["ollama", "run", "qwen3:4b"],
        input=prompt,
        text=True,
        capture_output=True
    )

    output = result.stdout.strip()
    sql_query = extract_sql_from_text(output)
    return sql_query





# Function to extract SQL from text response
def extract_sql_from_text(text_response):
    lines = text_response.splitlines()
    sql_lines = [line for line in lines if line.strip().upper().startswith(("SELECT","INSERT","UPDATE","DELETE","DROP","CREATE","ALTER"))]
    return " ".join(sql_lines).strip()




def run_sql_query(query):
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    cursor = conn.cursor()
    cursor.execute(query)
    try:
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
    except:
        results, columns = [], []
    conn.commit()
    conn.close()
    return results, columns




# Streamlit UI
st.title("💡 NLP to SQL Query Executor - Sakila DB")

user_input = st.text_input("🔎 Enter your natural language query:")

if st.button("🚀 Run Query"):
    if user_input.strip() == "":
        st.warning("Please enter a valid query.")
    else:
        with st.spinner("Generating SQL query..."):
            schema = get_db_schema()
            sql_query = generate_sql_via_ollama(user_input, schema)
            st.code(sql_query, language='sql')






# Safety check for destructive queries
            destructive_keywords = ["DROP TABLE", "DELETE FROM"]
            if any(keyword in sql_query.upper() for keyword in destructive_keywords):
                confirm = st.text_input("⚠️ This query may modify or delete data. Type 'CONFIRM' to proceed:")
                if confirm.strip().upper() != "CONFIRM":
                    st.warning("Query not executed. Confirmation required for destructive commands.")
                else:
                    try:
                        results, columns = run_sql_query(sql_query)
                        st.success("✅ Query executed successfully.")
                        if results:
                            df = pd.DataFrame(results, columns=columns)
                            st.dataframe(df)
                        else:
                            st.write("Query executed successfully. No data returned.")
                    except Exception as e:
                        st.error(f"❌ Error executing SQL: {e}")
            else:
                try:
                    results, columns = run_sql_query(sql_query)
                    st.success("✅ Query executed successfully.")
                    if results:
                        df = pd.DataFrame(results, columns=columns)
                        st.dataframe(df)
                    else:
                        st.write("Query executed successfully. No data returned.")
                except Exception as e:
                    st.error(f"❌ Error executing SQL: {e}")
