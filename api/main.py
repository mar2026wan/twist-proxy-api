from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# الرابط الحقيقي المستخرج من ملف الـ HAR الخاص بك
BASE_TARGET_URL = "https://api.twistmena.com"

@app.api_route("/api/api", methods=["GET", "POST"])
@app.api_route("/", methods=["GET", "POST"])
async def proxy_handler(request: Request):
    try:
        data = await request.json()
        
        path = data.get("path", "")
        method = data.get("method", "GET").upper()
        custom_headers = data.get("headers", {})
        body = data.get("body", None)
        
        if not path.startswith("/"):
            path = "/" + path
        target_url = f"{BASE_TARGET_URL}{path}"
        
        # الـ Headers الرسمية الحديثة المستخرجة من الحزم غير المشفرة
        headers = {
            "User-Agent": "Twist-Mobile/11.1.1 (Android; 15; SM-A057F; music; ar-US)",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "platform": "android",
            "channel": "mobileapp",
            "app_version": "11.1.1",
            "appversion": "11.1.1"
        }
        headers.update(custom_headers)
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            if method == "GET":
                response = await client.get(target_url, headers=headers)
            elif method == "POST":
                response = await client.post(target_url, headers=headers, json=body)
            else:
                return Response(content="Method not supported", status_code=400)
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                media_type="application/json"
            )
            
    except Exception as e:
        return Response(
            content=f"{{\"error\": \"Proxy Internal Error\", \"details\": \"{str(e)}\"}}", 
            status_code=500, 
            media_type="application/json"
        )
