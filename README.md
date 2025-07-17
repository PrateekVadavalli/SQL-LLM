# NLP to SQL Query Executor

This project converts natural language queries to SQL queries and executes them directly on your MySQL database using Ollama (running locally).

---

## Features

- Converts natural language prompts to MySQL queries.
- Uses Ollama models locally for fast, private inference.
- Executes generated SQL directly on your MySQL Sakila database.
- Safety confirmation for destructive queries like DROP TABLE or DELETE.

---

## Requirements

- Python 3.8+
- MySQL running with Sakila database
- Ollama installed with qwen3:4b model pulled
- pandas
- mysql-connector-python

---

## Installation

1. Clone this repository.

2. Install dependencies:

    ```bash
    pip install streamlit pandas mysql-connector-python
    ```

3. Ensure Ollama is installed and the model is pulled:

    ```bash
    ollama pull qwen3:4b
    ```

4. Run MySQL locally.

---

## Running the App

```bash
streamlit run app.py
