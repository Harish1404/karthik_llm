from fastapi import APIRouter, UploadFile
from fastapi.responses import PlainTextResponse

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile):
    
    binary_content = await file.read()
    text_content = binary_content.decode("utf-8")

    prompts = []

    for line in text_content.splitlines():
        if line.startswith("prompt:"):
            prompt = line.removeprefix("prompt:").strip()
            prompts.append(prompt)

    return prompts


