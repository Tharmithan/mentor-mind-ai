"""Monthly learning roadmap templates (Week 6 · Day 5)."""

from __future__ import annotations

MONTHLY_ROADMAPS: dict[str, list[dict]] = {
    "ai_engineer": [
        {
            "month": 1,
            "title": "Foundations",
            "topics": [
                {"name": "Python", "description": "Core syntax, OOP, virtual envs, pip", "resources": ["Real Python", "Exercism Python"]},
                {"name": "Statistics", "description": "Probability, distributions, hypothesis testing", "resources": ["StatQuest", "Khan Academy Statistics"]},
            ],
            "goals": ["Build 3 Python scripts", "Complete stats fundamentals quiz", "Set up Git + GitHub"],
            "milestone": "Pass Python + Statistics foundation assessment",
        },
        {
            "month": 2,
            "title": "Machine Learning",
            "topics": [
                {"name": "Machine Learning", "description": "Supervised/unsupervised, scikit-learn, evaluation", "resources": ["Andrew Ng ML", "Kaggle Learn"]},
            ],
            "goals": ["Train 2 classifiers on real datasets", "Understand bias-variance tradeoff", "Kaggle mini-competition entry"],
            "milestone": "Deploy a scikit-learn model via FastAPI",
        },
        {
            "month": 3,
            "title": "Deep Learning",
            "topics": [
                {"name": "Deep Learning", "description": "Neural nets, CNNs, PyTorch basics, transfer learning", "resources": ["fast.ai", "PyTorch tutorials"]},
            ],
            "goals": ["Build an image classifier", "Fine-tune a pretrained model", "Track experiments"],
            "milestone": "Complete a deep learning portfolio project",
        },
        {
            "month": 4,
            "title": "NLP & LLMs",
            "topics": [
                {"name": "NLP", "description": "Tokenization, embeddings, transformers, RAG", "resources": ["Hugging Face course", "LangChain docs"]},
            ],
            "goals": ["Build a RAG chatbot", "Evaluate LLM outputs", "Prompt engineering practice"],
            "milestone": "Ship an LLM-powered app with evaluation metrics",
        },
        {
            "month": 5,
            "title": "Production AI",
            "topics": [
                {"name": "MLOps basics", "description": "Docker, API deployment, monitoring", "resources": ["Docker docs", "MLflow"]},
                {"name": "Software design", "description": "Clean APIs, testing, CI/CD", "resources": ["FastAPI docs", "pytest"]},
            ],
            "goals": ["Containerize your best project", "Add CI pipeline", "Write model card"],
            "milestone": "Production-ready AI project on GitHub",
        },
        {
            "month": 6,
            "title": "Portfolio & Interviews",
            "topics": [
                {"name": "Portfolio", "description": "GitHub polish, README, demos", "resources": ["Portfolio examples", "Streamlit/Gradio"]},
                {"name": "Interview prep", "description": "ML system design, coding, behavioral", "resources": ["MentorMind Interview Coach", "NeetCode"]},
            ],
            "goals": ["3 polished portfolio projects", "10 mock interviews", "Resume + LinkedIn update"],
            "milestone": "Ready to apply for AI Engineer roles",
        },
    ],
    "data_scientist": [
        {
            "month": 1,
            "title": "Python & Statistics",
            "topics": [
                {"name": "Python", "description": "pandas, NumPy, data wrangling", "resources": ["Kaggle Python", "pandas docs"]},
                {"name": "Statistics", "description": "Descriptive stats, inference, A/B testing", "resources": ["StatQuest", "Think Stats"]},
            ],
            "goals": ["EDA on 2 datasets", "Stats quiz mastery"],
            "milestone": "Publish an EDA notebook on Kaggle",
        },
        {
            "month": 2,
            "title": "Machine Learning",
            "topics": [
                {"name": "Machine Learning", "description": "Regression, classification, model selection", "resources": ["Andrew Ng ML", "scikit-learn"]},
            ],
            "goals": ["End-to-end ML pipeline", "Cross-validation mastery"],
            "milestone": "Kaggle competition submission",
        },
        {
            "month": 3,
            "title": "Advanced ML & Visualization",
            "topics": [
                {"name": "Feature engineering", "description": "Encoding, selection, pipelines", "resources": ["Feature Engineering book"]},
                {"name": "Data Visualization", "description": "Matplotlib, Seaborn, Plotly, storytelling", "resources": ["Storytelling with Data"]},
            ],
            "goals": ["Dashboard with insights", "Business recommendation report"],
            "milestone": "Data story presentation",
        },
        {
            "month": 4,
            "title": "SQL & Big Data",
            "topics": [
                {"name": "SQL", "description": "Joins, window functions, query optimization", "resources": ["Mode Analytics SQL", "LeetCode SQL"]},
                {"name": "Cloud basics", "description": "Data warehouses, notebooks in cloud", "resources": ["BigQuery intro", "AWS data analytics"]},
            ],
            "goals": ["50 SQL practice problems", "Cloud notebook project"],
            "milestone": "SQL + cloud portfolio piece",
        },
        {
            "month": 5,
            "title": "Portfolio Projects",
            "topics": [
                {"name": "Capstone", "description": "Full DS project from problem to deployment", "resources": ["Kaggle datasets", "Medium/blog"]},
            ],
            "goals": ["2 end-to-end projects", "Write technical blog posts"],
            "milestone": "GitHub portfolio complete",
        },
    ],
    "mlops_engineer": [
        {
            "month": 1,
            "title": "DevOps Foundations",
            "topics": [
                {"name": "Linux & Git", "description": "CLI, branching, PRs", "resources": ["Pro Git book", "Linux Journey"]},
                {"name": "Docker", "description": "Containers, compose, images", "resources": ["Docker getting started"]},
            ],
            "goals": ["Dockerize a Python app", "Git workflow mastery"],
            "milestone": "Multi-container app with Docker Compose",
        },
        {
            "month": 2,
            "title": "ML Pipelines",
            "topics": [
                {"name": "Python for ML", "description": "Training scripts, config management", "resources": ["Hydra", "scikit-learn pipelines"]},
                {"name": "Experiment tracking", "description": "MLflow, metrics, artifacts", "resources": ["MLflow docs", "DVC"]},
            ],
            "goals": ["Reproducible training pipeline", "Tracked experiments"],
            "milestone": "MLflow project with 5+ runs",
        },
        {
            "month": 3,
            "title": "Cloud & CI/CD",
            "topics": [
                {"name": "Cloud", "description": "AWS/GCP basics, SageMaker or Vertex intro", "resources": ["AWS Cloud Practitioner"]},
                {"name": "CI/CD", "description": "GitHub Actions, automated tests", "resources": ["GitHub Actions docs"]},
            ],
            "goals": ["Deploy model to cloud", "CI pipeline for ML repo"],
            "milestone": "Automated train → deploy pipeline",
        },
        {
            "month": 4,
            "title": "Monitoring & Scale",
            "topics": [
                {"name": "Monitoring", "description": "Prometheus, Grafana, model drift", "resources": ["Evidently AI", "WhyLabs"]},
                {"name": "Kubernetes", "description": "Pods, services, basic K8s deploy", "resources": ["Kubernetes basics"]},
            ],
            "goals": ["Monitoring dashboard", "K8s deployment"],
            "milestone": "Production ML system with monitoring",
        },
    ],
    "software_engineer": [
        {
            "month": 1,
            "title": "Programming Core",
            "topics": [
                {"name": "Python or JavaScript", "description": "Language mastery, clean code", "resources": ["Exercism", "Eloquent JS / Real Python"]},
                {"name": "Git", "description": "Version control, collaboration", "resources": ["Pro Git", "GitHub Skills"]},
            ],
            "goals": ["100 Exercism exercises", "Contribute to open source"],
            "milestone": "Clean code portfolio repo",
        },
        {
            "month": 2,
            "title": "Data Structures & Algorithms",
            "topics": [
                {"name": "DSA", "description": "Arrays, trees, graphs, sorting, DP patterns", "resources": ["NeetCode 150", "LeetCode"]},
            ],
            "goals": ["50 LeetCode problems", "Pattern recognition"],
            "milestone": "Pass mock coding interview",
        },
        {
            "month": 3,
            "title": "Web & APIs",
            "topics": [
                {"name": "Backend APIs", "description": "REST, FastAPI/Express, auth", "resources": ["FastAPI tutorial", "MDN Web Docs"]},
                {"name": "Databases", "description": "SQL, ORMs, schema design", "resources": ["PostgreSQL tutorial", "SQLBolt"]},
            ],
            "goals": ["Full-stack CRUD app", "Database design project"],
            "milestone": "Deployed web application",
        },
        {
            "month": 4,
            "title": "System Design & Portfolio",
            "topics": [
                {"name": "System design", "description": "Scalability, caching, microservices intro", "resources": ["System Design Primer"]},
                {"name": "Interview prep", "description": "Behavioral + technical interviews", "resources": ["MentorMind Interview Coach"]},
            ],
            "goals": ["2 portfolio apps", "System design practice"],
            "milestone": "Interview-ready SWE portfolio",
        },
    ],
}

GOAL_ALIASES: dict[str, str] = {
    "ai engineer": "ai_engineer",
    "become an ai engineer": "ai_engineer",
    "artificial intelligence engineer": "ai_engineer",
    "data scientist": "data_scientist",
    "become a data scientist": "data_scientist",
    "mlops": "mlops_engineer",
    "mlops engineer": "mlops_engineer",
    "software engineer": "software_engineer",
    "become a software engineer": "software_engineer",
    "web developer": "software_engineer",
    "machine learning engineer": "ai_engineer",
}
