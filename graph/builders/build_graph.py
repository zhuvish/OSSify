from sqlalchemy import text
from backend.app.db.postgres import SessionLocal
from backend.app.services.graph_service import GraphService

TOPIC_RULES = {
    "session": "Sessions",
    "auth": "Authentication",
    "login": "Authentication",
    "security": "Security",
    "cli": "CLI",
    "blueprint": "Routing",
    "route": "Routing",
    "request": "Request Lifecycle",
    "app": "Application Core",
    "auth": "Authentication",
    "oauth": "Authentication",
    "jwt": "Authentication",
    "router": "Routing",
    "route": "Routing",
    "db": "Database",
    "sql": "Database",
}

def build_graph():

    db = SessionLocal()

    graph = GraphService()

    query = """
    SELECT
        c.contributor_id,
        ctr.username,
        cf.filename,
        r.id AS repo_id,
        r.full_name AS repo_name

    FROM commits c

    JOIN commit_files cf
        ON c.id = cf.commit_id

    JOIN contributors ctr
        ON c.contributor_id = ctr.id

    JOIN repositories r
        ON c.repo_id = r.id

    WHERE c.contributor_id IS NOT NULL
    """

    rows = db.execute(text(query)).fetchall()

    print(f"Fetched {len(rows)} rows from PostgreSQL")

    count = 0

    for row in rows:

        contributor_id = row.contributor_id
        username = row.username
        filename = row.filename
        repo_id = row.repo_id
        repo_name = row.repo_name

        # Create repository node
        graph.create_repository(
            repo_id=repo_id,
            repo_name=repo_name
        )

        # Create contributor node
        graph.create_contributor(
            contributor_id=contributor_id,
            username=username,
            repo_id=repo_id,
            repo_name=repo_name
        )

        # Create file node
        graph.create_file(
            filename=filename,
            repo_id=repo_id
        )

        # Contributor -> File
        graph.contributor_modified_file(
            contributor_id=contributor_id,
            filename=filename,
            repo_id=repo_id
        )

        # File -> Repository
        graph.file_part_of_repo(
            filename=filename,
            repo_id=repo_id
        )

        filename_lower = filename.lower()

        for keyword, topic in TOPIC_RULES.items():

            if keyword in filename_lower:

                graph.create_topic(topic, )

                graph.contributor_expert_in(
                    contributor_id=contributor_id,
                    repo_id=repo_id,
                    topic_name=topic
                )

        count += 1

        if count % 100 == 0:
            print(f"Processed {count} rows...")

    collab_query = """
    SELECT DISTINCT
        c1.contributor_id AS contributor1,
        c2.contributor_id AS contributor2,
        c1.repo_id AS repo_id

    FROM commit_files cf1

    JOIN commits c1
        ON cf1.commit_id = c1.id

    JOIN commit_files cf2
        ON cf1.filename = cf2.filename

    JOIN commits c2
        ON cf2.commit_id = c2.id

    WHERE
        c1.contributor_id IS NOT NULL
        AND c2.contributor_id IS NOT NULL
        AND c1.contributor_id != c2.contributor_id
        AND c1.repo_id = c2.repo_id
    """

    collab_rows = db.execute(text(collab_query)).fetchall()

    print(f"Found {len(collab_rows)} collaboration rows")

    count = 0

    for row in collab_rows:

        graph.contributors_work_together(
            contributor1=row.contributor1,
            contributor2=row.contributor2,
            repo_id=row.repo_id
        )

        count += 1

        if count % 100 == 0:
            print(f"Built {count} collaboration edges...")


    graph.close()
    db.close()

    print("Graph build complete!")


if __name__ == "__main__":
    build_graph()