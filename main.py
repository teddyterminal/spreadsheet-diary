from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd

from services.ratings_service import RatingsService

START_RATING = 245
CSV_PATH = "ratings.csv"

service = RatingsService(CSV_PATH)


app = FastAPI()
# Serve static files under /static so API routes are not shadowed.
app.mount("/static", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
def root():
    return FileResponse("index.html")

undo_stack = []

@app.get("/data")
def get_data():
    df = service.decorate_df_columns()
    print(df.columns)
    return df.fillna("").to_dict(orient="records")

class Edit(BaseModel):
    row: int
    diff: float

@app.post("/edit")
def edit(edit: Edit):
    undo_stack.append(service.df.copy())

    service.df.loc[edit.row, "diff"] = edit.diff
    service.save_df()

    return {"status": "ok"}

@app.post("/undo")
def undo():
    global undo_stack
    if not undo_stack:
        return {"status": "empty"}

    df = undo_stack.pop()
    service.save_df(df)
    return {"status": "ok"}