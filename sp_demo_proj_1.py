

#Note: This is a DEMO Proj - Aninda

import os
import sqlite3
from dotenv import load_dotenv
import streamlit as st
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

# Load environment variables
load_dotenv()
llamaindex_api_key = os.environ.get("LLAMAINDEX_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")

from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
# pip install llama-index-indices-managed-llama-cloud - done

index = LlamaCloudIndex(
  name="sp-ex-index-ex-1",
  project_name="Default",
  organization_id="e092ea91-1530-4ce4-9e93-10dd4a06e8b9",
  api_key=llamaindex_api_key
)

#nodes = index.as_retriever().retrieve(query)
#response = index.as_query_engine().query(query)


#---------------------------------


# Function to generate a response using the queried input
def generate_response(input_text):
    nodes = index.as_retriever().retrieve(input_text)  # Retrieve relevant nodes
    response = index.as_query_engine().query(input_text)  # Get the response
    return str(response)

#----------THE FOLLOWING CODE IS GENERIC FOR STREAMLIT INTERFACE TO ALLOW CHAT AND STORGAGE
# AND DISPLAY OF CHAT HISTORY AND REVIEW TO THE USER
# Function to initialize SQLite database and create a table for chat history
def create_chat_table():
    with sqlite3.connect("chat_history.db") as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT NOT NULL
            )
            """
        )
        conn.commit()


# Function to add a new chat entry to the database
def add_chat_to_db(query, response):
    with sqlite3.connect("chat_history.db") as conn:
        conn.execute(
            "INSERT INTO chat_history (query, response) VALUES (?, ?)", (query, response)
        )
        conn.commit()


# Function to retrieve the entire chat history from the database
def fetch_chat_history():
    with sqlite3.connect("chat_history.db") as conn:
        rows = conn.execute("SELECT id, query, response FROM chat_history").fetchall()
    return [{"id": row[0], "query": row[1], "response": row[2]} for row in rows]


# App layout and functionality
st.sidebar.title("Chat History")

# Initialize the database and create the table
create_chat_table()

# Fetch chat history from the database
chat_history = fetch_chat_history()

# Display previous chats in the sidebar
selected_chat_id = None
for chat in chat_history:
    if st.sidebar.button(chat["query"], key=chat["id"]):    # added key=chat["id] to solve auto key problem
        selected_chat_id = chat["id"]
        #print(selected_chat_id)

# Main content area
st.title("LLM Chat With User Document")

# Show the response when a chat is selected in the sidebar
if selected_chat_id is not None:
    selected_chat = next(
        (
            chat
            for chat in chat_history
            if chat["id"] == selected_chat_id
        ),
        None,
    )
    if selected_chat:
        st.subheader(f"Previous Query: {selected_chat['query']}")
        st.info(selected_chat["response"])

with st.form("query_form"):
    text_input = st.text_area("Enter your query here")  # User input
    submitted = st.form_submit_button("Submit") # Had to remove key=1 to make the same key error for buttons
    if submitted:
        if text_input:
            # Generate a new response
            response = generate_response(text_input)

            # Add the query and response to the database
            add_chat_to_db(text_input, response)

            # Display the response in the main content area
            st.subheader("Your Query:")
            st.write(text_input)
            st.subheader("Response:")
            st.info(response)

            # Refresh the app to update the sidebar with the new chat entry
           # st.experimental_rerun()
        else:
            st.warning("Please enter a query to submit.")


























