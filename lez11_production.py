import os
from agno.os import AgentOS
from dotenv import load_dotenv
from agno.team import Team
from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.hackernews import HackerNewsTools
from agno.tools.yfinance import YFinanceTools
from pathlib import Path
from agno.db.sqlite import SqliteDb
from fastapi import FastAPI

data_dir = Path(os.getenv("DATA_DIR", "/data"))
data_dir.mkdir(parents=True, exist_ok=True)

db = SqliteDb(db_file=str(data_dir / "agno_sessions.db"))
#load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise RuntimeError(
        "OPENROUTER_API_KEY is missing."
    )

news_agent = Agent(
    id="news_agent",
    model=OpenRouter(
        id="openrouter/free",
        api_key=api_key,
    ),
    cache_session=True,
    add_history_to_context=True,
    num_history_runs=5,
    db=db,
    name="News Agent",
    role="Prendi le news tech da HackerNews",
    tools=[HackerNewsTools()]
)

finance_agent = Agent(
    id="finance_agent",
    model=OpenRouter(
        id="openrouter/free",
        api_key=api_key,
    ),
    cache_session=True,
    add_history_to_context=True,
    num_history_runs=5,
    db=db,
    name="Agente finanziario",
    role="Ottieni informazioni finanziarie e dati di borsa",
    tools=[YFinanceTools()]
)

team = Team(
    name="Research Team",
    members=[news_agent, finance_agent],
    model=OpenRouter(
        id="openrouter/free",
        api_key=api_key,
    ),
    id="research-team",
    instructions="Delega all'agente appropriato in base alla richiesta."
)
allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

agent_os = AgentOS(
    teams=[team],
    agents=[news_agent, finance_agent],
    cors_allowed_origins=allowed_origins
)

app = agent_os.get_app()

@app.get("/health")
def health():
    return {"status": "ok"}

#App FastAPI - Esecuzione del backend [utile per il debugging e lo sviluppo locale]

#if __name__ == "__main__":
#    agent_os.serve(app="lez11_production:app", reload=True)

#per lanciare un'app facendola scalare per tanti utenti, si deve usare uvicorn
