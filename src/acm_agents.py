import os
import openai
from dotenv import load_dotenv, find_dotenv

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List, Dict,Sequence
from langchain.agents import tool
import operator
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage,BaseMessage
import re
#from typing import Sequence
#from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from langchain_community.utilities.sql_database import SQLDatabase
from langchain.prompts.chat import ChatPromptTemplate
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent

from IPython.display import Image, display
from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod
from langchain_openai import ChatOpenAI






class AgentState(TypedDict):
    #messages: Annotated[list[AnyMessage], operator.add]
    messages: Annotated[Sequence[BaseMessage], add_messages]
    task: str
    route:str
    content: str
    iteration: int
    score:int
    summary: str
    pr: str
    srch:str

ROUTER_PROMPT = """You are an expert engineer of Red Hat Advanced Cluster Management (RHACM or ACM). 
You will see the question and decide how to route it. 
If the question is about creating a ACM GRC Policy, then it will routed to the author_node.
Any other questions should be routed to the search_node. 
Therefore you will return one of the choices mentioned below as per your understanding. 
- author_node 
- search_node. 
Do not attempt to return any other things. """

AUTHOR_PROMPT = """You are an expert at writing GRC (governance risk and compliance) Policies 
for Red Hat Advanced Cluster Management (RHACM or ACM). 
You are aware of the different kind (CRDs) under apiVersion: policy.open-cluster-management.io 
and know how to use them.
You can write a ACM policy yaml given a task as below 
If a user gives you some feedback on the yaml you have produced,
process it, think through it and improve the yaml. 
And clarify each of the changes that you have made to improve.
------

{content}"""

CRITIC_PROMPT = """You are an expert at testing GRC (governance risk and compliance) Policies 
for Red Hat Advanced Cluster Management (RHACM or ACM). 
You are aware of the different kind (CRDs) under apiVersion: policy.open-cluster-management.io 
and know how to use them.
Given a policy yaml as below, you can find out the flaws in it and suggest the changes to be made point by point.
------

{content}"""

SCORER_PROMPT = """You are an expert evaluator of GRC (governance risk and compliance) Policies 
for Red Hat Advanced Cluster Management (RHACM or ACM). 
You are aware of the different kind (CRDs) under apiVersion: policy.open-cluster-management.io 
and know how to use them.
Rate the given content on a scale of 0-100 based on: 
    - Technical accuracy (50 points) 
    - Completeness (50 points) 
Provide only the numerical score as your response.
-------

{content}"""

PR_PROMPT = """In the content provided to you, there is a  GRC (governance risk and compliance) Policy 
for Red Hat Advanced Cluster Management (RHACM or ACM) definition buried.
Just output that in a nicely formatted fashion
------

{content}"""

root_nodes = ['author','search']


_ = load_dotenv(find_dotenv()) 
openai.api_key  = os.getenv('OPENAI_API_KEY')
#model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
#gpt-4o
#gpt-4o-mini
#gpt-3.5-turbo
#o1
#o3-mini
model = ChatOpenAI(model="gpt-4o", temperature=0)


def router_node(state: AgentState):

    messages = [
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=state['task'])
    ]
    
    
    response = model.invoke(messages)
    #print("---------------------: ",response.content)
    
    #route = response.content.strip().lower()
    
    #if route not in ['author_node', 'search_node']:
    # If response doesn't match expected values, route to default
    #route = random.choice(['author_node', 'search_node'])
    
    return {"route":response.content,"messages":state['task']}

def next_step(state: AgentState):
    if  state['route'] == 'author_node' :
        return 'author'
    elif state['route'] == 'search_node' :
        return 'search'
    else :
        return 'END'
    
def author_node(state: AgentState):

    i = state['iteration']
    print( "Iteration number: ",state['iteration']+1)
    
    messages = [
        SystemMessage(content=AUTHOR_PROMPT.format(content=state['task'])),
        HumanMessage(content=state['summary'])
    ]
    
    
    response = model.invoke(messages)
    
    #print("------------------------------------------")
    #state["messages"][-1].pretty_print()
    #print("------------------------------------------")
    
    return {"content": response.content,'iteration': i+1,"messages":response.content}

def critic_node(state: AgentState):
    
    content = state['content']  
    messages = [
        SystemMessage(content=CRITIC_PROMPT.format(content=content)),
        #HumanMessage(content=state['action'])
    ]
    
    response = model.invoke(messages)
    
    return {"summary": response.content,"messages":response.content}

def scorer_node(state: AgentState):

    content = state['content']  
    messages = [
        SystemMessage(content=SCORER_PROMPT.format(content=content)),
        #HumanMessage(content=state['action'])
    ]
    
    response = model.invoke(messages)
    
    return {"score": response.content,"messages":response.content}

def pr_node(state: AgentState):

    content = state['content']  
    messages = [
        SystemMessage(content=PR_PROMPT.format(content=content)),
        #HumanMessage(content=state['action'])
    ]
    
    response = model.invoke(messages)
    
    return {"pr": response.content,"messages":response.content}

def proceed(state: AgentState):
    if  state['iteration']>3 :
        return False
    else :
        return True
    
def search_node(state: AgentState):
    
    DBPASS=os.getenv('DBPASS')
    DATABASE=os.getenv('DATABASE')
    SCHEMA=os.getenv('DBUSER')
    
    print("DB Name: ",DATABASE)
    print("DB Pass: ",DBPASS)
    print("DB Schema: ",SCHEMA)

    db = SQLDatabase.from_uri(
    f"postgresql+psycopg2://postgres:{DBPASS}@localhost:5432/{DATABASE}"
    )
    toolkit = SQLDatabaseToolkit(db=db, llm=model)
   
    content = state['task']
    
    agent_executor = create_sql_agent(llm=model, toolkit=toolkit, 
                                      verbose=True, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                                      handle_parsing_errors=True)

        
    response = agent_executor.run(state['task'])
    
    #response = model.invoke(messages)
    
    return {"srch": response,"messages":response}

def process(query):
    builder = StateGraph(AgentState)
    builder.add_node("router", router_node)
    builder.add_node("author", author_node)
    builder.add_node("critic", critic_node)
    builder.add_node("scorer", scorer_node)
    builder.add_node("pullreq", pr_node)
    builder.add_node("search", search_node)
    builder.set_entry_point("router")
    builder.add_conditional_edges(
                "router",
                next_step
                )
    builder.add_edge("author", "scorer")
    builder.add_conditional_edges(
                "author",
                proceed,
                #if func returns true, go to summary_node
                {True: "critic", False: "pullreq"}
            )
    builder.add_edge("critic", "author")
    builder.add_edge("pullreq", END)
    builder.add_edge("search", END)


    with SqliteSaver.from_conn_string(":memory:") as checkpointer:
        graph = builder.compile(checkpointer=checkpointer)
        display(
            Image(
                graph.get_graph().draw_mermaid_png(
                    draw_method=MermaidDrawMethod.API,
                )
            )
        )
        thread = {"configurable": {"thread_id": "1"}}
        for s in graph.stream({
            'task': query, 'iteration':0,"summary": "no feedback yet",
        }, thread):
            #print(s)
            #print(list(s.values())[0])
            #print("----")

            state = graph.get_state(thread).values

        for message in state["messages"]:
            message.pretty_print()
        #last_message = state["messages"][0]
        #return last_message.pretty_print()