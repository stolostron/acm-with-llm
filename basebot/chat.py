# from langchain_community.chat_models import ChatOpenAI
# from langchain.schema import AIMessage, HumanMessage
# from langchain_core.messages import HumanMessage, AIMessage
# from callback import add_record, callback
# from dotenv import load_dotenv, find_dotenv
import gradio as gr
# from langchain.prompts.chat import ChatPromptTemplate
# from langchain_community.utilities.sql_database import SQLDatabase
# from langchain_openai import OpenAI
# from langchain_openai import ChatOpenAI
# from langchain.agents.agent_types import AgentType
# from langchain_community.agent_toolkits import SQLDatabaseToolkit, create_sql_agent
import os
# from langchain.chains import create_history_aware_retriever
# from langchain_core.prompts import MessagesPlaceholder
from index import *



# Main loop to accept user input and call the ChatGPT API
def main():
	gr.ChatInterface(chat_with_gpt).launch()

# Entry point of the script
if __name__ == "__main__":
	main()
