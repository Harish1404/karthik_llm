from fastapi import FastAPI


app = FastAPI()


@app.get("/")
def landing_page():
    return {
        "message": "Vanakkam da maapla Pondi la irundhu"
    }



