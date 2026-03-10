import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from routes import router

app = FastAPI()


@app.middleware("http")
async def normalize_api_prefix(request: Request, call_next):
    if request.scope.get("path", "").startswith("/api/"):
        request.scope["path"] = request.scope["path"][4:] or "/"
    return await call_next(request)

app.include_router(router)

@app.get("/health", response_model=dict)
async def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    # Inline dark‑theme HTML landing page
    html = """
    <!DOCTYPE html>
    <html lang='en'>
    <head>
        <meta charset='UTF-8'>
        <meta name='viewport' content='width=device-width, initial-scale=1.0'>
        <title>DemoPilot – AI‑Powered Demo Rehearsal</title>
        <style>
            body { background:#111; color:#eee; font-family:Arial,Helvetica,sans-serif; margin:0; padding:2rem; }
            a { color:#1ea7fd; }
            .card { background:#222; padding:1rem 1.5rem; margin-bottom:1rem; border-radius:8px; }
            h1, h2 { color:#fff; }
            ul { list-style:none; padding:0; }
            li { margin:0.5rem 0; }
            .endpoint { font-family:monospace; background:#333; padding:0.2rem 0.5rem; border-radius:4px; }
        </style>
    </head>
    <body>
        <div class='card'>
            <h1>DemoPilot</h1>
            <p>Transform your pitch with AI‑driven rehearsal and feedback, ensuring confidence and success in high‑stakes presentations.</p>
        </div>
        <div class='card'>
            <h2>Available API Endpoints</h2>
            <ul>
                <li><span class='endpoint'>GET /health</span> – health check</li>
                <li><span class='endpoint'>POST /auth/signup</span> – create a new user</li>
                <li><span class='endpoint'>POST /auth/login</span> – obtain JWT token</li>
                <li><span class='endpoint'>POST /demos</span> – create a demo</li>
                <li><span class='endpoint'>GET /demos</span> – list demos</li>
                <li><span class='endpoint'>GET /demos/{demo_id}</span> – demo details</li>
                <li><span class='endpoint'>PATCH /demos/{demo_id}</span> – update demo</li>
                <li><span class='endpoint'>POST /rehearsals</span> – submit a rehearsal recording</li>
                <li><span class='endpoint'>GET /rehearsals</span> – list rehearsals</li>
                <li><span class='endpoint'>POST /feedback</span> – generate AI feedback for a rehearsal</li>
                <li><span class='endpoint'>POST /scripts</span> – generate refined pitch script</li>
            </ul>
        </div>
        <div class='card'>
            <h2>Tech Stack</h2>
            <ul>
                <li>FastAPI 0.115.0</li>
                <li>PostgreSQL via SQLAlchemy 2.0.35</li>
                <li>DigitalOcean Serverless Inference (openai‑gpt‑oss‑120b)</li>
                <li>Python 3.12+</li>
            </ul>
        </div>
        <div class='card'>
            <p>API docs: <a href='/docs'>Swagger UI</a> | <a href='/redoc'>ReDoc</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
