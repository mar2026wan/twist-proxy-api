from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

# 1. تفعيل CORS للسماح لأي تطبيق بالوصول إلى البروكسي الخاص بك
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# النطاق الأساسي الخاص بـ Twist Music (الذي يوجه البروكسي الطلبات إليه)
BASE_TARGET_URL = "https://api.twistmena.com" # قم بتعديله إلى رابط الـ API الأساسي للمنصة

@app.post("/api/api")
async def proxy_handler(request: Request):
    try:
        # استقبال البيانات القادمة من الـ Request (الـ Payload)
        data = await request.json()
        
        path = data.get("path", "")
        method = data.get("method", "GET").upper()
        custom_headers = data.get("headers", {})
        body = data.get("body", None)
        
        # تركيب الرابط النهائي المستهدف
        target_url = f"{BASE_TARGET_URL}{path}"
        
        # إعداد الـ Headers الافتراضية مع دمج الـ Headers الممررة من المستخدم
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
            "Content-Type": "application/json",
        }
        headers.update(custom_headers)
        
        # إرسال الطلب برمجياً إلى خوادم المنصة باستخدام httpx
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(target_url, headers=headers)
            elif method == "POST":
                response = await client.post(target_url, headers=headers, json=body)
            else:
                return Response(content="Method not supported", status_code=400)
            
            # إعادة النتيجة القادمة من السيرفر الأصلي كما هي للمستخدم
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type="application/json"
            )
            
    except Exception as e:
        return Response(content=f"{{\"error\": \"{str(e)}\"}}", status_code=500, media_type="application/json")
