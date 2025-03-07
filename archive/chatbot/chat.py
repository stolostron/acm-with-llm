from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from langchain_core.messages import HumanMessage, AIMessage
from callback import add_record, callback
from dotenv import load_dotenv, find_dotenv
import gradio as gr
from langchain.prompts.chat import ChatPromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
import os
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_community.callbacks import ArgillaCallbackHandler
from langchain.callbacks import StdOutCallbackHandler
from langchain_community.callbacks import ArgillaCallbackHandler

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)#gpt-3.5-turbo


_ = load_dotenv(find_dotenv()) 
API_KEY = os.getenv('OPENAI_API_KEY')
DBPASS=os.getenv('DB_PASS')
DATABASE=os.getenv('DATABASE')
SCHEMA=os.getenv('SCHEMA')

db = SQLDatabase.from_uri(
    f"postgresql+psycopg2://postgres:{DBPASS}@localhost:5432/{DATABASE}", schema='search'
)
toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0))

dataset = callback()

argilla_callback = ArgillaCallbackHandler(
    dataset_name="langchain-dataset",
    workspace_name="admin",
    api_url=os.getenv('ARGILLA_API_URL'),
    api_key=os.getenv('ARGILLA_API_KEY')
)
callbacks = [StdOutCallbackHandler(), argilla_callback]

# Main function to interact with the ChatGPT API
def chat_with_gpt(message, history):
	print("In chat_with_gpt ")
	final_prompt = ChatPromptTemplate.from_messages([
    ("system", '''You are a helpful AI assistant expert in querying SQL Database to find answers to user's question about Kubernetes resources, clusters etc. 
    Utilize your kubernetes knowledge while answering questions. For ex: failing pods mean pods that are not running or have an error status like "Pending","Error","Failed","Terminating","ImagePullBackOff","CrashLoopBackOff","RunContainerError","ContainerCreating" etc.
    All resource details and key names for filters are in the jsonb column 'data' within the resources table - which is mostly 1 level deep. 
    This query will yield all the queryable properties - SELECT distinct jsonb_object_keys(jsonb_strip_nulls("data")) AS "prop" FROM resources.
    Confirm the exact key names in the 'data' column before querying.
    The types of resources are in the 'kind' key within the data column. 
    The answer set should be de-duplicated. Run the final query and get the answer. A recursive query on edges table will show all resource relationships. Limit fetching data from the tables at most to 100 rows.'''),
    ("user", "{input}")
	])
	history_langchain_format = []
	for human, ai in history[:3]:
		history_langchain_format.append(HumanMessage(content=human))
		history_langchain_format.append(AIMessage(content=ai))
		
	
	prompt = ChatPromptTemplate.from_messages([
	MessagesPlaceholder(variable_name="chat_history"),
	("user", "{input}"),
	("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation")
	])
	agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
	
	retriever_chain = create_history_aware_retriever(llm, agent_executor, prompt)
	
	chat_history = history_langchain_format
	
	# Call the OpenAI API to get a response based on the user's prompt
	response = retriever_chain.invoke({
	    "chat_history": chat_history,
	    "input": final_prompt.format(input=message)
	})
	add_record(final_prompt.format(input=message), response['output'],dataset) #this works
	# Return the generated response
	return response['output']




# Main loop to accept user input and call the ChatGPT API
def main():
	gr.ChatInterface(chat_with_gpt).launch()

# Entry point of the script
if __name__ == "__main__":
	main()
