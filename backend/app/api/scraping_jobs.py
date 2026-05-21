from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.celery_app import celery_app
from app.scrapers.registry import SCRAPER_REGISTRY
from app.tasks.scraping_tasks import scrape_source


router = APIRouter(
    prefix="/scraping-jobs",
    tags=["Scraping Jobs"],
)


class ScrapeSourceRequest(BaseModel):
    source_id: str
    limit: int = 10
    run_pipeline: bool = True


@router.get("/sources")
def list_available_scrapers():
    return {
        "available_scrapers": list(SCRAPER_REGISTRY.keys())
    }


@router.post("/run")
def run_scraping_job(request: ScrapeSourceRequest):
    if request.source_id not in SCRAPER_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"No scraper found for source_id: {request.source_id}",
        )

    if request.limit < 1 or request.limit > 50:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 50",
        )

    task = scrape_source.delay(
        source_id=request.source_id,
        limit=request.limit,
        run_pipeline=request.run_pipeline,
    )

    return {
        "task_id": task.id,
        "status": "queued",
        "source_id": request.source_id,
    }


@router.get("/{task_id}")
def get_scraping_job_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "state": result.state,
    }

    if result.state == "PENDING":
        response["message"] = "Task is waiting or does not exist yet."

    elif result.state == "STARTED":
        response["message"] = "Task is running."

    elif result.state == "SUCCESS":
        response["result"] = result.result

    elif result.state == "FAILURE":
        response["error"] = str(result.result)

    else:
        response["message"] = "Task state updated."

    return response