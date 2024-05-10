## List of queries that we ran

### Scenario - 1
1. what changed around cluster-1 in last 5 hours . List by time in ascending order

1. what objects are managed by policy-1 in cluster-1

1. what objects are managed by policy-x in cluster-1

1. do we have objects that are affected by both policy-x and policy-1 in cluster-1

### Scenario - 2

1. do we have policy-5 on clusters with the location eastcoast?


1. what objects are managed by policy-5 on clusters with the location eastcoast?

1. what policies affect object-10 on clusters with the location eastcoast?



### List of issues that we need to resolve

1. This `what objects are affected by policy-5 on clusters with the location eastcoast?` did not work - but this did `what objects are managed by policy-5 on clusters with the location eastcoast`. Need to investigate

1. This `what changed around cluster-1 in last 5 hours . List by time in ascending order` has to be first query else, it just does not list - but returns the SQL query.  Need to investigate

1. Also noticed that Cypher agent sometimes:
    - translates the english to cypher correctly
    - gets the correct answer by running the cypher
    - but when converting it to english, it trips and says `no data found`.That may have been the issue with item 1.



### Not sure if these all ran
1. did any changes to policy occur for cluster-1
1. for cluster-1 was there any changes to policy
1. what objects and clusters are affected by policy-1
1. what objects are affected by policy-x in cluster-1
1. do we have objects that are affected by both policy-x ad policy-1 
1. what objects are affected by policy-1 for clusters with name cluster-1
1. what policies affect Object-1 on clusters with the name cluster-1 ? ignore all letter cases please
