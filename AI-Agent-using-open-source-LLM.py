### Creating end to end search engine GenAI app using Tools and Agents with opem source LLM

import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun, DuckDuckGoSearchRun
from langchain.agents import create_agent


import os
from dotenv import load_dotenv
load_dotenv()


## Arxiv and Wikipedia Tools
api_wrapper_arxiv=ArxivAPIWrapper(top_k_results=1,doc_content_chars_max=250)
arxiv=ArxivQueryRun(api_wrapper=api_wrapper_arxiv)


import wikipedia

wikipedia.set_user_agent("MyLangChainApp/1.0")
api_wrapper_wiki=WikipediaAPIWrapper(top_k_results=1,doc_content_chars_max=250)
wiki=WikipediaQueryRun(api_wrapper=api_wrapper_wiki)

search=DuckDuckGoSearchRun(name="search")

st.title("Langchain - Chat with search")


## sidebar for settings
st.sidebar.title("Settings")
api_key=st.sidebar.text_input("Enter your GROQ API key: ",type="password")


if "messages" not in st.session_state:
    st.session_state["messages"]=[
        {"role":"assistant","content":"Hi,I'm a chatbot who can search the web. How can I help you."}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg['content'])

if prompt:=st.chat_input(placeholder="What is machine learning?"):
    st.session_state.messages.append({"role":"user","content":prompt})
    st.chat_message("user").write(prompt)

    llm=ChatGroq(groq_api_key=api_key,model_name="openai/gpt-oss-safeguard-20b",streaming=True)
    tools=[search,arxiv,wiki]

    search_agent = create_agent(
    model=llm,
    tools=tools
    )

    with st.chat_message("assistant"):
        response = search_agent.invoke({
            "messages": [
            {"role": "user", "content": prompt}
            ]
        })

        answer=response["messages"][-1].content
        st.write(answer)


    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

