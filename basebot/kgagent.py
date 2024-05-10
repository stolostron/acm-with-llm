import os
#import openai
from dotenv import load_dotenv, find_dotenv
from langchain.llms import OpenAI
from langchain.chains import GraphCypherQAChain
from langchain.chat_models import ChatOpenAI
from langchain.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate

from langchain.callbacks import ArgillaCallbackHandler, StdOutCallbackHandler



_ = load_dotenv(find_dotenv()) 
#openai.api_key  = os.getenv('OPENAI_API_KEY')
API_KEY = os.getenv('OPENAI_API_KEY')
NEO4J_PASSWORD=os.getenv('NEO4J_PASSWORD')
NEO4J_URL=os.getenv('NEO4J_URL')
NEO4J_DB=os.getenv('NEO4J_DB')


print(NEO4J_URL, NEO4J_PASSWORD)



def chat_with_gpt_kg(message, history):
    print("In chat with KG ")

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
    
    Note: Do not include any explanations or apologies in your responses.
    Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
    Do not include any text except the generated Cypher statement.


    The question is:
    {question}"""

    CYPHER_GENERATION_PROMPT = PromptTemplate(
        input_variables=["schema", "question"], template=CYPHER_GENERATION_TEMPLATE
    )

    llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0)
    # chain = GraphCypherQAChain.from_llm(
    #     ChatOpenAI(temperature=0), graph=graph, verbose=True,validate_cypher=True,
    #     cypher_prompt=CYPHER_GENERATION_PROMPT
    # )

    chain = GraphCypherQAChain.from_llm(
        llm, graph=graph, verbose=True,validate_cypher=True,
        cypher_prompt=CYPHER_GENERATION_PROMPT
    )

    response = chain.invoke(message)
    # Return the generated response
    print("Question: ",message)
    print("Response from KG=====")
    #print(type(response))
    print(response)
    return response

    