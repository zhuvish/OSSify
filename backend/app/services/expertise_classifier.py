import os

EXTENSION_RULES = {
    "frontend": {"jsx", "tsx", "css", "scss", "html"},
    "backend": {"py", "java", "go", "rb", "php"},
    "database": {"sql"},
    "documentation": {"md", "rst"},
    "devops": {"yaml", "yml", "dockerfile"},
}

PATH_RULES = {
    "frontend": {
        "frontend",
        "ui",
        "components",
        "views",
        "templates",
        "static"
    },

    "backend": {
        "backend",
        "api",
        "server",
        "auth",
        "services",
        "controllers"
    },

    "testing": {
        "test",
        "tests",
        "spec",
        "pytest"
    },

    "documentation": {
        "docs",
        "documentation",
        "readme"
    },

    "devops": {
        "docker",
        "k8s",
        "kubernetes",
        "ci",
        "cd",
        "infra"
    },

    "machine_learning": {
        "ml",
        "models",
        "training",
        "inference"
    }
}


def classify_file(filename):
    filename = filename.lower()

    matched_domains = set()

    parts = filename.replace("\\", "/").split("/")

    for part in parts:
        clean_part = part.lower()

        for domain, keywords in PATH_RULES.items():
            if clean_part in keywords:
                matched_domains.add(domain)

    ext = os.path.splitext(filename)[1].replace(".", "")

    if ext:
        for domain, extensions in EXTENSION_RULES.items():
            if ext in extensions:
                matched_domains.add(domain)

    return list(matched_domains)