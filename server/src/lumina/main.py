"""FastAPI application entrypoint for Lumina server."""

from fastapi import FastAPI

app = FastAPI(
    title="Lumina Server",
    version="0.1.0",
    description="Lumina AI Desktop Pet Agent backend",
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0"}
