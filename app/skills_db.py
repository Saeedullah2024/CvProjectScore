"""
Static knowledge bases used by the extractors and matching engine.

In a production system these would live in a database and be maintained
by an admin UI or synced from a taxonomy provider (e.g. ESCO, LinkedIn
Skills Graph). Here they are plain Python collections so the project
runs with zero external services.
"""

# --- Technical / hard skills -------------------------------------------------
TECH_SKILLS = [
    # Programming languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "sql",
    "bash", "shell scripting", "perl", "dart", "objective-c",
    # Web / frontend
    "html", "css", "sass", "react", "react.js", "vue", "vue.js", "angular",
    "next.js", "nuxt.js", "svelte", "tailwind css", "bootstrap", "jquery",
    "webpack", "vite", "redux", "graphql", "rest api", "restful apis",
    # Backend / frameworks
    "node.js", "express.js", "django", "flask", "fastapi", "spring",
    "spring boot", "asp.net", ".net", "laravel", "ruby on rails", "nestjs",
    # Data / ML / AI
    "machine learning", "deep learning", "natural language processing", "nlp",
    "computer vision", "data science", "data analysis", "data engineering",
    "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "keras",
    "opencv", "spark", "apache spark", "hadoop", "airflow", "mlops",
    "llm", "large language models", "transformers", "generative ai",
    # Databases
    "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle",
    "elasticsearch", "cassandra", "dynamodb", "firebase", "supabase",
    "microsoft sql server", "nosql",
    # Cloud / DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud platform",
    "docker", "kubernetes", "terraform", "ansible", "jenkins", "ci/cd",
    "github actions", "gitlab ci", "cloudformation", "linux", "nginx",
    "microservices", "serverless",
    # Tools / practices
    "git", "github", "gitlab", "jira", "confluence", "agile", "scrum",
    "kanban", "tdd", "unit testing", "pytest", "junit", "selenium",
    "postman", "figma", "excel", "power bi", "tableau", "looker",
    # Mobile
    "android", "ios", "react native", "flutter", "xamarin",
    # Security
    "cybersecurity", "penetration testing", "network security",
    "information security", "owasp",
]

# --- Soft / interpersonal skills ---------------------------------------------
SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "collaboration",
    "problem solving", "critical thinking", "time management",
    "adaptability", "creativity", "project management", "negotiation",
    "conflict resolution", "mentoring", "public speaking",
    "stakeholder management", "decision making", "attention to detail",
    "customer service", "presentation skills", "analytical thinking",
    "emotional intelligence", "strategic planning", "multitasking",
]

ALL_SKILLS = sorted(set(TECH_SKILLS + SOFT_SKILLS), key=len, reverse=True)

# --- Certifications ------------------------------------------------------
CERTIFICATIONS = [
    "aws certified solutions architect", "aws certified developer",
    "aws certified sysops administrator", "azure fundamentals",
    "microsoft certified", "google cloud certified", "pmp",
    "project management professional", "certified scrum master", "csm",
    "cissp", "ceh", "certified ethical hacker", "comptia security+",
    "comptia a+", "comptia network+", "ccna", "ccnp", "itil",
    "six sigma", "lean six sigma", "certified kubernetes administrator",
    "cka", "terraform associate", "salesforce certified",
    "oracle certified professional", "ocp", "sas certified",
    "tableau desktop specialist", "google analytics certified",
    "toefl", "ielts",
]

# --- Education ordinal levels -------------------------------------------
# Higher number = higher level. Used to compare CV education vs JD requirement.
DEGREE_LEVELS = {
    "high school": 1, "high school diploma": 1, "secondary school": 1,
    "associate": 2, "associate degree": 2, "diploma": 2,
    "bachelor": 3, "bachelor's": 3, "bsc": 3, "b.sc": 3, "ba": 3, "b.a": 3,
    "beng": 3, "b.eng": 3, "btech": 3, "b.tech": 3, "bs": 3, "undergraduate": 3,
    "master": 4, "master's": 4, "msc": 4, "m.sc": 4, "ma": 4, "m.a": 4,
    "meng": 4, "m.eng": 4, "mtech": 4, "m.tech": 4, "mba": 4, "ms": 4,
    "postgraduate": 4,
    "phd": 5, "ph.d": 5, "doctorate": 5, "doctoral": 5,
}

DEGREE_PATTERN_KEYWORDS = sorted(DEGREE_LEVELS.keys(), key=len, reverse=True)

# --- Section headers used to split raw resume / JD text into blocks -----
CV_SECTION_HEADERS = {
    "skills": ["skills", "technical skills", "core competencies", "key skills"],
    "education": ["education", "academic background", "qualifications"],
    "experience": ["experience", "work experience", "professional experience",
                   "employment history", "work history"],
    "certifications": ["certifications", "certificates", "licenses",
                        "licenses & certifications"],
    "projects": ["projects", "personal projects", "key projects",
                 "academic projects"],
    "summary": ["summary", "professional summary", "objective", "profile"],
}

JD_SECTION_HEADERS = {
    "required": ["requirements", "required skills", "required qualifications",
                 "must have", "minimum qualifications", "what you need",
                 "basic qualifications"],
    "preferred": ["preferred", "preferred qualifications", "nice to have",
                  "bonus points", "good to have", "preferred skills"],
    "responsibilities": ["responsibilities", "what you'll do",
                          "key responsibilities", "role responsibilities",
                          "duties", "about the role"],
    "education": ["education", "academic requirements"],
    "experience": ["experience"],
}
