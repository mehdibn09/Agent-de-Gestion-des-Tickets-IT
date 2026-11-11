"""API TicketAssist : application injectable et service local."""
import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.schemas import Analyse, Erreur, ListeTickets, Modification, Statut, TicketInput, TicketOut
from api.security import administrateur, authentifier
from ticket_agent import __version__
from ticket_agent.agent import Agent
from ticket_agent.config import Settings
from ticket_agent.model import Classifier
from ticket_agent.storage import Conflit, Introuvable, Store, TransitionInvalide

logger = logging.getLogger(__name__)
Role = Annotated[str, Depends(authentifier)]
Admin = Annotated[str, Depends(administrateur)]


def agent(request: Request) -> Agent:
    value = request.app.state.agent
    if value is None:
        raise HTTPException(503, "Modèle indisponible : lancer ticket train et redémarrer l’API")
    return value


AgentDep = Annotated[Agent, Depends(agent)]


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or Settings.from_env()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        application.state.store = Store(config.db_path)
        application.state.agent = None
        try:
            application.state.agent = Agent(Classifier(config.model_path, config.threshold))
        except Exception:
            logger.warning("Modèle absent ou incompatible ; API en mode indisponible pour l’analyse")
        yield

    application = FastAPI(title="TicketAssist API", version=__version__, lifespan=lifespan,
                          description="Qualification, validation humaine et suivi de tickets IT",
                          responses={code: {"model": Erreur} for code in (401, 403, 404, 409, 422, 500, 503)})
    application.state.settings = config
    application.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8080", "http://localhost:8080"],
                               allow_methods=["GET", "POST", "PATCH"], allow_headers=["X-API-Key", "Content-Type"])

    @application.exception_handler(StarletteHTTPException)
    async def erreur_http(request: Request, exc: StarletteHTTPException):
        return JSONResponse(status_code=exc.status_code,
                            content={"code": f"http_{exc.status_code}", "message": str(exc.detail)}, headers=exc.headers)

    @application.exception_handler(RequestValidationError)
    async def erreur_validation(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"code": "validation", "message": "Requête invalide ; consulter le contrat dans /docs"})

    @application.exception_handler(Introuvable)
    async def introuvable(request: Request, exc: Introuvable):
        return JSONResponse(status_code=404, content={"code": "introuvable", "message": str(exc)})

    @application.exception_handler(Conflit)
    async def conflit(request: Request, exc: Conflit):
        return JSONResponse(status_code=409, content={"code": "conflit", "message": str(exc)})

    @application.exception_handler(TransitionInvalide)
    async def transition(request: Request, exc: TransitionInvalide):
        return JSONResponse(status_code=422, content={"code": "transition", "message": str(exc)})

    @application.exception_handler(Exception)
    async def inattendue(request: Request, exc: Exception):
        logger.error("Erreur interne TicketAssist : %s", type(exc).__name__)
        return JSONResponse(status_code=500, content={"code": "interne", "message": "Erreur interne du serveur"})

    @application.get("/")
    def accueil():
        return {"application": "TicketAssist", "version": __version__, "docs": "/docs", "health": "/health"}

    @application.get("/health")
    @application.get("/v1/health")
    def sante(request: Request):
        if request.app.state.agent is None:
            raise HTTPException(503, "Modèle indisponible")
        return {"status": "OK", "version": __version__, "modele": "tfidf-logreg-tickets",
                "seuil": config.threshold, "donnees": "voir data/README.md"}

    @application.post("/v1/tickets/analyze", response_model=Analyse)
    def analyser(entree: TicketInput, role: Role, current: AgentDep):
        return current.analyser(**entree.model_dump())

    @application.post("/v1/tickets", response_model=TicketOut, status_code=201)
    def creer(entree: TicketInput, role: Role, current: AgentDep, request: Request):
        result = current.analyser(**entree.model_dump())
        return request.app.state.store.creer(entree.model_dump(), result, role)

    @application.get("/v1/tickets", response_model=ListeTickets)
    def lister(request: Request, role: Role, statut: Statut | None = None,
               limit: Annotated[int, Query(ge=1, le=100)] = 50, offset: Annotated[int, Query(ge=0)] = 0):
        return request.app.state.store.lister(statut, limit, offset)

    @application.get("/v1/tickets/{identifiant}", response_model=TicketOut)
    def obtenir(identifiant: str, request: Request, role: Role):
        return request.app.state.store.obtenir(identifiant)

    @application.patch("/v1/tickets/{identifiant}", response_model=TicketOut)
    def modifier(identifiant: str, entree: Modification, request: Request, role: Admin):
        return request.app.state.store.modifier(identifiant, **entree.model_dump())

    return application


app = create_app()
