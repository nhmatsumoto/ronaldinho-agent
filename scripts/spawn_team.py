import os

ROLES = [
    # --- INFRASTRUCTURE, DEVOPS & SYSTEMS ---
    ("Kubernetes Master", "K8s, Helm, Orchestration", ["Zero downtime", "Auto-scaling", "Cluster health"]),
    ("Cloud Security", "SecOps, IAM, Compliance", ["Vulnerability scanning", "Secrets management", "Hardening"]),
    ("SRE / Observability", "Prometheus, Grafana, Logs", ["SLO/SLA management", "Incident response", "Monitoring"]),
    ("FinOps specialist", "Cloud Cost Optimization", ["Cost transparency", "Resource rightsizing", "Budgeting"]),
    ("Terraform Master", "Infrastructure as Code", ["Repeatable infra", "State management", "Modules"]),
    ("Ansible Architect", "Configuration Management", ["Agentless automation", "Playbook modularity", "Idempotency"]),
    ("Docker Captain", "Containerization, Security", ["Image optimization", "Run-time config", "Volumes"]),
    ("CI/CD Architect", "Pipelines, GitHub Actions", ["Fast feedback", "Safe deployments", "Tooling"]),
    ("Network Engineer", "VPC, DNS, Load Balancing", ["Connectivity", "Security groups", "Latency"]),
    ("Database Administrator", "Scaling, Backups, HA", ["Data integrity", "Disaster recovery", "Performance"]),
    ("Linux Kernel Expert", "Low-level optimization", ["Syscalls", "Memory management", "Drivers"]),
    ("Hardware Specialist", "Arduino, ESP32, Sensors", ["Firmware", "Power management", "Prototyping"]),
    ("IoT Architect", "MQTT, Edge Computing", ["Device mgmt", "Offline sync", "Security"]),
    ("Cloud Migration Pro", "On-prem to Cloud", ["Strangler migration", "Risk assessment", "Cost planning"]),
    ("Multicloud Expert", "AWS, Azure, GCP", ["Portability", "Cross-cloud sync", "Redundancy"]),
    ("VPC Networking", "Complex Routing", ["Subnetting", "Transit Gateways", "VPN"]),
    ("Security Architect", "Zero Trust, WAF", ["Penetration testing", "Encryption", "Threat detection"]),

    # --- BACKEND, DATA & AI ---
    ("API Designer", "Rest, GraphQL, schemas", ["Contract-first dev", "Versioning", "Developer experience"]),
    ("Go Systems Engineer", "Performant background services", ["Concurrency", "Low latency", "Systems programming"]),
    ("Python Backend Pro", "FastAPI, Django, Logic", ["Maintainable code", "Async patterns", "Library choice"]),
    ("Rust Low-level", "Memory safety, Performance", ["Zero cost abstractions", "Safety", "Systems"]),
    ("Node.js Guru", "Scaling async services", ["Event loop", "Microservices", "Performance"]),
    ("Java Spring Expert", "Enterprise architecture", ["Dependency injection", "Security", "Reliability"]),
    ("C++ Game Dev", "Performance, Graphics", ["Memory mgmt", "Engine architecture", "Math"]),
    ("SQL Perf Tuner", "Postgres, Query Optimization", ["Index strategy", "Query profiling", "Schema tuning"]),
    ("NoSQL Modeler", "Mongo, DynamoDB, Cassandra", ["Data modeling", "Scaling", "Read/Write efficiency"]),
    ("VectorDB Expert", "Pinecone, Milvus, Weaviate", ["Embedding storage", "Similarity search", "Scalable AI"]),
    ("Cache Magician", "Redis, ValKey, Memcached", ["Hot data strategy", "Latency reduction", "Persistence"]),
    ("Event-Driven Master", "Kafka, RabbitMQ, EDA", ["Event sourcing", "Message integrity", "Decoupling"]),
    ("Serverless Expert", "Lambda, Cloud functions", ["Pay-per-use infra", "Cold start optimization", "Tracing"]),
    ("RAG Architect", "Retrieval Augmented Generation", ["Knowledge retrieval", "Fact checking", "Chunking"]),
    ("Prompt Engineer", "LLM Instruction, Few-shot", ["Context optimization", "Reliability", "Tone control"]),
    ("NLP Specialist", "Tokenization, Transformers", ["Language tech", "Embedding logic", "Classification"]),
    ("Deep Learning Pro", "PyTorch, TensorFlow", ["Model training", "Architecture", "Optimization"]),
    ("Computer Vision", "OpenCV, YOLO", ["Object detection", "Image processing", "Video stream"]),
    ("MLOps Engineer", "Training & Deployment", ["Model monitoring", "Versioning", "Data drift"]),
    ("Data Engineer", "Airflow, Spark, ETL", ["Data pipelines", "Data lakes", "Governance"]),
    ("Data Scientist", "Notebooks, Pandas, Sklearn", ["Insight generation", "Predictive modeling", "Stats"]),
    ("Graph Database Expert", "Neo4j, Cypher", ["Relation mining", "Pathfinding", "Network analysis"]),

    # --- FRONTEND, UI/UX & MOBILE ---
    ("React Specialist", "Hooks, Context, Rendering", ["Component architecture", "State management", "Patterns"]),
    ("Next.js Expert", "SSR, ISR, App Router", ["SEO", "Performance", "Metadata"]),
    ("Vue Master", "Composition API, Vite", ["Reactivity", "Simplicity", "Modularity"]),
    ("Angular Architect", "Enterprise scale SPAs", ["TypeScript", "RxJS", "Strictness"]),
    ("Tailwind Pro", "Utility-first CSS", ["Responsive UI", "Design consistency", "Speed"]),
    ("SASS / CSS Expert", "Advanced Styling", ["Modular CSS", "Layouts", "Animations"]),
    ("Framer Motion pro", "UI Animations", ["Micro-interactions", "User delight", "Smoothness"]),
    ("Accessibility Pro", "A11y, WCAG, ARIA", ["Inclusive design", "Screen reader support", "Color contrast"]),
    ("Design System Architect", "Scalable UI Libraries", ["Components", "Tokens", "Themes"]),
    ("SEO Specialist", "Technical SEO, Ranking", ["Indexing", "Meta tags", "Speed"]),
    ("Performance Engineer", "Core Web Vitals", ["Loading speed", "Interactivity", "Stability"]),
    ("Mobile iOS Expert", "Swift, SwiftUI", ["App Store guidelines", "Native feel", "Performance"]),
    ("Mobile Android Expert", "Kotlin, Compose", ["Play Store guidelines", "Background tasks", "UI"]),
    ("Flutter Dev", "Cross-platform, Dart", ["Code reuse", "Beautiful UI", "Fast dev"]),
    ("React Native Guru", "Native bridges, Perf", ["Cross-platform", "Native modules", "JS thread"]),
    ("PWA Master", "Offline-first, SW", ["Service workers", "Caching", "Installable"]),
    ("Micro-frontends Guru", "Module Federation", ["Independent scaling", "Unified UX", "Lazy loading"]),
    ("WebAssembly Expert", "Rust to WASM", ["High perf in browser", "Heavy computation", "Sandboxing"]),

    # --- BLOCKCHAIN & WEB3 ---
    ("Solidity Dev", "Smart Contracts, Ethereum", ["Security audit", "Gas optimization", "Tokens"]),
    ("Solana Engineer", "Rust, High throughput", ["Parallel execution", "Dapps", "Performance"]),
    ("DeFi Architect", "Financial Protocols", ["Liquidity pools", "Yield farming", "Security"]),
    ("NFT specialist", "Minting, Metadata", ["Royalties", "Standardization", "IPFS"]),
    ("Web3 Integrator", "Ethers.js, Wagmi", ["Wallet connection", "Chain events", "Frontend"]),

    # --- BUSINESS, PRODUCT & MARKETING ---
    ("Product Manager", "Discovery, Roadmap", ["Prioritization", "User value", "Specs"]),
    ("SaaS Strategist", "Pricing, GTM", ["Subscription models", "Growth", "Retention"]),
    ("Business Analyst", "KPIs, Modeling", ["Requirement clarity", "Data-driven decisions", "ROI"]),
    ("Conversion King", "Landing pages, CRO", ["A/B testing", "Heatmaps", "Copywriting"]),
    ("SEO Content Strategist", "Topic Clusters", ["Keyword research", "Authority", "Ranking"]),
    ("Email Marketer", "Automation, Campaigns", ["Deliverability", "Open rates", "Templates"]),
    ("Growth Hacker", "Viral loops, Referrals", ["Onboarding", "Virality", "Scalability"]),
    ("Customer Success", "Onboarding, LTV", ["User feedback", "Churn prevention", "Support"]),
    ("Technical Writer", "Documentation, DevRel", ["API docs", "Tutorials", "Guides"]),
    ("Privacy Officer", "LGPD, GDPR, Compliance", ["Data protection", "Anonymization", "Policy"]),

    # --- SPECIALIZED TOOLS & PLATFORMS ---
    ("Stripe specialist", "Payments, Billing", ["Revenue integrity", "Billing flows", "Webhooks"]),
    ("Shopify Developer", "E-commerce, Liquid", ["Custom themes", "Apps", "Headless"]),
    ("Firebase Master", "NoSQL, Serverless", ["Real-time sync", "Auth", "Hosting"]),
    ("Supabase Guru", "Postgres, Auth", ["Open source Firebase", "SQL", "Real-time"]),
    ("Elasticsearch Expert", "Search Engine", ["Ranking", "Log analysis", "Filters"]),
    ("Redis Guru", "In-memory patterns", ["Data structures", "Pub/Sub", "Caching"]),
    ("Playwright Expert", "Testing, Scraping", ["Browser automation", "E2E", "Reliability"]),
    ("Cypress Pro", "Frontend Testing", ["Quick feedback", "Time travel", "Interactivity"]),
    ("Vite Master", "Build Tools, ESM", ["Speed", "Optimization", "Plugins"]),
    ("Webpack Hero", "Bundling Legacy", ["Config tuning", "Optimization", "Loaders"]),

    # --- INDUSTRY SPECIFIC ---
    ("Fintech Specialist", "Compliance, Ledgers", ["Security", "Precision", "Regulatory"]),
    ("Edtech Architect", "LMS, Interactive", ["Learning paths", "Gamification", "Tracking"]),
    ("Healthtech Pro", "HIPAA, Interoperability", ["Privacy", "Standards", "Connectivity"]),
    ("E-commerce Architect", "Marketplaces", ["Inventory", "Ordering", "Warehouse"]),
    ("Proptech Dev", "Real Estate Tech", ["Map integration", "Legal data", "Images"]),

    # --- SOFT SKILLS & MANAGEMENT ---
    ("Agile Facilitator", "Scrum, Kanban", ["Velocity", "Blocker removal", "Health"]),
    ("Team Lead", "Mentorship, Culture", ["Delivery", "Happiness", "Tech debt"]),
    ("CTO Advisor", "Tech Strategy", ["Scale", "Architecture", "Hiring"]),
    ("Quality Auditor", "Code Standards", ["Maintainability", "Security", "Best practices"]),
    ("Creative Director", "UI/UX, Branding", ["Consistency", "Visual impact", "Delight"]),
    ("Code cleaner", "Refactoring technician", ["Variable naming", "Dry principle", "Clarity"]),
]

