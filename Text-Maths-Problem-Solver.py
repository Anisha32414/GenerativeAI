import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_community.utilities import WikipediaAPIWrapper

import math


# ============================================================
# Load environment variables
# ============================================================

load_dotenv()


# ============================================================
# Streamlit App Configuration
# ============================================================

st.set_page_config(
    page_title="Text to Math Problem Solver and Data Search Assistant",
    page_icon="🦜"
)

st.title("Text to Math Problem Solver Using Google Gemma 2")


# ============================================================
# GROQ API KEY
# ============================================================

groq_api_key = st.sidebar.text_input(
    label="GROQ API Key",
    type="password"
)

if not groq_api_key:
    st.info("Please add your GROQ API Key to continue")
    st.stop()


# ============================================================
# Initialize LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-safeguard-20b",
    api_key=groq_api_key,
    temperature=0
)


# ============================================================
# Wikipedia Tool
# ============================================================

wikipedia_wrapper = WikipediaAPIWrapper()


@tool
def wikipedia_search(query: str) -> str:
    """
    Search Wikipedia for information about a topic.
    Use this tool when the user asks factual or knowledge-based
    questions that can be answered using Wikipedia.
    """
    return wikipedia_wrapper.run(query)


# ============================================================
# Calculator Tool
# ============================================================

@tool
def calculator(expression: str) -> str:
    """
    Calculate mathematical expressions.

    Examples:
    2 + 2
    25 * 4
    100 / 5
    sqrt(144)
    """

    try:
        allowed_names = {
            "sqrt": math.sqrt,
            "pow": pow,
            "abs": abs,
            "round": round,
            "pi": math.pi,
            "e": math.e
        }

        result = eval(
            expression,
            {"__builtins__": {}},
            allowed_names
        )

        return str(result)

    except Exception as e:
        return f"Unable to calculate the expression: {str(e)}"


# ============================================================
# Reasoning Tool
# ============================================================

reasoning_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are a mathematical and logical reasoning assistant.

Solve the following question carefully.

Requirements:
1. Understand the problem.
2. Break it into logical steps.
3. Perform calculations correctly.
4. Explain the reasoning clearly.
5. Give the final answer at the end.

Question:
{question}

Answer:
"""
)


reasoning_chain = reasoning_prompt | llm


@tool
def reasoning_tool(question: str) -> str:
    """
    Solve mathematical, logical, and reasoning-based questions
    with a detailed step-by-step explanation.
    """

    response = reasoning_chain.invoke({
        "question": question
    })

    return response.content


# ============================================================
# Initialize Agent
# ============================================================

tools = [
    wikipedia_search,
    calculator,
    reasoning_tool
]


agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
You are a helpful mathematical and knowledge assistant.

You have access to three tools:

1. wikipedia_search
   - Use this for factual information and Wikipedia searches.

2. calculator
   - Use this for numerical calculations.

3. reasoning_tool
   - Use this for mathematical and logical reasoning.

Choose the appropriate tool based on the user's question.

For mathematical problems:
- Use the calculator when numerical calculations are required.
- Use the reasoning_tool when detailed reasoning is required.
- Give a clear step-by-step explanation.

Always provide a useful final answer to the user.
"""
)


# ============================================================
# Chat History
# ============================================================

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi! I am a Math and Knowledge Assistant. I can solve mathematical problems, reasoning questions, and search Wikipedia."
        }
    ]


# ============================================================
# Display Previous Messages
# ============================================================

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# ============================================================
# Generate Response
# ============================================================

def generate_response(question):

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": question
            }
        ]
    })

    return response["messages"][-1].content


# ============================================================
# User Input
# ============================================================

question = st.text_area(
    "Enter your question",
    "A car is moving with a speed of 30 Km/hr. After an hour it starts moving with a speed of 40 Km/hr and it keeps moving with the same speed and stopped after 1 hr. What distance did it cover in the past 2 hr?"
)


# ============================================================
# Generate Answer
# ============================================================

if st.button("Find the answer"):

    if question:

        with st.spinner("Generating Response..."):

            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": question
            })

            st.chat_message("user").write(question)

            try:

                response = generate_response(question)

                # Add assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

                st.write("### Response:")
                st.success(response)

            except Exception as e:

                st.error("Something went wrong.")
                st.exception(e)

    else:

        st.warning("Please enter the question!")