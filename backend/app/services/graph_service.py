from neo4j import GraphDatabase
from typing import Dict, List

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

        with self.driver.session() as session:

            # --------------------------------------------------
            # Repository node
            # --------------------------------------------------
            repo_res = session.run(
                """
                MATCH (r:Repository {id:$repo_id})
                RETURN r.id AS id, r.name AS name
                """,
                repo_id=repo_id
            ).single()

            if not repo_res:
                return {"nodes": [], "links": []}

            repo_node = f"repo_{repo_id}"

            nodes[repo_node] = {
                "id": repo_node,
                "label": repo_res["name"],
                "type": "repository"
            }

            # --------------------------------------------------
            # Get Topics + Contributors
            # --------------------------------------------------
            q = """
            MATCH (c:Contributor {repo_id:$repo_id})
                -[:EXPERT_IN]->
                (t:Topic)

            RETURN
                t.name AS topic,
                c.id AS contributor_id,
                c.username AS contributor_name

            ORDER BY t.name, c.username
            """

            results = session.run(q, repo_id=repo_id)

            topic_map = {}

            for rec in results:
                topic = rec["topic"]

                if topic not in topic_map:
                    topic_map[topic] = []

                topic_map[topic].append({
                    "id": rec["contributor_id"],
                    "username": rec["contributor_name"]
                })

            # --------------------------------------------------
            # Limit topics
            # --------------------------------------------------
            selected_topics = sorted(topic_map.keys())[:10]

            for topic in selected_topics:

                topic_node = f"topic_{topic}"

                nodes[topic_node] = {
                    "id": topic_node,
                    "label": topic,
                    "type": "topic"
                }

                # Repository -> Topic
                links.append({
                    "source": repo_node,
                    "target": topic_node,
                    "type": "topic_of"
                })

                # --------------------------------------------------
                # Top contributors for this topic
                # --------------------------------------------------
                contributors = topic_map[topic][:10]

                for contributor in contributors:

                    contributor_node = (
                        f"contributor_{contributor['id']}"
                    )

                    if contributor_node not in nodes:
                        nodes[contributor_node] = {
                            "id": contributor_node,
                            "label": contributor["username"],
                            "type": "contributor"
                        }

                    links.append({
                        "source": topic_node,
                        "target": contributor_node,
                        "type": "expert_in"
                    })

        return {
            "nodes": list(nodes.values()),
            "links": links
        }

    def get_graph_for_contributor(self, contributor_id: int, repo_id: int) -> Dict:
        query = """
            MATCH (c:Contributor {id:$contributor_id, repo_id: $repo_id})

            OPTIONAL MATCH (c)-[:EXPERT_IN]->(t:Topic)

            OPTIONAL MATCH (c)-[:CO_WORKED_WITH]-(other:Contributor)

            OPTIONAL MATCH (c)-[:CONTRIBUTED_TO]->(:File)-[:PART_OF]->(r:Repository)

            RETURN
                c,
                collect(DISTINCT t) AS topics,
                collect(DISTINCT other) AS collaborators,
                collect(DISTINCT r) AS repos
        """

        with self.driver.session() as session:

            result = session.run(
                query,
                contributor_id=contributor_id,
                repo_id=repo_id
            ).single()

        if not result:
            return {
                "nodes": [],
                "links": []
            }

        contributor = result["c"]
        topics = result["topics"]
        collaborators = result["collaborators"]
        repos = result["repos"]

        nodes = []
        links = []

        contributor_node_id = (
            f"contributor_{contributor['id']}"
        )

        nodes.append({
                "id": contributor_node_id,
                "label": contributor["username"],
                "type": "contributor",
            }
        )

        for repo in repos:
            if repo is None:
                continue
            repo_node_id = f"repo_{repo['id']}"
            nodes.append({
                    "id": repo_node_id,
                    "label": repo["name"],
                    "type": "repository",
                }
            )

            links.append({
                    "source": repo_node_id,
                    "target": contributor_node_id,
                }
            )

        # --------------------------
        # Topics
        # --------------------------

        for topic in topics:
            if topic is None:
                continue
            topic_id = (
                f"topic_{topic['name']}"
            )
            nodes.append({
                    "id": topic_id,
                    "label": topic["name"],
                    "type": "topic",
                }
            )

            links.append({
                    "source": contributor_node_id,
                    "target": topic_id,
                }
            )

        # --------------------------
        # Collaborators
        # --------------------------

        for collaborator in collaborators:
            if collaborator is None:
                continue
            collaborator_id = (
                f"collaborator_{collaborator['id']}"
            )

            nodes.append({
                    "id": collaborator_id,
                    "label": collaborator["username"],
                    "type": "contributor",
                }
            )

            links.append({
                    "source": contributor_node_id,
                    "target": collaborator_id,
                }
            )

        return {
            "nodes": nodes,
            "links": links,
        }

    def repository_exists(self, repo_name):
        query = """
        MATCH (r:Repository {name:$repo_name})
        RETURN count(r) > 0 AS exists
        """

        with self.driver.session() as session:
            result = session.run(
                query,
                repo_name=repo_name
            ).single()

            return bool(result["exists"])

    def delete_repository_graph(self, repo_id: int):
        query = """
        MATCH (n)
        WHERE
            (n:Contributor AND n.repo_id = $repo_id)
            OR
            (n:File AND n.repo_id = $repo_id)
            OR
            (n:Repository AND n.id = $repo_id)

        DETACH DELETE n
        """

        with self.driver.session() as session:
            session.run(query, repo_id=repo_id)