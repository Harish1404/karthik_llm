from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from pydantic import BaseModel, Field
from app.ai.rag.pipeline import rag_pipeline

router = APIRouter(tags=["File"])


class RetrieveRequest(BaseModel):
    query: str = Field(..., description="Query text to search for semantically relevant chunks")
    n_results: int = Field(5, ge=1, le=50, description="Number of chunks to retrieve")
    document_id: str | None = Field(None, description="Optional document ID to restrict search to a specific document")


@router.post("/upload")
@router.post("/file/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Only PDF files are supported currently."
        )

    try:
        return await rag_pipeline.data_ingestion(file)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process and ingest file: {str(e)}"
        )


@router.post("/retrieve")
@router.post("/file/retrieve")
async def retrieve_chunks(request: RetrieveRequest):
    try:
        return await rag_pipeline.retrieve(
            query=request.query,
            n_results=request.n_results,
            document_id=request.document_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve chunks: {str(e)}"
        )
