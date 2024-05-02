
## Key value prop
The example below uses:
1. 2 different agents (SQL and NeO4j) to answer the questions
1. The question has to go through a routing module which uses fewshot prompt based system to decide which agent to call based on user intent.
1. And obviously this is extendible - one of the agents could be a RAG which gets data from a document etc.

## Follow the steps in order to get this up and running
###  Run Neo4j Docker
```
(base) ➜  ~ podman  run \
        --restart always \
        --publish=7474:7474 --publish=7687:7687 \
        -e NEO4J_apoc_export_file_enabled=true \
        -e NEO4J_apoc_import_file_enabled=true \
        -e N0EO4J_apoc_import_file_use__neo4j__config=true \
        -e NEO4J_PLUGINS=\[\"apoc\"\] \
        neo4j:5.13.0-community-ubi8 
```  
### Update Neo4j
1. log into the Neo4j browser: http://localhost:7474/browser/
1. change the password 
1. update the [.env](../.env) file
1. insert this data into the Neo4j
    ```
    CREATE
      (pol1:Policy {name: 'policy-1'}),
      (pol2:Policy {name: 'policy-2'}),
      (pol3:Policy {name: 'policy-3'}),
      (pol4:Policy {name: 'policy-4'}),
      (pol5:Policy {name: 'policy-5'}),
      (polx:Policy {name: 'policy-x'}),
      (cluster1:Cluster {name: 'cluster-1', location: 'eastcoast'}),
      (cluster2:Cluster {name: 'cluster-2', location: 'westcoast'}),
      (cluster3:Cluster {name: 'cluster-3', location: 'westcoast'}),
      (cluster4:Cluster {name: 'cluster-4', location: 'northeast'}),
      (cluster5:Cluster {name: 'cluster-5', location: 'northeast'}),

      (object1:Object {name: 'object-1'}),
      (object2:Object {name: 'object-2'}),
      (object3:Object {name: 'object-3'}),
      (object4:Object {name: 'object-4'}),
      (object5:Object {name: 'object-5'}),
      (object6:Object {name: 'object-6'}),
      (object7:Object {name: 'object-7'}),
      (object8:Object {name: 'object-8'}),
      (object9:Object {name: 'object-9'}),
      (object10:Object {name: 'object-10'}),

      (pol1)-[:RUNSON]->(cluster1),
      (pol1)-[:RUNSON]->(cluster2),
      (pol2)-[:RUNSON]->(cluster2),
      (pol2)-[:RUNSON]->(cluster3),
      (pol3)-[:RUNSON]->(cluster3),
      (pol3)-[:RUNSON]->(cluster4),
      (pol4)-[:RUNSON]->(cluster4),
      (pol4)-[:RUNSON]->(cluster5),
      (pol5)-[:RUNSON]->(cluster5),
      (pol5)-[:RUNSON]->(cluster1),
      (polx)-[:RUNSON]->(cluster1),
      (pol1)-[:MANAGES]->(object1),
      (pol1)-[:MANAGES]->(object2),
      (pol2)-[:MANAGES]->(object3),
      (pol2)-[:MANAGES]->(object4),
      (pol3)-[:MANAGES]->(object5),
      (pol3)-[:MANAGES]->(object6),
      (pol4)-[:MANAGES]->(object7),
      (pol4)-[:MANAGES]->(object8),
      (pol5)-[:MANAGES]->(object9),
      (pol5)-[:MANAGES]->(object10),
      (polx)-[:MANAGES]->(object1),

      (object1)-[:ISON]->(cluster1),
      (object2)-[:ISON]->(cluster2),
      (object3)-[:ISON]->(cluster2),
      (object4)-[:ISON]->(cluster3),
      (object5)-[:ISON]->(cluster3),
      (object6)-[:ISON]->(cluster4),
      (object7)-[:ISON]->(cluster4),
      (object8)-[:ISON]->(cluster5),
      (object9)-[:ISON]->(cluster5),
      (object10)-[:ISON]->(cluster1) ;
    ```

### Get the python modules
Set up your virtualenv:
```
pip install -r basebot/requirements.txt
```

### Update your PostgreSQL DB to have this table
1. create table
    ```
    CREATE TABLE IF NOT EXISTS relation.local_policies (
        event_name text NOT NULL,
        policy_id character varying(254) NOT NULL,
        cluster_id character varying(254) NOT NULL,
        leaf_hub_name character varying(254) NOT NULL,
        message text,
        reason text,
        count integer NOT NULL DEFAULT 0,
        source jsonb,
        created_at timestamp without time zone DEFAULT now() NOT NULL,
        compliance text NOT NULL,
        CONSTRAINT local_policies_unique_constraint UNIQUE (event_name, count, created_at)
    ) ;
    ```
1. insert data
    ```
    insert into relation.local_policies values ('event1', 'policy-3', 'cluster-3', 'hub-1', 'NonCompliant; violation - limitranges [container-mem-limit-range] not found in namespace default', 'PolicyStatusSync', 1, '{ "component": "policy-status-history-sync"}', now(), 'non-compliant');
    insert into relation.local_policies values ('event1', 'policy-3', 'cluster-4', 'hub-1', 'NonCompliant; violation - limitranges [container-mem-limit-range] not found in namespace default', 'PolicyStatusSync', 1, '{ "component": "policy-status-history-sync"}', now(), 'non-compliant');
    insert into relation.local_policies values ('event1', 'policy-3', 'cluster-3', 'hub-1', 'NonCompliant; violation - limitranges [container-mem-limit-range] not found in namespace default', 'PolicyStatusSync', 1, '{ "component": "policy-status-history-sync"}', now(), 'non-compliant');
    insert into relation.local_policies values ('event1', 'policy-x', 'cluster-1', 'hub-1', 'Unknown; Policy default/policy-x was propagated', 'PolicyPropagation', 1, '{ "component": "policy-status-history-sync"}', now(), 'unknown');
    insert into relation.local_policies values ('event1', 'policy-1', 'cluster-1', 'hub-1', 'NonCompliant; violation - limitranges [container-mem-limit-range] not found in namespace default', 'PolicyStatusSync', 1, '{ "component": "policy-status-history-sync"}', now(), 'non-compliant');
    ```
    

1. update the [.env](../.env) file if needed

### Run the code
python basebot/chat.py

### Ask Questions

[Questions](QueriesIssues.md)














