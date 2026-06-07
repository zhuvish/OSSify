from sqlalchemy import text
from backend.app.db.postgres import SessionLocal
from backend.app.services.graph_service import GraphService
from backend.app.models.contributor_expertise import ContributorExpertise
from backend.app.models.commit import Commit
from collections import defaultdict

TOPIC_RULES = {

    # ==================================
    # AUTHENTICATION & AUTHORIZATION
    # ==================================
    "auth": "Authentication",
    "login": "Authentication",
    "logout": "Authentication",
    "oauth": "Authentication",
    "oidc": "Authentication",
    "jwt": "Authentication",
    "token": "Authentication",
    "session": "Authentication",
    "permission": "Authorization",
    "role": "Authorization",
    "rbac": "Authorization",
    "access": "Authorization",

    # ==================================
    # SECURITY
    # ==================================
    "security": "Security",
    "crypto": "Security",
    "encrypt": "Security",
    "decrypt": "Security",
    "cipher": "Security",
    "hash": "Security",
    "sign": "Security",
    "signer": "Security",
    "signature": "Security",
    "xss": "Security",
    "csrf": "Security",
    "cors": "Security",
    "vulnerability": "Security",

    # ==================================
    # ROUTING / API
    # ==================================
    "route": "Routing",
    "router": "Routing",
    "blueprint": "Routing",
    "endpoint": "API",
    "api": "API",
    "rest": "API",
    "graphql": "API",
    "request": "API",
    "response": "API",
    "handler": "API",

    # ==================================
    # DATABASE
    # ==================================
    "db": "Database",
    "database": "Database",
    "sql": "Database",
    "postgres": "Database",
    "mysql": "Database",
    "sqlite": "Database",
    "mongodb": "Database",
    "migration": "Database",
    "schema": "Database",
    "query": "Database",
    "orm": "Database",
    "model": "Database",

    # ==================================
    # FRONTEND
    # ==================================
    "frontend": "Frontend",
    "ui": "Frontend",
    "ux": "Frontend",
    "component": "Frontend",
    "page": "Frontend",
    "layout": "Frontend",
    "react": "Frontend",
    "vue": "Frontend",
    "angular": "Frontend",
    "svelte": "Frontend",
    "tailwind": "Frontend",
    "css": "Frontend",
    "html": "Frontend",

    # ==================================
    # BACKEND
    # ==================================
    "backend": "Backend",
    "service": "Backend",
    "controller": "Backend",
    "middleware": "Backend",
    "application": "Backend",
    "app": "Backend",
    "server": "Backend",
    "worker": "Backend",

    # ==================================
    # TESTING
    # ==================================
    "test": "Testing",
    "tests": "Testing",
    "pytest": "Testing",
    "junit": "Testing",
    "mock": "Testing",
    "fixture": "Testing",
    "integration": "Testing",
    "unit": "Testing",
    "coverage": "Testing",

    # ==================================
    # DOCUMENTATION
    # ==================================
    "docs": "Documentation",
    "doc": "Documentation",
    "readme": "Documentation",
    "guide": "Documentation",
    "tutorial": "Documentation",
    "examples": "Documentation",
    "changelog": "Documentation",
    "changes": "Documentation",

    # ==================================
    # DEVOPS / INFRA
    # ==================================
    "docker": "DevOps",
    "kubernetes": "DevOps",
    "helm": "DevOps",
    "terraform": "DevOps",
    "ansible": "DevOps",
    "infra": "DevOps",
    "deployment": "DevOps",
    "deploy": "DevOps",
    "nginx": "DevOps",
    "apache": "DevOps",

    # ==================================
    # CI/CD
    # ==================================
    "workflow": "CI/CD",
    "github": "CI/CD",
    "actions": "CI/CD",
    "jenkins": "CI/CD",
    "gitlab": "CI/CD",
    "pipeline": "CI/CD",
    "circleci": "CI/CD",
    "travis": "CI/CD",
    "yaml": "CI/CD",
    "yml": "CI/CD",

    # ==================================
    # CLOUD
    # ==================================
    "aws": "Cloud",
    "gcp": "Cloud",
    "azure": "Cloud",
    "lambda": "Cloud",
    "s3": "Cloud",
    "cloud": "Cloud",

    # ==================================
    # DATA ENGINEERING
    # ==================================
    "spark": "Data Engineering",
    "hadoop": "Data Engineering",
    "etl": "Data Engineering",
    "airflow": "Data Engineering",
    "pipeline": "Data Engineering",

    # ==================================
    # MACHINE LEARNING
    # ==================================
    "ml": "Machine Learning",
    "model": "Machine Learning",
    "training": "Machine Learning",
    "inference": "Machine Learning",
    "tensorflow": "Machine Learning",
    "pytorch": "Machine Learning",
    "sklearn": "Machine Learning",
    "dataset": "Machine Learning",

    # ==================================
    # AI / LLM
    # ==================================
    "llm": "AI",
    "rag": "AI",
    "embedding": "AI",
    "prompt": "AI",
    "openai": "AI",
    "langchain": "AI",
    "vector": "AI",
    "qdrant": "AI",

    # ==================================
    # MESSAGING
    # ==================================
    "kafka": "Messaging",
    "rabbitmq": "Messaging",
    "queue": "Messaging",
    "pubsub": "Messaging",
    "consumer": "Messaging",
    "producer": "Messaging",

    # ==================================
    # OBSERVABILITY
    # ==================================
    "monitor": "Observability",
    "metrics": "Observability",
    "logging": "Observability",
    "log": "Observability",
    "tracing": "Observability",
    "prometheus": "Observability",
    "grafana": "Observability",

    # ==================================
    # PERFORMANCE
    # ==================================
    "cache": "Performance",
    "redis": "Performance",
    "optimization": "Performance",
    "benchmark": "Performance",
    "performance": "Performance",

    # ==================================
    # SERIALIZATION
    # ==================================
    "serializer": "Serialization",
    "serialize": "Serialization",
    "deserializer": "Serialization",
    "marshal": "Serialization",
    "json": "Serialization",
    "yaml": "Serialization",
    "pickle": "Serialization",

    # ==================================
    # PACKAGE / BUILD
    # ==================================
    "setup": "Build System",
    "build": "Build System",
    "package": "Build System",
    "requirements": "Build System",
    "poetry": "Build System",
    "npm": "Build System",
    "gradle": "Build System",
    "maven": "Build System",

    # ==================================
    # CLI
    # ==================================
    "cli": "CLI",
    "command": "CLI",
    "argparse": "CLI",
    "click": "CLI",
    "terminal": "CLI",

    # ==================================
    # WEB FRAMEWORK
    # ==================================
    "flask": "Web Framework",
    "django": "Web Framework",
    "fastapi": "Web Framework",
    "express": "Web Framework",
    "spring": "Web Framework",

    # ==================================
    # FILE SYSTEM
    # ==================================
    "file": "File Handling",
    "filesystem": "File Handling",
    "storage": "File Handling",
    "upload": "File Handling",
    "download": "File Handling",
}

