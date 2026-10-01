from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .core.database import engine, Base, SessionLocal
from .core.security import hash_password
from .core.logging_config import setup_logging
from .api.routes import auth, graph, query, security, analytics

logger = setup_logging()
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(graph.router, prefix=settings.API_V1_STR)
app.include_router(query.router, prefix=settings.API_V1_STR)
app.include_router(security.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)


@app.get("/health")
def health():
    return {"status": "healthy", "version": settings.VERSION}


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    from .models.user import User
    from .services.data_generator import ensure_seed_data
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            # Multiple roles for demo
            db.add(User(
                email="admin@caceai.com",
                password_hash=hash_password("admin123"),
                full_name="Admin User",
                role="admin",
            ))
            db.add(User(
                email="analyst@caceai.com",
                password_hash=hash_password("analyst123"),
                full_name="Analyst User",
                role="analyst",
            ))
            db.add(User(
                email="viewer@caceai.com",
                password_hash=hash_password("viewer123"),
                full_name="Viewer User",
                role="viewer",
            ))
            db.commit()
            logger.info("Created demo users (admin / analyst / viewer)")
        
        ensure_seed_data(db)
        logger.info("Context Knowledge Graph seeded")
    finally:
        db.close()
