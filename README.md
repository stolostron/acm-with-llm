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
        python -m venv .ven
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
There are some experimental notebooks here. These can be ignored for now as they have not been cleaned up. They were used for self education and experimentation.


### Sample Queries for KG Chat
1. can you describe 1 hop connectivity from node with a name called KlusterletAgent.
    ```
    MATCH (n {name: 'KlusterletAgent'})-[:CREATES]->(p)
    RETURN n, p
    ```
1. can you describe what all is connected to node with a name called KlusterletAgent.
    ```
    MATCH (n {name: 'KlusterletAgent'})-[r]-(m)
    RETURN n, r, m
    ```
1. can you describe what all is connected to node with a name called KlusterletAgent. Describe all connections one by one
1. who creates the node with the name KlusterletAgent
    ```
    MATCH (u:Users)-[:CREATES]->(n)
    WHERE n.name = 'KlusterletAgent'
    RETURN u.name AS creator
    ```
1. how was node with the name KlusterletAgent created
    ```
    MATCH p=(:Users)-[*1..3]-(x)-[:CREATES]->(n)
    WHERE n.name = 'KlusterletAgent'
    RETURN p AS path
    ```
1. what are all things created by the user in a cascading fashion
    ```
    MATCH p=(:Users {name: 'user'})-[:CREATES*]->(x)
    RETURN p AS path
    ```
1. what are all things created by User in a cascading fashion
    ```
    MATCH p=(:Users)-[*1..]->(x)-[:CREATES]->(q)
    RETURN p AS path
    ```
1. What things are created by User
    ```
    MATCH (u:Users)-[:CREATES]->(n)
    RETURN n
    ``` 
1. What things are created by User. And what do these create in return
    ```
    MATCH (u:Users)-[:CREATES]->(n)
    MATCH (n)-[:CREATES]->(m)
    RETURN u.name AS User, COLLECT(DISTINCT n.name) AS CreatedThings, COLLECT(DISTINCT m.name) AS CreatedByUser
    ```   
1. what are created in namespace open-cluster-management-observability and is on hub
    ```
    MATCH (n)-[:CREATES]->(m)
    WHERE n.namespace = 'open-cluster-management-observability' AND m.onHub = 'true'
    RETURN m
    ```
1. what are created in namespace open-cluster-management-observability or has namespace set to cluster-scoped and is on hub
    ```
    MATCH (n)-[:CREATES]->(m)
    WHERE n.namespace = 'open-cluster-management-observability' OR n.onHub = 'true'
    RETURN m
    ```
1. what are created in namespace open-cluster-management-observability or cluster-scoped and is on hub
    ```
    MATCH (n)<-[:CREATES]-(m)
    WHERE (n:Processor OR n:IntermediateResource OR n:API) AND (n.namespace = 'open-cluster-management-observability' OR n.namespace = 'cluster-scoped') AND n.onHub = 'true'
    RETURN n
    ```

1. what are created in namespace open-cluster-management-observability or cluster-scoped and is on hub. Can you describe the flow step by step
    ```
    I'm sorry, but without any provided information, I don't have the necessary details to describe the flow step by step. Could you please provide more information or clarify your question?
    ```
1. what are created in namespace open-cluster-management-observability or cluster-scoped and is on hub. Can you describe the steps in details please.
    ```
    I'm sorry, but without any provided information, I don't have the necessary details to describe the steps in creating anything in the "open-cluster-management-observability" namespace or cluster-scoped on the hub. Could you please provide more information or clarify your question?
    ```
1. what are created in namespace open-cluster-management-observability or cluster-scoped and is on hub and how are created
    ```
    MATCH (n)-[:CREATES]->(m)
    WHERE (n.namespace = 'open-cluster-management-observability' OR n.namespace = 'cluster-scoped') AND n.onHub = 'true'
    RETURN n, m
    ```

1. Putting a question mark or full stop at the end of a question trips the question being answered all together.

1. what gets created n namespace open-cluster-management-observability or cluster-scoped and is on hub and who creates them
    ```
    MATCH (u:Users)-[:CREATES]->(n)
    WHERE n.namespace = "open-cluster-management-observability" OR n.namespace = "cluster-scoped"
    AND n.onHub = "true"
    RETURN n, u
    ```
1. do we have anything called GRAFANA - ignore the case please. Can you decsribe how is it created

    ```
    Yes, we have something called Grafana. It is created by the MulticlusterObservabilityOperator, which is a controller that watches the Custom Resource called MCO-CR. The MulticlusterObservabilityOperator is located in the namespace 'open-cluster-management' and is created by the User. Grafana itself is a Pod and is located in the namespace 'open-cluster-management-observability'.
    
    MATCH p=(:Users)-[*1..3]-(x)-[:CREATES]->(q:Processor)
    WHERE toLower(q.name) = 'grafana'
    RETURN p AS path
    ```
1. what are created in namespace open-cluster-management-agent-addon

    ```
    I'm sorry, but I don't have the information about what is created in the namespace open-cluster-management-agent-addon.

    MATCH (n:IntermediateResource)<-[:CREATES]-(m)
    WHERE n.namespace = 'open-cluster-management-agent-addon'
    RETURN m

    ```
1. 


