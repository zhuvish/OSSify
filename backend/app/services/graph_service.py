from neo4j import GraphDatabase

class GraphService:

    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "password")
        )

    def close(self):
        self.driver.close()

    def create_contributor(self, contributor_id, username, repo_id, repo_name):

        query = """
        MERGE (c:Contributor {
            id: $id,
            repo_id: $repo_id
        })
        SET c.username = $username
        SET c.repo_name = $repo_name
        """

        with self.driver.session() as session:
            session.run(
                query,
                id=contributor_id,
                username=username,
                repo_id=repo_id,
                repo_name=repo_name
            )

    def create_repository(self, repo_id, repo_name):

        query = """
        MERGE (r:Repository {id: $id})
        SET r.name = $name
        """

        with self.driver.session() as session:
            session.run(
                query,
                id=repo_id,
                name=repo_name
            )

    def create_file(self, filename, repo_id):

        query = """
       MERGE (f:File {
            path: $path,
            repo_id: $repo_id
        })
        """

        with self.driver.session() as session:
            session.run(
                query, 
                path=filename,
                repo_id=repo_id
            )

    def contributor_modified_file(
        self,
        contributor_id,
        filename,
        repo_id
    ):

        query = """
        MATCH (c:Contributor {
            id: $contributor_id,
            repo_id: $repo_id
        })

        MATCH (f:File {
            path: $filename,
            repo_id: $repo_id
        })

        MERGE (c)-[:CONTRIBUTED_TO]->(f)
        """

        with self.driver.session() as session:
            session.run(
                query,
                contributor_id=contributor_id,
                filename=filename,
                repo_id=repo_id
            )

    def file_part_of_repo(
        self,
        filename,
        repo_id
    ):

        query = """
        MATCH (f:File {path: $filename})
        MATCH (r:Repository {id: $repo_id})

        MERGE (f)-[:PART_OF]->(r)
        """

        with self.driver.session() as session:
            session.run(
                query,
                filename=filename,
                repo_id=repo_id
            )

    def contributors_work_together(
        self,
        contributor1,
        contributor2,
        repo_id
    ):

        query = """
        MATCH (c1:Contributor {
            id: $contributor1,
            repo_id: $repo_id
        })

        MATCH (c2:Contributor {
            id: $contributor2,
            repo_id: $repo_id
        })

        MERGE (c1)-[:CO_WORKED_WITH]->(c2)
        """

        with self.driver.session() as session:
            session.run(
                query,
                contributor1=contributor1,
                contributor2=contributor2,
                repo_id=repo_id
            )

    def contributors_work_together(
        self,
        contributor1,
        contributor2,
        repo_id
    ):

        query = """
        MATCH (c1:Contributor {
            id: $contributor1,
            repo_id: $repo_id
        })

        MATCH (c2:Contributor {
            id: $contributor2,
            repo_id: $repo_id
        })

        MERGE (c1)-[:CO_WORKED_WITH]->(c2)
        """

        with self.driver.session() as session:
            session.run(
                query,
                contributor1=contributor1,
                contributor2=contributor2,
                repo_id=repo_id
            )

    def create_topic(self, topic_name):

        query = """
        MERGE (t:Topic {
            name: $topic_name
        })
        """

        with self.driver.session() as session:
            session.run(
                query,
                topic_name=topic_name
            )

    def contributor_expert_in(
        self,
        contributor_id,
        repo_id,
        topic_name
    ):

        query = """
        MATCH (c:Contributor {
            id:$contributor_id,
            repo_id:$repo_id
        })

        MATCH (t:Topic {
            name:$topic_name
        })

        MERGE (c)-[:EXPERT_IN]->(t)
        """

        with self.driver.session() as session:
            session.run(
                query,
                contributor_id=contributor_id,
                repo_id=repo_id,
                topic_name=topic_name
            )

    def get_graph_for_repo(self, repo_id: int):
        nodes = {}
        links = []

        # Get repository node
        with self.driver.session() as session:
            repo_res = session.run(
                "MATCH (r:Repository {id:$repo_id}) RETURN r.name AS name, r.id AS id",
                repo_id=repo_id
            ).single()

            if repo_res:
                rid = repo_res["id"]
                rname = repo_res["name"]
                nodes[f"repo_{rid}"] = {"id": f"repo_{rid}", "label": rname, "type": "repository"}

            # Contributor -> Topic edges
            q1 = """
            MATCH (c:Contributor {repo_id:$repo_id})-[e:EXPERT_IN]->(t:Topic)
            RETURN c.id AS cid, c.username AS username, t.name AS topic
            """
            for rec in session.run(q1, repo_id=repo_id):
                cid = rec["cid"]
                username = rec["username"]
                topic = rec["topic"]

                cnode = f"contributor_{cid}"
                tnode = f"topic_{topic}"

                if cnode not in nodes:
                    nodes[cnode] = {"id": cnode, "label": username or str(cid), "type": "contributor"}
                if tnode not in nodes:
                    nodes[tnode] = {"id": tnode, "label": topic, "type": "topic"}

                links.append({"source": cnode, "target": tnode, "type": "expert_in"})

            # Topic -> Repository edges: topics that appear in this repo
            q2 = """
            MATCH (t:Topic)
            WHERE exists((:Contributor {repo_id:$repo_id})-[:EXPERT_IN]->(t))
            RETURN t.name AS topic
            """
            for rec in session.run(q2, repo_id=repo_id):
                topic = rec["topic"]
                tnode = f"topic_{topic}"
                if tnode in nodes and f"repo_{repo_id}" in nodes:
                    links.append({"source": tnode, "target": f"repo_{repo_id}", "type": "topic_of"})

            # Contributor -> File edges, limited to avoid overloading the graph
            q_files = """
            MATCH (c:Contributor {repo_id:$repo_id})-[:CONTRIBUTED_TO]->(f:File {repo_id:$repo_id})
            WITH c, f
            LIMIT 5
            RETURN c.id AS cid, c.username AS username, f.path AS filepath
            """
            for rec in session.run(q_files, repo_id=repo_id):
                cid = rec["cid"]
                username = rec["username"]
                filepath = rec["filepath"]

                contributor_node = f"contributor_{cid}"
                file_node = f"file_{filepath}"

                if contributor_node not in nodes:
                    nodes[contributor_node] = {
                        "id": contributor_node,
                        "label": username or str(cid),
                        "type": "contributor"
                    }

                if file_node not in nodes:
                    nodes[file_node] = {
                        "id": file_node,
                        "label": filepath.split("/")[-1],
                        "type": "file"
                    }

                links.append({
                    "source": contributor_node,
                    "target": file_node,
                    "type": "modified"
                })

            # File -> Repository edges
            q_repo_files = """
            MATCH (f:File {repo_id:$repo_id})-[:PART_OF]->(r:Repository {id:$repo_id})
            RETURN f.path AS filepath
            """
            for rec in session.run(q_repo_files, repo_id=repo_id):
                filepath = rec["filepath"]
                file_node = f"file_{filepath}"
                if file_node in nodes and f"repo_{repo_id}" in nodes:
                    links.append({
                        "source": file_node,
                        "target": f"repo_{repo_id}",
                        "type": "part_of"
                    })

            # Co-work edges between contributors
            q3 = """
            MATCH (c1:Contributor {repo_id:$repo_id})-[co:CO_WORKED_WITH]-(c2:Contributor {repo_id:$repo_id})
            RETURN c1.id AS c1, c2.id AS c2
            """
            for rec in session.run(q3, repo_id=repo_id):
                c1 = rec["c1"]
                c2 = rec["c2"]
                n1 = f"contributor_{c1}"
                n2 = f"contributor_{c2}"
                if n1 not in nodes:
                    nodes[n1] = {"id": n1, "label": str(c1), "type": "contributor"}
                if n2 not in nodes:
                    nodes[n2] = {"id": n2, "label": str(c2), "type": "contributor"}
                links.append({"source": n1, "target": n2, "type": "co_worked"})

        return {"nodes": list(nodes.values()), "links": links}