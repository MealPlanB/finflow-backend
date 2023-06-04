from fastapi import FastAPI
from starlette.responses import JSONResponse
from routers import users, trade, charts
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

app = FastAPI()

app.include_router(users.router)
app.include_router(trade.router, prefix="/trade")
app.include_router(charts.router, prefix="/charts")


@app.get("/openapi.json")
async def get_open_api_endpoint():
    return JSONResponse(get_openapi(title="API Documentation", version=1, routes=app.routes))


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Documentation")


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Documentation", redoc=True)

