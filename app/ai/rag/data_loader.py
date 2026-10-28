import pymupdf
from app.core.security import get_file_hash


class DataPreprocessor:

    async def load_pdf(self, file) -> dict:
        pdf_bytes = await file.read()
        file_hash = get_file_hash(pdf_bytes)
        file_size_bytes = len(pdf_bytes)

        pages = []
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
            for page in pdf:
                page_text = page.get_text()
                if page_text and page_text.strip():
                    pages.append({
                        "page_number": page.number + 1,
                        "text": page_text
                    })

        return {
            "file_bytes": pdf_bytes,
            "file_hash": file_hash,
            "file_size_bytes": file_size_bytes,
            "pages": pages
        }

    def chunk_pages(self, pages: list[dict], chunk_size: int = 200, overlap: int = 50) -> list[dict]:
        chunks = []
        chunk_index = 0
        step = max(1, chunk_size - overlap)

        for page in pages:
            page_number = page["page_number"]
            words = page["text"].split()
            if not words:
                continue

            for start in range(0, len(words), step):
                chunk_words = words[start:start + chunk_size]
                chunk_text = " ".join(chunk_words)
                chunks.append({
                    "chunk_index": chunk_index,
                    "page_number": page_number,
                    "text": chunk_text
                })
                chunk_index += 1

                if start + chunk_size >= len(words):
                    break

        return chunks

    async def process_file(self, file) -> dict:
        pdf_data = await self.load_pdf(file)
        chunks = self.chunk_pages(pdf_data["pages"])
        return {
            "file_hash": pdf_data["file_hash"],
            "file_size_bytes": pdf_data["file_size_bytes"],
            "total_chunks": len(chunks),
            "chunks": chunks
        }


data_processor = DataPreprocessor()
process_file = data_processor.process_file
