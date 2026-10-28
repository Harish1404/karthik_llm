from datetime import datetime, timezone
from app.ai.rag.data_loader import data_processor
from app.ai.rag.embed import embedding
from app.ai.rag.vector_store import vector_store
from app.utils.ids import generate_uuid


class RagPipeline:

    @staticmethod
    async def data_ingestion(file):
        uploaded_at = datetime.now(timezone.utc).isoformat()
        
        # 1. Process PDF, extract text per page, chunk, and compute hash
        content = await data_processor.process_file(file)
        file_hash = content["file_hash"]

        # 2. Check if identical file has already been ingested
        existing_doc = await vector_store.get_document_by_hash(file_hash)
        if existing_doc:
            return {
                "status": "already_ingested",
                "message": f"File '{existing_doc.get('filename')}' with identical content has already been ingested.",
                "document": existing_doc
            }

        # 3. Generate embeddings for the chunks
        chunks = content.get("chunks", [])
        chunk_texts = [c["text"] for c in chunks]
        embeddings = await embedding.embed_chunks(chunk_texts)

        # 4. Construct Document Record
        document_id = generate_uuid()
        ingested_at = datetime.now(timezone.utc).isoformat()
        document_record = {
            "document_id": document_id,
            "filename": getattr(file, "filename", "unnamed.pdf"),
            "file_hash": file_hash,
            "file_size_bytes": content["file_size_bytes"],
            "uploaded_at": uploaded_at,
            "ingested_at": ingested_at,
            "ingestion_status": "completed",
            "chunk_count": content["total_chunks"],
            "chunking_version": "v1",
            "embedding_model": embedding.model_name
        }

        # 5. Insert into ChromaDB
        await vector_store.insert(
            document_record=document_record,
            chunks=chunks,
            embeddings=embeddings
        )

        return {
            "status": "completed",
            "message": "File successfully processed and ingested into vector database.",
            "document": document_record
        }

    @staticmethod
    async def retrieve(query: str, n_results: int = 5, document_id: str | None = None):
        query_embedding = await embedding.embed_query(query)
        results = await vector_store.retrieve(
            query_embedding=query_embedding,
            n_results=n_results,
            document_id=document_id
        )
        return {
            "query": query,
            "total_results": len(results),
            "results": results
        }

    @staticmethod
    async def generation():
        pass


rag_pipeline = RagPipeline()
