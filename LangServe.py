from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langserve import add_routes

import os
from dotenv import load_dotenv
load_dotenv()

model=ChatGroq(model="openai/gpt-oss-safeguard-20b")

### Prompt Template

generic_template="Translate the following text into {language}:"
prompt=ChatPromptTemplate.from_messages(
    [("system",generic_template),("user","{text}")]
)

### Parser

parser=StrOutputParser()

### create Chain

chain=prompt|model|parser

### APP defination

app=FastAPI(title="langchain-Server",
            version=1.0,
            description="This is a simple API server using langchain runnable interfaces")


### Adding Chain routes
add_routes(
    app,
    chain,
    path='/chain'
)

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="localhost",port=8000)