def build_graph(repo_id: int):

    db = SessionLocal()

    graph = GraphService()
    print(f"Clearing existing graph for repo {repo_id}...")
    graph.delete_repository_graph(repo_id)

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
    AND c.repo_id = :repo_id
    """

    rows = db.execute(text(query), {"repo_id": repo_id}).fetchall()

    print(f"Fetched {len(rows)} rows from PostgreSQL")

    count = 0

    contributor_topics = defaultdict(set)
    repo_contributors = set()

    for row in rows:

        contributor_id = row.contributor_id
        username = row.username
        filename = row.filename
        repo_id = row.repo_id
        repo_name = row.repo_name
        repo_contributors.add(contributor_id)

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

        filename_lower = (filename or "").lower()

        for keyword, topic in TOPIC_RULES.items():

            if keyword in filename_lower:
                contributor_topics[contributor_id].add(topic)

        count += 1

        if count % 100 == 0:
            print(f"Processed {count} rows...")

    for contributor_id, topics in contributor_topics.items():

        for topic in topics:

            graph.create_topic(topic)

            graph.contributor_expert_in(
                contributor_id=contributor_id,
                repo_id=repo_id,
                topic_name=topic
            )

    DOMAIN_TO_TOPIC = {
        "backend": "Backend",
        "frontend": "Frontend",
        "testing": "Testing",
        "documentation": "Documentation",
        "database": "Database",
        "devops": "DevOps",
    }

    expertise_rows = (
        db.query(ContributorExpertise)
        .filter(
            ContributorExpertise.contributor_id.in_(
                repo_contributors
            )
        )
        .all()
    )

    for exp in expertise_rows:

        topic_name = DOMAIN_TO_TOPIC.get(
            exp.domain.lower()
        )

        if not topic_name:
            continue

        graph.create_topic(topic_name)

        graph.contributor_expert_in(
            contributor_id=exp.contributor_id,
            repo_id=repo_id,
            topic_name=topic_name
        )

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
        AND c1.repo_id = :repo_id
    """

    collab_rows = db.execute(text(collab_query), {"repo_id": repo_id}).fetchall()

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