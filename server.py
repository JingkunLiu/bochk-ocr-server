import ddddocr
import base64
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys

app = FastAPI(title="Captcha OCR API", version="1.0")

# 配置 CORS，允许油猴脚本跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 ddddocr (show_ad=False 防止在控制台打印广告)
ocr = ddddocr.DdddOcr(show_ad=False)
ocr.set_ranges(6) # 设置识别范围为数字和字母 "0-9a-zA-Z"

class ImageReq(BaseModel):
    image_base64: str

@app.post("/api/recognize")
def recognize(req: ImageReq):
    try:
        # 去掉 data:image/jpeg;base64, 前缀
        if "," in req.image_base64:
            base64_str = req.image_base64.split(",")[-1]
        else:
            base64_str = req.image_base64
            
        img_bytes = base64.b64decode(base64_str)
        res = ocr.classification(img_bytes)
        return {"code": 200, "result": res}
    except Exception as e:
        return {"code": 500, "message": str(e), "result": ""}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
