"""Career path definitions and skill mappings (Week 6 · Day 3)."""

from __future__ import annotations

CAREER_PATHS: dict[str, dict] = {
    "data_scientist": {
        "title": "Data Scientist",
        "tagline": "Turn data into insights and predictive models",
        "required_skills": {
            "statistics": 85,
            "machine_learning": 80,
            "python": 75,
            "data_visualization": 70,
            "communication": 65,
        },
        "subject_weights": {
            "Mathematics": 0.35,
            "Programming": 0.25,
            "Data Structures": 0.15,
            "Portuguese": 0.1,
        },
        "interview_weights": {"technical": 0.25, "communication": 0.2, "confidence": 0.15},
        "interest_keywords": ["data", "statistics", "analytics", "research", "science", "ml", "machine learning"],
    },
    "ai_engineer": {
        "title": "AI Engineer",
        "tagline": "Build and deploy intelligent applications with LLMs and ML",
        "required_skills": {
            "machine_learning": 85,
            "python": 85,
            "deep_learning": 80,
            "software_design": 75,
            "nlp": 70,
            "communication": 60,
        },
        "subject_weights": {
            "Programming": 0.35,
            "Mathematics": 0.25,
            "Data Structures": 0.2,
            "Portuguese": 0.05,
        },
        "interview_weights": {"technical": 0.35, "communication": 0.15, "confidence": 0.15},
        "interest_keywords": ["ai", "llm", "gpt", "neural", "deep learning", "nlp", "genai"],
    },
    "mlops_engineer": {
        "title": "MLOps Engineer",
        "tagline": "Ship, monitor, and scale ML systems in production",
        "required_skills": {
            "python": 80,
            "devops": 85,
            "machine_learning": 75,
            "cloud": 80,
            "software_design": 75,
            "monitoring": 70,
        },
        "subject_weights": {
            "Programming": 0.4,
            "Data Structures": 0.25,
            "Mathematics": 0.15,
        },
        "interview_weights": {"technical": 0.35, "communication": 0.1, "confidence": 0.15},
        "interest_keywords": ["mlops", "devops", "deploy", "pipeline", "kubernetes", "cloud", "production"],
    },
    "software_engineer": {
        "title": "Software Engineer",
        "tagline": "Design, build, and maintain robust software systems",
        "required_skills": {
            "programming": 90,
            "algorithms": 85,
            "software_design": 80,
            "databases": 75,
            "communication": 70,
            "problem_solving": 85,
        },
        "subject_weights": {
            "Programming": 0.35,
            "Data Structures": 0.35,
            "Mathematics": 0.1,
            "Portuguese": 0.1,
        },
        "interview_weights": {"technical": 0.3, "communication": 0.25, "confidence": 0.15},
        "interest_keywords": ["software", "web", "app", "backend", "frontend", "coding", "engineer", "developer"],
    },
}

SUBJECT_SKILL_MAP: dict[str, list[str]] = {
    "Mathematics": ["statistics", "problem_solving"],
    "Programming": ["python", "programming", "software_design"],
    "Data Structures": ["algorithms", "problem_solving"],
    "Portuguese": ["communication"],
    "Science": ["problem_solving"],
}

SKILL_RESOURCES: dict[str, list[str]] = {
    "statistics": ["Khan Academy Statistics", "StatQuest YouTube", "Think Stats (free book)"],
    "machine_learning": ["Andrew Ng ML Specialization", "Hands-On ML (book)", "Kaggle Learn"],
    "python": ["Real Python", "Python official tutorial", "Exercism Python track"],
    "deep_learning": ["fast.ai", "Deep Learning Specialization (Coursera)", "PyTorch tutorials"],
    "devops": ["Docker docs", "Kubernetes basics (KodeKloud)", "GitHub Actions CI/CD"],
    "cloud": ["AWS Cloud Practitioner", "Google Cloud Skills Boost", "Azure Fundamentals"],
    "algorithms": ["NeetCode patterns", "LeetCode Top 150", "CLRS selected chapters"],
    "software_design": ["System Design Primer (GitHub)", "Clean Code (book)", "Refactoring Guru"],
    "nlp": ["Hugging Face course", "Speech and Language Processing (book)", "spaCy tutorials"],
    "communication": ["Mock interviews", "Toastmasters", "STAR method practice"],
}

