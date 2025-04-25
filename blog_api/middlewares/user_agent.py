from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class UserAgentMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        blocked_agents = [
            "curl",
            "httpie",
            "wget",
            "python",
            "java",
            "libwww",
            "perl",
            "ruby",
            "scrapy",
            "bot",
            "spider",
            "crawler",
            "scanner",
            "axios",
            "go-http-client",
            "okhttp",
            "PostmanRuntime",
        ]

        user_agent = request.headers.get("user-agent").lower()

        if user_agent == "" or user_agent is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "User-Agent empty"},
            )

        for agent in blocked_agents:
            if agent in user_agent:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "User-Agent blocked"},
                )

        return await call_next(request)
