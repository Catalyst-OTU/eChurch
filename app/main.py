import json
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apis.routers import router as api_router
from config.logger import log
from config.settings import settings
from db.init_db import create_system_admin
from db.init_models import init_tables,init_database
from db.session import SessionLocal, drop_and_alter_table_columns
from middleware.intruder_detection import IntruderDetectionMiddleware
from middleware.tenant import TenantMiddleware


## adding our api routes
def include(app):
    app.include_router(api_router)


def initial_data_insert():
    """Insert initial data using synchronous session."""
    with SessionLocal() as db:
        create_system_admin(db)
        drop_and_alter_table_columns(db)



# List of allowed origins
origins = [
    "http://localhost:4200",
    "https://performance-appraisal.netlify.app"
]


def start_application():
    app = FastAPI(docs_url="/", title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(localhost|[a-zA-Z0-9_-]+\.localhost)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    init_database()
    init_tables()
    initial_data_insert()
    include(app)
    app.add_middleware(IntruderDetectionMiddleware)
    app.add_middleware(TenantMiddleware)
    return app


app = start_application()



# Custom error handling middleware
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_message = "Validation error occurred"
    # Optionally, you can log the error or perform additional actions here
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": error_message + f"{exc}"})


# Generic error handler for all other exceptions
@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    error_message = "An unexpected error occurred:\n"
    # Optionally, you can log the error or perform additional actions here
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": error_message + f"{exc}"})


@app.exception_handler(json.JSONDecodeError)
def json_decode_error_handler(request: Request, exc: json.JSONDecodeError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Configuration must be a valid JSON object"},
    )


if __name__ == '__main__':
    uvicorn.run("main:app", host='127.0.0.1', port=8080, log_level="info", reload=True)
    log.info("running")


# if __name__ == "__main__":
#     uvicorn.run("main:app", host='127.0.0.1', port=8080, ssl_keyfile="key.pem", ssl_certfile="cert.pem")