import os
import sys
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
from langchain_community.document_loaders import DirectoryLoader






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

When a user asks about `OperatorPolicy`, always refer strictly to the `OperatorPolicy` resource as defined in the Open Cluster Management CRD at
https://raw.githubusercontent.com/stolostron/config-policy-controller/refs/tags/v{acm_released_version}.0/deploy/crds/policy.open-cluster-management.io_operatorpolicies.yaml
Follow the example to ensure accuracy and alignment.
```yaml
apiVersion: policy.open-cluster-management.io/v1beta1
kind: OperatorPolicy
metadata:
  name: example-operator
  labels:
    policy.open-cluster-management.io/cluster-name: "managed"
    policy.open-cluster-management.io/cluster-namespace: "managed"
spec:
  remediationAction: enforce # optional
  severity: medium # optional
  complianceType: musthave # required
  complianceConfig: # optional
    catalogSourceUnhealthy: Compliant
    DeploymentsUnavailable: NonCompliant
    UpgradesAvailable: Compliant
    DeprecationsPresent: Compliant
  operatorGroup: # optional
    name: grc-dep-group
    namespace: operator-policy-testns
    targetNamespaces:
      - operator-policy-testns
  subscription: # required
    name: example-operator
    namespace: grc-dep
    channel: alpha
    source: grc-mock-source
    sourceNamespace: olm
  upgradeApproval: Automatic # required
  removalBehavior: # optional
    operatorGroups: DeleteIfUnused
    subscriptions: Delete
    clusterServiceVersions: Delete
    customResourceDefinitions: Delete
  versions: # optional
    - example-operator.v0.36.0

```

- Do not use `ConfigurationPolicy` or any other policy types.
- Ensure compliance with the structure outlined in the CRD.
- Use the correct field names as defined in the CRD, such as `operatorGroup`, `subscription`, `remediationAction`, and `complianceType`.

If any discrepancies arise between the CRD and examples, revise and adjust the response accordingly.
Ensure that the OperatorPolicy includes all required fields, especially upgradeApproval, and subscription.
Do not mix in outdated structures, and always ensure that the response aligns with the latest specification.

You can write a ACM policy yaml given a task as below 
If a user gives you some feedback on the yaml you have produced,
process it, think through it and improve the yaml. 
And clarify each of the changes that you have made to improve.

You are an expert in writing Kubernetes YAML, with a specialization in Red Hat Advanced Cluster Management (ACM) policies.

If the following YAML is an ACM Policy resource, review and improve it by:

- Fixing syntax errors
- Improving formatting and consistency
- Ensuring it conforms to the ACM Policy CustomResourceDefinition (CRD)
- Preserving the original intent and structure

Return only the corrected YAML.

YAML:
```yaml
{yaml_content}
```
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


success = load_dotenv(find_dotenv())
if not success:
    print("⚠️ Warning: Failed to load .env file!")
    sys.exit(1)

acm_released_version = os.getenv('ACM_RELEASED_VERSION')
openai.api_key = os.getenv('OPENAI_API_KEY')
#model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
#gpt-4o
#gpt-4o-mini
#gpt-3.5-turbo
#o1
#o3-mini
model = ChatOpenAI(model="gpt-4o", temperature=0)

loader = DirectoryLoader(
    path="load_files",
)

try:
    yamlFiles = loader.load()
except FileNotFoundError as e:
    print(f"[Info] No files found in directory: '{loader.path}'. Skipping load.")
    yamlFiles = []
except Exception as e:
    print(f"An unexpected error occurred while loading files from '{loader.path}': {e}. No files were loaded.")
    yamlFiles = []

def router_node(state: AgentState):
    """
    Looks at the user question and decides which agent can handle the job.
    
    Args:
        state: The Agent State
        
    Returns:
        Updates the Agent State
    """
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
    """
    This is a conditional edge handler
    
    Args:
        state: The Agent State
        
    Returns:
        Updates the Agent State
    """    
    if  state['route'] == 'author_node' :
        return 'author'
    elif state['route'] == 'search_node' :
        return 'search'
    else :
        return 'END'
    
def author_node(state: AgentState):
    """
    Helps to create a ACM Policy. And based on the feedback it can improve the policy.
    
    Args:
        state: The Agent State
        
    Returns:
        Updates the Agent State
    """

    i = state['iteration']
    print( "Iteration number: ",state['iteration']+1)
    
    messages = [
        SystemMessage(content=AUTHOR_PROMPT.format(content=state['task'], acm_released_version=acm_released_version, yaml_content=yamlFiles)),
        HumanMessage(content=state['summary'])
    ]
    
    response = model.invoke(messages, tools=[{"type": "web_search_preview"}])
    msg = response.content[0]['text']
    
    return {"content": msg,'iteration': i+1,"messages":msg}

def critic_node(state: AgentState):
    """
    Helps to review a ACM Policy and give feedback for improvement.
    
    Args:
        state: The Agent State
        
    Returns:
        Updates the Agent State
    """    
    content = state['content']  
    messages = [
        SystemMessage(content=CRITIC_PROMPT.format(content=content)),
        #HumanMessage(content=state['action'])
    ]
    
    response = model.invoke(messages)
    
    return {"summary": response.content,"messages":response.content}

def scorer_node(state: AgentState):
    """
    Helps to score a ACM Policy. This is a stub at the moment.
    This needs to be worked on.
    
    Args:
        state: The Agent State
        
    Returns:
        Updates the Agent State
    """  
    content = state['content']  
    messages = [
        SystemMessage(content=SCORER_PROMPT.format(content=content)),
        #HumanMessage(content=state['action'])
    ]
    
    response = model.invoke(messages)
    
    return {"score": response.content,"messages":response.content}

def pr_node(state: AgentState):
    """
    Send a PR for the code being generated. This is just a stub right now.
    Implementation is missing
    
    Args:
        state: The Agent State
        
    Returns:
        Updates the Agent State
    """
    content = state['content']  
    messages = [
        SystemMessage(content=PR_PROMPT.format(content=content)),
        #HumanMessage(content=state['action'])
    ]
    
    response = model.invoke(messages)
    
    return {"pr": response.content,"messages":response.content}

def proceed(state: AgentState):
    """
    This is a conditional edge handler.
    
    Args:
        state: The Agent State
        
    Returns:
        Updates the Agent State
    """ 
    if  state['iteration']>3 :
        return False
    else :
        return True
    
def search_node(state: AgentState):
    """
    Helps to handle a ACM Search query. As of now it needs a local DB.
    But we can easily change that.
    
    Args:
        state: The Agent State
        
    Returns:
        Updates the Agent State
    """    
    DBUSER=os.getenv('DBUSER')
    DBPASS=os.getenv('DBPASS')
    DATABASE=os.getenv('DATABASE')
    DBHOST=os.getenv('DBHOST')
    DBPORT=os.getenv('DBPORT')
    DBSCHEMA=os.getenv('DBSCHEMA')
    
    print("DB Name: ",DATABASE)
    print("DB Host: ",DBHOST)
    print("DB Port: ",DBPORT)
    print("DB User: ",DBUSER)
    print("DB Schema: ",DBSCHEMA)

    db = SQLDatabase.from_uri(
    #f"postgresql+psycopg2://postgres:{DBPASS}@localhost:5432/{DATABASE}"
    f"postgresql+psycopg2://{DBUSER}:{DBPASS}@{DBHOST}:{DBPORT}/{DATABASE}",schema=DBSCHEMA
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
            print(s)
            #print(list(s.values())[0])
            print("----")

            state = graph.get_state(thread).values

        for message in state["messages"]:
            message.pretty_print()
        #last_message = state["messages"][0]
        #return last_message.pretty_print()
        