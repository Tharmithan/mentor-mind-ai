"""Curriculum templates for offline exam study plans (Week 6 · Day 2)."""

from __future__ import annotations

# Each phase is a list of (focus, tasks) tuples spread across days in that phase.
CURRICULA: dict[str, list[tuple[str, str, list[str]]]] = {
    "Machine Learning": [
        (
            "Foundations",
            "Math & Python refresh",
            [
                "Review linear algebra: vectors, matrices, dot products",
                "NumPy & pandas quick practice",
                "Skim supervised vs unsupervised learning overview",
            ],
        ),
        (
            "Foundations",
            "Data prep & EDA",
            [
                "Train/validation/test splits",
                "Feature scaling and encoding",
                "Plot distributions and correlations",
            ],
        ),
        (
            "Supervised Learning",
            "Regression",
            [
                "Linear & logistic regression intuition",
                "Loss functions and gradient descent",
                "Practice with scikit-learn pipelines",
            ],
        ),
        (
            "Supervised Learning",
            "Classification",
            [
                "Decision trees and random forests",
                "Precision, recall, F1, confusion matrix",
                "Handle class imbalance basics",
            ],
        ),
        (
            "Model Evaluation",
            "Metrics & validation",
            [
                "Cross-validation and overfitting",
                "ROC-AUC and threshold tuning",
                "Error analysis on a sample dataset",
            ],
        ),
        (
            "Unsupervised Learning",
            "Clustering & dim reduction",
            [
                "K-means and elbow method",
                "PCA intuition and use cases",
                "When to use unsupervised methods",
            ],
        ),
        (
            "Neural Networks",
            "Deep learning basics",
            [
                "Perceptrons, activation functions",
                "Backpropagation at a high level",
                "Build a small MLP in PyTorch or Keras",
            ],
        ),
        (
            "Neural Networks",
            "CNNs & regularization",
            [
                "Convolution layers and pooling",
                "Dropout and batch normalization",
                "Transfer learning overview",
            ],
        ),
        (
            "Applied ML",
            "Feature engineering",
            [
                "Domain-specific features",
                "Feature selection techniques",
                "End-to-end mini project walkthrough",
            ],
        ),
        (
            "Applied ML",
            "Ensembles & tuning",
            [
                "Bagging, boosting (XGBoost intro)",
                "Grid/random search for hyperparameters",
                "Compare 3 models on the same task",
            ],
        ),
        (
            "Exam Prep",
            "Practice problems",
            [
                "10 conceptual MCQs (bias-variance, metrics)",
                "Implement one algorithm from scratch (simple)",
                "Review common interview ML questions",
            ],
        ),
        (
            "Exam Prep",
            "Mock exam",
            [
                "Timed practice set (90 min)",
                "Review mistakes and weak topics",
                "Write cheat-sheet of key formulas",
            ],
        ),
        (
            "Final Review",
            "Light revision",
            [
                "Re-read cheat-sheet and must-know list",
                "Flashcard drill on definitions",
                "Rest — avoid cramming new topics",
            ],
        ),
        (
            "Final Review",
            "Exam day readiness",
            [
                "Skim top 5 weak areas only",
                "Prepare materials and calm routine",
                "Quick confidence review of what you mastered",
            ],
        ),
    ],
    "Data Structures": [
        ("Arrays & Strings", "Core patterns", ["Two-pointer technique", "Sliding window", "Hash map lookups"]),
        ("Linked Lists", "Pointer manipulation", ["Reverse a list", "Detect cycles", "Merge sorted lists"]),
        ("Stacks & Queues", "Applications", ["Valid parentheses", "BFS with queue", "Monotonic stack intro"]),
        ("Trees", "Traversals", ["DFS pre/in/post-order", "BFS level-order", "BST operations"]),
        ("Trees", "Advanced", ["Lowest common ancestor", "Tree height & balance", "Serialize/deserialize"]),
        ("Graphs", "Fundamentals", ["Adjacency list vs matrix", "DFS/BFS on graphs", "Connected components"]),
        ("Graphs", "Algorithms", ["Dijkstra intro", "Topological sort", "Union-find basics"]),
        ("Sorting", "Classic algorithms", ["Merge sort & quicksort", "Big-O comparison", "When to use which"]),
        ("Dynamic Programming", "Patterns", ["Fibonacci → memoization", "Knapsack intro", "1D DP problems"]),
        ("Heaps", "Priority queues", ["Heapify operations", "Top-K elements", "Merge K sorted"]),
        ("Exam Prep", "Mixed practice", ["5 medium LeetCode-style problems", "Timed mock set", "Review mistakes"]),
        ("Exam Prep", "Final drill", ["Complexity analysis refresh", "Must-know patterns list", "Light review only"]),
    ],
    "Programming": [
        ("Basics", "Syntax & types", ["Variables, loops, functions", "Error handling", "Unit test one function"]),
        ("OOP", "Classes & design", ["Encapsulation & inheritance", "Design a small class hierarchy", "SOLID skim"]),
        ("Debugging", "Tools & mindset", ["Use debugger/breakpoints", "Read stack traces", "Fix 3 buggy snippets"]),
        ("Algorithms", "Complexity", ["Big-O practice", "Compare two solutions", "Optimize a brute-force"]),
        ("APIs", "HTTP & REST", ["GET/POST semantics", "Build a tiny FastAPI route", "JSON serialization"]),
        ("Databases", "SQL basics", ["SELECT/JOIN queries", "Indexes intro", "ORM vs raw SQL"]),
        ("Testing", "Quality", ["Write pytest cases", "Mock external calls", "TDD on one feature"]),
        ("Exam Prep", "Project review", ["Walk through a past project", "Explain design decisions", "Mock oral Q&A"]),
    ],
}

