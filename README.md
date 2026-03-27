# Research to Outreach

Research to Outreach is a monorepo that automates lead research and outreach by combining an AI research agent (powered by Anthropic) with a FastAPI backend and a React frontend. Given a search query, the system finds leads, enriches them with contact details and a research summary, and surfaces them in a dashboard for review and outreach.

## Getting started

1. Clone the repository: `git clone <repo-url> && cd research-to-outreach`
2. Copy the example env file: `cp .env.example .env` and fill in your credentials
3. Start all services: `docker-compose up`
