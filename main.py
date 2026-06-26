from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库表定义
class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    seat_width: int
    seat_depth: int
    back_angle: int
    leg_height: int
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 创建数据库
engine = create_engine("sqlite:///furniture.db")
SQLModel.metadata.create_all(engine)

# 接收参数的格式
class FurnitureParams(BaseModel):
    seat_width: int
    seat_depth: int
    back_angle: int
    leg_height: int

# 提供前端页面
@app.get("/")
def home():
    return FileResponse("index.html")
@app.get("/orders")
def orders_page():
    return FileResponse("orders.html")
# 生成家具，同时保存到数据库
@app.post("/api/generate")
def generate_furniture(params: FurnitureParams):
    # 保存到数据库
    order = Order(
        seat_width=params.seat_width,
        seat_depth=params.seat_depth,
        back_angle=params.back_angle,
        leg_height=params.leg_height,
    )
    with Session(engine) as session:
        session.add(order)
        session.commit()
        session.refresh(order)

    return JSONResponse(
        content={
            "status": "success",
            "message": "参数接收成功",
            "order_id": order.id,
            "received_params": {
                "座面宽度": f"{params.seat_width} mm",
                "座面深度": f"{params.seat_depth} mm",
                "靠背角度": f"{params.back_angle}°",
                "腿高":     f"{params.leg_height} mm",
            }
        },
        media_type="application/json; charset=utf-8"
    )

# 查询所有历史订单
@app.get("/api/orders")
def get_orders():
    with Session(engine) as session:
        orders = session.exec(select(Order)).all()
        return JSONResponse(
            content=[
                {
                    "id": o.id,
                    "座面宽度": f"{o.seat_width} mm",
                    "座面深度": f"{o.seat_depth} mm",
                    "靠背角度": f"{o.back_angle}°",
                    "腿高": f"{o.leg_height} mm",
                    "时间": o.created_at,
                }
                for o in orders
            ],
            media_type="application/json; charset=utf-8"
        )