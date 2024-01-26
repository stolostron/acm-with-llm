## Important Links for Langchain/LLM

https://python.langchain.com/docs/use_cases/graph/graph_cypher_qa
https://python.langchain.com/docs/use_cases/qa_structured/sql#case-3-sql-agents
https://python.langchain.com/docs/integrations/toolkits/sql_database


## What do you need to run
### Prereq
1. Clone this repo
1. Setup venv
    - `cd to the repo dir`
    - run: 
        ```
        python -m venv .venv
        source .venv/bin/activate
        ```
    - run :`which python` and this show that python is being used from the venv directory
    - after all work is done, to exit the venv, just run: `deactivate`
1. Setup Argilla as explained in section [to run Argilla](README.md/#to-run-argilla)    
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


