import os
import sys
import base64

import uvicorn
import ddddocr

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI


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


@app.post("/api/deepseek")
def recognize(req: ImageReq):
    try:
        # 去掉 data:image/jpeg;base64, 前缀
        if "," in req.image_base64:
            base64_str = req.image_base64.split(",")[-1]
        else:
            base64_str = req.image_base64

        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com")
        
        response = client.chat.completions.create(
            #model = "deepseek-v4-pro",
            #model = "deepseek-chat",
            model = "deepseek-vision",
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant"
                },
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": { "url": "data:image/jpeg;base64,{base64_str}" }
                        },
                        {
                            "type": "text",
                            "text": "请识别图片中白色背景上的4个字符，注意区分大小写。仅输出这4个字符，不要输出任何其他文字。"
                        }
                    ]
                },
            ],
            stream = False,
            reasoning_effort = "high",
            #extra_body= { "thinking": { "type": "disabled" } }
            extra_body= { "thinking": { "type": "enabled" } }
        )

        return {"code": 200, "result": response}
    except Exception as e:
        return {"code": 500, "message": str(e), "result": ""}


@app.post("/api/moonshot")
def recognize(req: ImageReq):
    try:
        # 去掉 data:image/jpeg;base64, 前缀
        if "," in req.image_base64:
            base64_str = req.image_base64.split(",")[-1]
        else:
            base64_str = req.image_base64

        client = OpenAI(
            api_key=os.environ.get('MOONSHOT_API_KEY'),
            base_url="https://api.moonshot.cn/v1")
        
        response = client.chat.completions.create(
            model = "kimi-k2.6",
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful assistant"
                },
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": { "url": f"data:image/jpeg;base64,{base64_str}" }
                        },
                        {
                            "type": "text",
                            "text": "请识别图片中白色背景上的4个字符，注意区分大小写。仅输出这4个字符，不要输出任何其他文字。"
                        }
                    ]
                },
            ],
            stream = False,
            extra_body= { "thinking": { "type": "disabled" } }
        )
        return {"code": 200, "result": response}
    except Exception as e:
        return {"code": 500, "message": str(e), "result": ""}




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
