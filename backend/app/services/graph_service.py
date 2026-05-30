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