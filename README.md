Ubuntu Package Dependency Graph
===============================

Small exercise showing the power of graph databases. It retrieves a list of debian packages available and push them to neo4j graph database.

To run
 1. clone repository
 1. install dependencies (py2neo): `pip -r requirements`
 1. `python ex.py`

If no argument is provided the program will generate the list of packages using `dpkg-query`, alternatively you can provide a list of packages in a file of json objects (check source code to get the idea of the format). The later option is useful in case you want to filter out some of the packages (e.g. not installed). 

Neo4j conneciton details can be provided through environment variable: *NEO4J_URI* (default `http://neo4j:neo@localhost:7474/db/data/`). In case you need a new instance of neo4j you are might consider using a docker image: `docker run -d -p 7474:7474 dariah/neo4j`


enjoy.
 
 

