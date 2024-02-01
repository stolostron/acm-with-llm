## Motivation

This repo contains some prototypes to run LLM atop ACM data and explore the boundaries. These require subscription to OpenAI as explained below. 

### On ACM Search Data
ACM Search data is stored in PostgreSQL DB. A sample database content file is included [here](./data/search_load.sql).
1. Create a database in PostgreSQL. 
1. Populate the database by importing [here](./data/search_load.sql) or running the SQLs manually.
1. Follow the steps mentioned below to get a Search-LLM to run.

### On ACM Knowledge Graph Data
[Knowledge Graphs](https://github.com/stolostron/knowledge-graph) are being created for ACM to help explain and manage certain complex cases.
To see how LLMs can help answer questions from Knowledge Graphs follow the steps mentioned below.


## Important Links for Langchain/LLM

https://python.langchain.com/docs/use_cases/graph/graph_cypher_qa
https://python.langchain.com/docs/use_cases/qa_structured/sql#case-3-sql-agents
https://python.langchain.com/docs/integrations/toolkits/sql_database


## What do you need to run
### Prereq
1. Clone this repo
1. Setup venv, review the Python 3.12 and Required Linux Packages sections is using Linux.
    - `cd to the repo dir`
    - run: 
        ```
        python -m venv .venv
        source .venv/bin/activate
        pip install -r src/requirements.txt
        ```
    - run :`which python` and this show that python is being used from the venv directory
    - after all work is done, to exit the venv, just run: `deactivate`
1. Setup Argilla as explained in section [to run Argilla](README.md/#to-run-argilla)    
1. Setup and run neo4j as described in the [Knowledge Graph repository](https://github.com/stolostron/knowledge-graph/)
   - An additional step is needed from the provided instructions for neo4j.  You must enable 
     the APOC plugin which can be done by providing the following additional parameters with
     the `docker run` command:
     ```
        -e NEO4J_apoc_export_file_enabled=true \
           -e NEO4J_apoc_import_file_enabled=true \
           -e N0EO4J_apoc_import_file_use__neo4j__config=true \
           -e NEO4J_PLUGINS=\[\"apoc\"\] \
     ```
1. Copy `env-sample` to `.env` and edit the new file.
  1. Obtain an API Key token from openai.com and update the value for the `OPENAI_API_KEY` variable. **NOTE** This requires you purchase a Tier 1 rate from openai.com because the gpt-4 model is being used.  See [Open AI Rate Limits](https://platform.openai.com/docs/guides/rate-limits/usage-tiers?context=tier-one) for more details.
  1. Update your DB credentials if using the search llm.
  1. Update the `NEO4J_PASSWORD` to match the password you are using for neo4j if using the
     Knowledge Graph llm.
  1. Be aware the port for neo4j is the Bolt port that default to `7687`, not the console port.
  1. Adjust other values if necessary.
#### Python 3.12
This setup procedure is not compatible with Python 3.12 or newer.  You must install and use
Python 3.11 for the virtual environment.  See the required packages to install in the next section.  When you setup the virtual python environment, run `python3.11 -m venv .venv` so python 3.11 will be 
used instead of 3.12.
#### Required Linux Packages
If you are running Linux, make sure you have the following packages installed.
- python3.11 (if Python 3.12 is the default)
- python3.11-devel (if Pythong 3.12 is the default)
- postgresql-devel
- g++

### Search using LLM
1. Have PostgreSQL DB with search data somewhere accessible
1. Run: `streamlit run src/search_chat.py --server.port 8051`

### Knowledge Graph using LLM
1. If you want to test Knowledge Graph, follow instructions [here](https://github.com/bjoydeep/knowledge-graph?tab=readme-ov-file#to-run) to have a Neo4j docker running on your machine.
1. Run: `streamlit run src/kg_chat.py --server.port 8051`

Note - Search and Knowledge Graph are mutually exclusive. You can run anyone you want to. They do share some code as of now though.

## To run Argilla
1. Background doc: https://docs.argilla.io/en/latest/index.html#project-architecture
1. Background doc: https://docs.argilla.io/en/latest/getting_started/installation/deployments/docker-quickstart.html
1. docker network create argilla-net
1. docker run -d --network argilla-net --name quickstart -p 6900:6900 argilla/argilla-quickstart:latest

#### Key Argilla docs

1. https://python.langchain.com/docs/integrations/callbacks/argilla This is not entirely helpful. See the comments in the code etc.
1. https://api.python.langchain.com/en/latest/_modules/langchain_community/callbacks/argilla_callback.html#
1. https://github.com/langchain-ai/langchain/blob/master/libs/community/langchain_community/callbacks/argilla_callback.py#L262
1. https://docs.argilla.io/en/latest/conceptual_guides/data_model.html#
1. https://docs.argilla.io/en/latest/practical_guides/practical_guides.html

## Experimental Notebooks
Refer to the [README](./notebooks/README.md)

## Questions this can answer
Refer to [Queries](./Queries.md)


