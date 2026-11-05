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

db = SqliteDb(
    db_file=str(Path(__file__).resolve().parent / "agno_sessions.db")
)

#load_dotenv()

openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
if not openrouter_api_key:
    raise RuntimeError(
        "OPENROUTER_API_KEY is missing. Add your OpenRouter API key to the "
        "environment or to a .env file in the project directory."
    )

news_agent = Agent(
    id="news_agent",
    model=OpenRouter(
        id="openrouter/free",
        api_key=openrouter_api_key,
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
        api_key=openrouter_api_key,
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
        api_key=openrouter_api_key,
    ),
    id="research-team",
    instructions="Delega all'agente appropriato in base alla richiesta."
)
agent_os = AgentOS(
    teams=[team],
    agents=[news_agent, finance_agent],
    cors_allowed_origins=[
        "http://localhost:3000",       # Esempio: frontend locale
        "https://tuo-frontend.vercel.app",  # Sostituisci col dominio reale
    #    "https://os.agno.com",         # Solo se usi la UI di AgentOS
    ],
)

app = agent_os.get_app()

#App FastAPI - Esecuzione del backend [utile per il debugging e lo sviluppo locale]


#if __name__ == "__main__":
#    agent_os.serve(app="lez11_production:app", reload=True)

#per lanciare un'app facendola scalare per tanti utenti, si deve usare uvicorn
