---
description: Orchestrates the transformation of natural language requirements into engineering specifications using DDD and specialist agents.
---

# Agent Orchestrator Workflow

This workflow processes natural language requirements through a Domain-Driven Design (DDD) pipeline and delegates tasks to specialist agents.

## 1. Requirement Analysis & TOON-DDD Transformation

**Input**: Natural Language Requirements (from User or PM)

**Process**:

1. **Analyze** requirements to identify Core Domain, Subdomains, and Bounded Contexts.
2. **Map** the Ubiquitous Language (UL) for each context.
3. **Define** Entities, Value Objects, Aggregates, and Domain Events.
4. **Produce** a TOON-based DDD Model for maximum token efficiency.

**Output**: `DDD_Model.toon` (Artifact)

## 2. Engineering Requirement Generation (TOON-First)

**Input**: `DDD_Model.toon`

**Process**:

1. Translate the DDD model into technical specifications using the TOON format.
2. Define API endpoints, Data Models, and Service Interfaces in `Engineering_Specs.toon`.
3. Identify dependencies and integration points.

**Output**: `Engineering_Specs.toon` (Artifact)

## 3. Specialist Delegation

The Orchestrator delegates tasks to specialists based on the `Engineering_Specs.toon`:

### A. TOON Specialist

* **Role**: Optimize all agent communications and data models.
* **Task**: Generate `Adapter_Specs.toon` and oversee format transitions.
* **Reference**: `.agent/specialists/toon.md`

### B. Database Specialist

* **Role**: Design schema and persistence based on `Schema.toon`.
* **Reference**: `.agent/specialists/database.md`

### C. Network Specialist

* **Role**: Define high-performance TOON/gRPC communication protocols.
* **Reference**: `.agent/specialists/network.md`

### D. Security Specialist

* **Role**: Define `Security_Policy.toon` and IAM rules.
* **Reference**: `.agent/specialists/security.md`

### E. DevOps Specialist

* **Role**: Manage infrastructure as code via `Infrastructure.toon`.
* **Reference**: `.agent/specialists/devops.md`

### F. Review Agent & Coherence Agent

* **Role**: Validate code alignment with `DDD_Model.toon` and `Engineering_Specs.toon`.
* **Reference**: `.agent/specialists/reviewer.md` | `.agent/specialists/coherence.md`

## 4. Execution Strategy

For each requirement:

1. **Update** the Ubiquitous Language in `DDD_Model.toon`.
2. **Generate** Tasks for each specialist using TOON for context efficiency.
3. **Review** outputs using the Coherence Check Agent via `Coherence_Report.toon`.