TEMPLATE = """# {role_upper} SPECIALIST (TOON)

## 🎯 SPECIALIZATION ({specialization})
{description}

## 🏆 OBJECTIVE
{objectives}

## 🛠️ TOOLKIT
- **Source**: `PROJECT_INFO.toon`, `Engineering_Specs.toon`.
- **Skills**: `{role_slug}.py` (Specialized interactions).
"""

def spawn():
    target_dir = ".agent/team"
    os.makedirs(target_dir, exist_ok=True)
    
    count = 0
    for role, specialization, objectives_list in ROLES:
        role_slug = role.lower().replace(" ", "_").replace("/", "_").replace(".","_").replace("-","_")
        role_upper = role.upper()
        
        objs = "\n".join([f"- **{obj}**: Garantir excelência técnica em {obj.lower()}." for obj in objectives_list])
        
        # Simple description synthesis
        description = f"Especialista em {role_upper}, responsável por {specialization.lower()}."
        
        content = TEMPLATE.format(
            role_upper=role_upper,
            specialization=specialization,
            description=description,
            objectives=objs,
            role_slug=role_slug
        )
        
        file_path = os.path.join(target_dir, f"{role_slug}.toon")
        with open(file_path, "w") as f:
            f.write(content)
        count += 1
        
    print(f"[*] Fenomenal! Spawning de {count} agentes de elite concluído.")

if __name__ == "__main__":
    spawn()
