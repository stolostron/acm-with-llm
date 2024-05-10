
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from langchain_core.messages import HumanMessage, AIMessage
#from callback import add_record, callback
from dotenv import load_dotenv, find_dotenv
#import gradio as gr
from langchain.prompts.chat import ChatPromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
import os
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
#import openai
from kgagent import *
from sqlagent import *

from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
)



_ = load_dotenv(find_dotenv()) 
#openai.api_key  = os.getenv('OPENAI_API_KEY')
API_KEY = os.getenv('OPENAI_API_KEY')

#gpt-3.5-turbo
llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)

def chat_with_gpt(message, history):
	
    print("Calling Index module ")
    #qintent = route_question(llm=llm, query=message)
    qintent = get_completion(message)
    print("qintent: ", qintent)


    if qintent == "Changes":
        response= chat_with_gpt_search(message, history)
        print("response from router: ", response)
        print(type(response))
        return response
    elif qintent == "KG":
        response= chat_with_gpt_kg(message, history)
        print("response from router: ", response)
        print(type(response))
        return response['result']



def route_question(llm,query):
    print("In route_question")
    return "Changes"
    #return "KG"

def get_completion(message):

    examples = [
        {"input": "where there any changes around policies y", "output": "Changes"},
        {"input": "what changed around cluster x", "output": "Changes"},
        {"input": "did anythig change around cluster or policy", "output": "Changes"},
        {"input": "did anythig change around policy x in the last 2 days", "output": "Changes"},
        {"input": "Which objects are related to policy x", "output": "KG"},
        {"input": "what objects will be affected if I make changes to policy x", "output": "KG"},
        {"input": "is there any relation between policy x and cluster y", "output": "KG"},
        {"input": "what things will be affected if I make changes to policy x", "output": "KG"},
    ]
    
    # This is a prompt template used to format each individual example.
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )
    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert at parsing the query and categorizing it to Changes or KG. If not clear or does not fall into any of the above categories, categorize it as Unknown. Just return the category like Changes or KG or Unknown. Nothing else is to be returned."),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )
    output_parser = StrOutputParser()
    chain = final_prompt | llm | output_parser
    response = chain.invoke(input=message)
    return response

"""     
def get_completion(message):
    
    prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert at parsing the query and categorizing it to Changes or KG or Unknown. If the question is around changes to policies or clusters, categorize it as Changes. If the question is around relationships between entities, categorize it as KG. If the question is not clear or does not fall into any of the above categories, categorize it as Unknown. Just return the category like Changes or KG or Unknown. Nothing else is to be returned"),
    ("user", "{input}")
    ])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    
    response = chain.invoke(input=message)


    return response
 """
