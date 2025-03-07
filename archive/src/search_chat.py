import os
from callback import add_record, callback
#import openai
from dotenv import load_dotenv, find_dotenv
from langchain.llms import OpenAI
from langchain.utilities import SQLDatabase
#from langchain_experimental.sql import SQLDatabaseChain
#from IPython.display import Markdown, display
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
# from langchain.agents import AgentExecutor
from langchain.agents.agent_types import AgentType
import streamlit as st
from langchain.callbacks import ArgillaCallbackHandler, StdOutCallbackHandler


st.set_page_config(page_title="LangChain: Search the fleet", page_icon="🦜")
st.title("🦜 LangChain: Search the fleet")


_ = load_dotenv(find_dotenv()) 
#openai.api_key  = os.getenv('OPENAI_API_KEY')
API_KEY = os.getenv('OPENAI_API_KEY')
DBPASS=os.getenv('DBPASS')
DATABASE=os.getenv('DATABASE')

#print(DBPASS, DATABASE)

dataset = callback()

argilla_callback = ArgillaCallbackHandler(
    dataset_name="langchain-dataset",
    workspace_name="admin",
    api_url=os.getenv('ARGILLA_API_URL'),
    api_key=os.getenv('ARGILLA_API_KEY')
)
callbacks = [StdOutCallbackHandler(), argilla_callback]

db = SQLDatabase.from_uri(
    f"postgresql+psycopg2://postgres:{DBPASS}@localhost:5432/{DATABASE}",
)
toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0))

agent = create_sql_agent(
    llm=OpenAI(temperature=0),
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    #callbacks=callbacks,
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Are you looking for something in the fleet?")

#callback()

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        #st_cb = StreamlitCallbackHandler(st.container())
        #response = agent.run(user_query, callbacks=[st_cb])
        response = agent.run(user_query,callbacks=callbacks) #this works
        st.session_state.messages.append({"role": "assistant", "content": response})
        #add_record(user_query, response,dataset) #this works
        st.write(response)