SUBJECT_ALIASES: dict[str, str] = {
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Machine Learning",
    "data structures": "Data Structures",
    "dsa": "Data Structures",
    "algorithms": "Data Structures",
    "programming": "Programming",
    "python": "Programming",
    "computer science": "Programming",
    "math": "Mathematics",
    "mathematics": "Mathematics",
    "calculus": "Mathematics",
    "statistics": "Mathematics",
}

LEARNING_RESOURCES: dict[str, list[str]] = {
    "Machine Learning": [
        "Andrew Ng — Machine Learning Specialization (Coursera)",
        "Scikit-learn user guide — model selection",
        "fast.ai — Practical Deep Learning (free)",
        "Kaggle Learn — Intro to ML micro-courses",
    ],
    "Data Structures": [
        "NeetCode / LeetCode — pattern-based practice",
        "Visualgo — interactive algorithm visualizations",
        "CLRS (Introduction to Algorithms) — reference chapters",
        "Grokking the Coding Interview — pattern review",
    ],
    "Programming": [
        "Real Python tutorials",
        "MDN Web Docs — JavaScript reference",
        "FastAPI documentation — build APIs quickly",
        "Exercism — language tracks with mentoring",
    ],
    "Mathematics": [
        "Khan Academy — Algebra & Calculus paths",
        "3Blue1Brown — Essence of Linear Algebra (YouTube)",
        "Paul's Online Math Notes",
        "OpenStax — free textbooks",
    ],
    "Portuguese": [
        "Duolingo / Busuu — daily practice",
        "Conjuga-me — verb conjugation drill",
        "Practice reading short news articles",
    ],
}

DEFAULT_CURRICULUM = [
    ("Week 1", "Core concepts", ["Read chapter summaries", "Create flashcards", "Practice 5 problems"]),
    ("Week 2", "Applied practice", ["Mixed exercises", "Timed quiz", "Review weak areas"]),
    ("Final", "Exam readiness", ["Mock exam", "Cheat-sheet", "Light review"]),
]