ROADMAP_TEMPLATES: dict[str, list[dict]] = {
    "data_scientist": [
        {
            "phase": "Foundation",
            "duration_weeks": 6,
            "goals": ["Solid Python & pandas", "Statistics refresh", "Exploratory data analysis"],
            "skills": ["python", "statistics", "data_visualization"],
            "resources": ["Kaggle Titanic", "StatQuest", "Matplotlib/Seaborn docs"],
        },
        {
            "phase": "Core ML",
            "duration_weeks": 8,
            "goals": ["Supervised learning", "Model evaluation", "Feature engineering"],
            "skills": ["machine_learning", "statistics"],
            "resources": ["Andrew Ng ML", "scikit-learn docs", "1 end-to-end Kaggle project"],
        },
        {
            "phase": "Portfolio",
            "duration_weeks": 6,
            "goals": ["2 portfolio projects", "Storytelling with data", "Interview prep"],
            "skills": ["communication", "machine_learning"],
            "resources": ["GitHub portfolio", "Medium/blog write-ups", "Mock case studies"],
        },
    ],
    "ai_engineer": [
        {
            "phase": "ML + Software Basics",
            "duration_weeks": 6,
            "goals": ["Python APIs", "ML fundamentals", "Git & testing"],
            "skills": ["python", "machine_learning", "software_design"],
            "resources": ["FastAPI tutorial", "scikit-learn", "pytest docs"],
        },
        {
            "phase": "Deep Learning & LLMs",
            "duration_weeks": 8,
            "goals": ["Neural networks", "Transformers intro", "RAG pipeline"],
            "skills": ["deep_learning", "nlp", "machine_learning"],
            "resources": ["Hugging Face course", "LangChain docs", "Build a chatbot project"],
        },
        {
            "phase": "Production AI",
            "duration_weeks": 6,
            "goals": ["Deploy model/API", "Prompt engineering", "Evaluation & safety"],
            "skills": ["software_design", "nlp"],
            "resources": ["OpenAI API docs", "Docker deploy", "LLM eval frameworks"],
        },
    ],
    "mlops_engineer": [
        {
            "phase": "Dev Foundations",
            "duration_weeks": 6,
            "goals": ["Linux & CLI", "Git workflows", "Docker containers"],
            "skills": ["devops", "python"],
            "resources": ["Docker getting started", "Git branching guide", "Bash basics"],
        },
        {
            "phase": "ML Pipelines",
            "duration_weeks": 8,
            "goals": ["Training pipelines", "Experiment tracking", "Model registry"],
            "skills": ["machine_learning", "devops", "monitoring"],
            "resources": ["MLflow", "DVC", "Airflow intro"],
        },
        {
            "phase": "Cloud & Monitoring",
            "duration_weeks": 6,
            "goals": ["Deploy on cloud", "CI/CD for ML", "Observability"],
            "skills": ["cloud", "devops", "monitoring"],
            "resources": ["AWS SageMaker intro", "Prometheus/Grafana", "GitHub Actions"],
        },
    ],
    "software_engineer": [
        {
            "phase": "Programming Core",
            "duration_weeks": 6,
            "goals": ["Strong Python/JS", "OOP & clean code", "Unit testing"],
            "skills": ["programming", "software_design"],
            "resources": ["Exercism", "Clean Code summaries", "pytest"],
        },
        {
            "phase": "DSA & Systems",
            "duration_weeks": 8,
            "goals": ["Algorithms patterns", "REST APIs", "Database design"],
            "skills": ["algorithms", "databases", "problem_solving"],
            "resources": ["NeetCode 150", "FastAPI/Express", "SQL practice"],
        },
        {
            "phase": "Interview & Portfolio",
            "duration_weeks": 6,
            "goals": ["2 portfolio apps", "System design basics", "Behavioral prep"],
            "skills": ["communication", "software_design"],
            "resources": ["System Design Primer", "Mock interviews", "Open-source contributions"],
        },
    ],
}

INDUSTRY_TRENDS: list[dict] = [
    {
        "title": "Generative AI in every product",
        "category": "AI",
        "relevance": "High demand for AI Engineers who can integrate LLMs safely",
        "impact": "RAG, agents, and fine-tuning skills are top hiring signals",
        "action": "Build one LLM-powered project with evaluation metrics",
    },
    {
        "title": "MLOps maturity gap",
        "category": "Infrastructure",
        "relevance": "Companies struggle to move models from notebook to production",
        "impact": "MLOps Engineers command premium salaries",
        "action": "Learn Docker + MLflow + a cloud deploy pipeline",
    },
    {
        "title": "Data literacy across roles",
        "category": "Data",
        "relevance": "Data Scientists who communicate insights win promotions",
        "impact": "Storytelling + SQL + experimentation design remain core",
        "action": "Publish a portfolio analysis with clear business recommendations",
    },
    {
        "title": "AI-assisted development",
        "category": "Software",
        "relevance": "Software Engineers who leverage AI tools ship faster",
        "impact": "Fundamentals (DSA, design) still gate top-tier interviews",
        "action": "Practice coding without AI, then use AI for refactoring & tests",
    },
    {
        "title": "Responsible AI & compliance",
        "category": "Governance",
        "relevance": "EU AI Act and enterprise policies require audit trails",
        "impact": "Understanding bias, privacy, and model monitoring is differentiating",
        "action": "Add model cards and bias checks to portfolio projects",
    },
]
