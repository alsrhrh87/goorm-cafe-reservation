from database import database, reservations
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, FileResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select, bindparam
from typing import List

# FastAPI 앱 생성
app = FastAPI()

# ✅ 정적 파일 먼저 mount
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ 템플릿 설정
templates = Jinja2Templates(directory="templates")

# ✅ 보안 설정
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != "2955":
        raise HTTPException(status_code=401, detail="Unauthorized")

# ✅ DB 연결
@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# ✅ 예약 폼
@app.get("/", response_class=HTMLResponse)
async def reservation_form(request: Request):
    # cloud_url을 템플릿으로 넘김 (jinja2 안에서 url_for 직접 호출 X)
    cloud_url = request.url_for("static", path="img/cloud.jpg")
    return templates.TemplateResponse("form.html", {
        "request": request,
        "cloud_url": cloud_url
    })

# ✅ 예약 저장
@app.post("/reserve")
async def reserve(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    time: str = Form(...),
    drink: str = Form(...),
    size: str = Form(...),
    temperature: str = Form(...),
    inquiry: str = Form(...)
):
    drink_detail = f"{drink} ({size}, {temperature})"
    query = reservations.insert().values(
        name=name,
        phone=phone,
        time=time,
        drink=drink_detail,
        inquiry=inquiry
    )
    await database.execute(query)

    with open("예약정보.txt", "a", encoding="utf-8") as f:
        f.write(f"{name}, {phone}, {time}, {drink_detail}, 요청사항: {inquiry}\n")

    cloud_url = request.url_for("static", path="img/cloud.jpg")
    return templates.TemplateResponse("form.html", {
        "request": request,
        "message": "예약 완료되었습니다!",
        "cloud_url": cloud_url
    })
@app.post("/delete")
async def delete_reservation(
    request: Request,
    delete_ids: List[int] = Form(...),
    credentials: HTTPBasicCredentials = Depends(verify_admin)
):
    query = reservations.delete().where(reservations.c.id.in_(delete_ids))
    await database.execute(query)

    return templates.TemplateResponse("list.html", {
        "request": request,
        "message": "예약이 삭제되었습니다.",
        "reservations": [dict(row) for row in await database.fetch_all(reservations.select())],
        "search": None
    })

# ✅ 관리자 리스트
@app.get("/list", response_class=HTMLResponse)
async def show_reservations(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(verify_admin),
    search: str = Query(None)
):
    try:
        if search:
            query = select(reservations).where(reservations.c.name.like(bindparam("search")))
            query = query.params(search=f"%{search}%")
        else:
            query = reservations.select()

        rows = await database.fetch_all(query)
        return templates.TemplateResponse("list.html", {
            "request": request,
            "reservations": [dict(row) for row in rows],
            "search": search
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return PlainTextResponse("에러 발생: " + str(e), status_code=500)

