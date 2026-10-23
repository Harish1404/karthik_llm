from fastapi import FastAPI
from app.routes import file

app = FastAPI()


@app.get("/")
def landing_page():
    return {
        "message": "Vanakkam da maapla Pondi la irundhu"
    }

app.include_router(file.router)


