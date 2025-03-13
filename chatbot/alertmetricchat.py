from langchain_community.chat_models import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from langchain_core.messages import HumanMessage, AIMessage
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


_ = load_dotenv(find_dotenv()) 
API_KEY = os.getenv('OPENAI_API_KEY')
DBPASS=os.getenv('DB_PASS')
DATABASE=os.getenv('DATABASE')
SCHEMA=os.getenv('SCHEMA')
OPENAI_MODEL=os.getenv('OPENAI_MODEL')

llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0)#gpt-3.5-turbo
print("Using ", OPENAI_MODEL , "to answer questions")


db = SQLDatabase.from_uri(
    f"postgresql+psycopg2://postgres:{DBPASS}@localhost:5432/{DATABASE}", schema='search'
)
toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0))


# Main function to interact with the ChatGPT API
def chat_with_gpt(message, history):
	print("In chat_with_gpt ")
	final_prompt = ChatPromptTemplate.from_messages([
    ("system", '''You are a helpful AI assistant expert in querying SQL Database to find answers to user's question about alerts, metrics etc. 
    Any questions on alerts and metrics should use alerts, metrics and amedges tables. amedges table stores information on the metrics used by each alert. 
    Join on alerts.name=amedge.sourceid OR metrics.name=amedges.destid. 
    Execute the final query and show me the results in the output. If you don't know - say I don't know.'''),
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
	agent_executor = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
	    agent_executor_kwargs={"return_intermediate_steps": True, "intermediate_steps":['Action','Action Input', 'Observation']}
	)
	
	retriever_chain = create_history_aware_retriever(llm, agent_executor, prompt)
	
	chat_history = history_langchain_format
	
	# Call the OpenAI API to get a response based on the user's prompt
	response = retriever_chain.invoke({
	    "chat_history": chat_history,
	    "input": final_prompt.format(input=message)
	})
	write_to_file(chat_history, final_prompt.format(input=message), message, response)
# 	add_record(final_prompt.format(input=message), response['output'],dataset) #this works
	# Return the generated response
	return response['output']

def write_to_file(chat_history, input, message, response):
	exists = os.path.exists('alertgptIO.tsv')
	f = open("alertgptIO.tsv", "a")
	try:
	    if not exists:
	        f.write("chat_history"+"|"+"input"+"|"+"intermediate_steps"+"|"+"response"+"|"+"message"+"|"+"output"+"\n")
	    chat_history = " ".join(str(element) for element in chat_history)
	    intermediate_steps=" ".join(str(v) for v in response["intermediate_steps"])
	    f.write(chat_history+"|"+input+"|"+intermediate_steps+"|"+str(response)+"|"+message+"|"+response['output']+"\n\n")
# 	    print(chat_history+"|"+input+"|"+intermediate_steps+"|"+str(response)+"|"+response['output']+"\n")
	except Exception as error:
	    print("chat_history: ", type(chat_history), chat_history) 
	    print("input: ", type(input), input) 
	    print("response: ", type(response), response) 
	    print("response['output']: ", type(response['output']) ,response['output']) 
	    print("intermediate_steps:", intermediate_steps)
	    print("could not write to file", type(error).__name__, "–", error)
	f.close()


# Main loop to accept user input and call the ChatGPT API
def main():
	gr.ChatInterface(chat_with_gpt).launch()

# Entry point of the script
if __name__ == "__main__":
	main()
