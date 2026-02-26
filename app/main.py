import os

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title="EFEFIC-FDVP20261-CI-CD API Gateway",
    description="API Gateway centralizado para los microservicios",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "users": os.getenv("USERS_SERVICE_URL", "http://users-service:8002"),
    "broadcast": os.getenv("BROADCAST_SERVICE_URL", "http://broadcast-service:8003"),
}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "efefic-fdvp20261-api-gateway",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    return {"message": "EFEFIC-FDVP20261-CI-CD API Gateway", "docs": "/docs"}


@app.api_route(
    "/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(
            status_code=404, detail=f"Servicio '{service}' no encontrado"
        )

    target_url = f"{SERVICES[service]}/{path}"
    body = await request.body()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                content=body,
                params=dict(request.query_params),
                timeout=30.0,
            )
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code,
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503, detail=f"Servicio '{service}' no disponible"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
