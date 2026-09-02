import streamlit as st
from pathlib import Path
import sqlite3

from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_agent
from langchain_groq import ChatGroq


# ============================================================
# STREAMLIT UI
# ============================================================

st.set_page_config(
    page_title="LangChain: Chat with SQL DB",
    page_icon="🦜"
)

st.title("🦜 LangChain: Chat with SQL DB")


# ============================================================
# DATABASE OPTIONS
# ============================================================

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = [
    "Use SQLITE3 DATABASE - students.db",
    "Connect to your SQL Database"
]

selected_opt = st.sidebar.radio(
    label="Choose the DB which you want to chat",
    options=radio_opt
)


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

if radio_opt.index(selected_opt) == 1:

    db_uri = MYSQL

    mysql_host = st.sidebar.text_input("Provide MySQL Host")
    mysql_user = st.sidebar.text_input("MySQL User")
    mysql_password = st.sidebar.text_input(
        "MySQL Password",
        type="password"
    )
    mysql_db = st.sidebar.text_input("MySQL Database")

else:

    db_uri = LOCALDB


# ============================================================
# GROQ API KEY
# ============================================================

api_key = st.sidebar.text_input(
    label="Groq API Key",
    type="password"
)

if not api_key:
    st.info("Please add the Groq API key")
    st.stop()


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    api_key=api_key,
    model_name="openai/gpt-oss-safeguard-20b",
    streaming=True
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

@st.cache_resource(ttl="2h")
def configure_db(
    db_uri,
    mysql_host=None,
    mysql_user=None,
    mysql_password=None,
    mysql_db=None
):

    if db_uri == LOCALDB:

        dbfilepath = (
            Path(__file__).parent / "students.db"
        ).absolute()

        print(dbfilepath)

        creator = lambda: sqlite3.connect(
            f"file:{dbfilepath}?mode=ro",
            uri=True
        )

        return SQLDatabase(
            create_engine(
                "sqlite:///",
                creator=creator
            )
        )

    elif db_uri == MYSQL:

        if not (
            mysql_host
            and mysql_user
            and mysql_password
            and mysql_db
        ):
            st.error(
                "Please provide all the MySQL database information"
            )
            st.stop()

        return SQLDatabase(
            create_engine(
                f"mysql+mysqlconnector://"
                f"{mysql_user}:{mysql_password}"
                f"@{mysql_host}/{mysql_db}"
            )
        )


# ============================================================
# CREATE DATABASE
# ============================================================

if db_uri == MYSQL:

    db = configure_db(
        db_uri=db_uri,
        mysql_host=mysql_host,
        mysql_user=mysql_user,
        mysql_password=mysql_password,
        mysql_db=mysql_db
    )

else:

    db = configure_db(
        db_uri=db_uri
    )


# ============================================================
# SQL TOOLKIT
# ============================================================

toolkit = SQLDatabaseToolkit(
    db=db,
    llm=llm
)

tools = toolkit.get_tools()


# ============================================================
# MODERN LANGCHAIN AGENT
# ============================================================

agent = create_agent(
    model=llm,
    tools=tools
)


# ============================================================
# CHAT HISTORY
# ============================================================

if (
    "messages" not in st.session_state
    or st.sidebar.button("Clear message history")
):

    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "How can I help you?"
        }
    ]


# Display previous messages

for msg in st.session_state.messages:

    st.chat_message(
        msg["role"]
    ).write(
        msg["content"]
    )


# ============================================================
# USER QUERY
# ============================================================

user_query = st.chat_input(
    placeholder="Ask anything from the database"
)


if user_query:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query
        }
    )

    st.chat_message("user").write(user_query)


    # ========================================================
    # AGENT RESPONSE
    # ========================================================

    with st.chat_message("assistant"):

        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_query
                    }
                ]
            }
        )

        # Get final response
        answer = response["messages"][-1].content

        st.write(answer)


        # Save assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )
