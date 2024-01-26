import os
from callback import add_record, callback
#import openai
from dotenv import load_dotenv, find_dotenv
from langchain.llms import OpenAI
from langchain.chains import GraphCypherQAChain
from langchain.chat_models import ChatOpenAI
from langchain.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate
import streamlit as st
from langchain.callbacks import ArgillaCallbackHandler, StdOutCallbackHandler


st.set_page_config(page_title="LangChain: Search the Knowledge Graph", page_icon="🦜")
st.title("🦜 LangChain: Search the Knowledge Graph")


_ = load_dotenv(find_dotenv()) 
#openai.api_key  = os.getenv('OPENAI_API_KEY')
API_KEY = os.getenv('OPENAI_API_KEY')
#DBPASS=os.getenv('DBPASS')
#DATABASE=os.getenv('DATABASE')
NEO4J_PASSWORD=os.getenv('NEO4J_PASSWORD')
NEO4J_URL=os.getenv('NEO4J_URL')
NEO4J_DB=os.getenv('NEO4J_DB')
ARGILLA_API_URL=os.getenv("ARGILLA_API_URL"),
ARGILLA_API_KEY=os.getenv("ARGILLA_API_KEY"),

print(NEO4J_URL, NEO4J_PASSWORD)

dataset = callback()
argilla_callback = ArgillaCallbackHandler(
    dataset_name="langchain-dataset",
    workspace_name="admin",
    api_url=os.getenv('ARGILLA_API_URL'),
    api_key=os.getenv('ARGILLA_API_KEY')
)
#callbacks = [StdOutCallbackHandler(), argilla_callback]
callbacks = [ argilla_callback]

graph = Neo4jGraph(
    url= NEO4J_URL, username="neo4j", password=NEO4J_PASSWORD
)

# Important
# Framing the questions is important.
# If question is: how does Host change it state from booted to acmmanaged state,
# and it sees a match of label/node Host, then it will try to filter on state.
# The state values cannot be hardcoded in the cypher query provided below.
# It substitutes the state value with the variable name dynamically
CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Ignore cases of the names or nouns provided in the question.
When a noun is provided, use the noun as a variable and get the node name adjusting for case if needed.
When a name is provided, use the name as a variable but extract the labels from the schema and use that as the node labels.
When a noun is provided, use the noun as a variable and extract the labels from the schema and use that as the node labels.
When a relationship type is provided, use the relationship type as a variable and extract the relationship type from the schema and use that as the relationship type.
When a property is provided, use the property as a variable and extract the property from the schema and use that as the property.


Schema:
{schema}


Cypher examples:
# how does Host change it state from booted to acmmanaged state?
MATCH (u:Users)-[:CREATES]->(a:API) 
MATCH(t:Time)
MATCH(i:IntermediateResource)-[]-(j)
MATCH p=(a)-[:UPDATES|WATCHES*]-(p1:Processor)-[*3]-(h1:Host)-[:NEXT*]->(h2:Host)-[*3]-(p2:Processor)
RETURN a,p, u,t,i,j
# How does bare metal host get booted and brought under acm management?
MATCH (u:Users)-[:CREATES]->(a:API) 
MATCH(t:Time)
MATCH p=(a)-[:UPDATES|WATCHES*]-(p1:Processor)-[]-()-[:NEXT*]->(h:Host)-[]-()
RETURN a,p,u,t
# How does grafana get data?
MATCH p=(q:Processor)-[:QUERIES*6]->(x)
RETURN p AS path
# how does grafana query to get data?
MATCH p=(q:Processor)-[:QUERIES*6]->(x)
RETURN p AS path
# How does Grafana get created?
MATCH p=(:Users)-[*1..3]-(x)-[:CREATES]->(q:Processor)
RETURN p AS path
# How does grafana get installed?
MATCH p=(:Users)-[*1..3]-(x)-[:CREATES]->(q:Processor)
RETURN p AS path
# tell me all things that gets created in namespace open-cluster-management-observability or cluster-scoped and is on hub and who creates them
MATCH p=(u:Users)-[*3]-(n)
RETURN p







Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.


The question is:
{question}"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
)

chain = GraphCypherQAChain.from_llm(
    ChatOpenAI(temperature=0), graph=graph, verbose=True,validate_cypher=True,
    cypher_prompt=CYPHER_GENERATION_PROMPT
)



if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Are you looking for something in the Knowledge Graph?")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        #st_cb = StreamlitCallbackHandler(st.container())
        #response = agent.run(user_query, callbacks=[st_cb])
        response = chain.run(user_query,callbacks=callbacks)
        st.session_state.messages.append({"role": "assistant", "content": response})
        #add_record(user_query, response,dataset) #this works
        st.write(response)