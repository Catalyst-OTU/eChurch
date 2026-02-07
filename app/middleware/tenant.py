from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from config.logger import log


class TenantMiddleware(BaseHTTPMiddleware):
    def dispatch(self, request: Request, call_next):
        # Extract subdomain from custom header
        subdomain = request.headers.get("subdomain", "public")

        # Store schema in request state
        request.state.schema = subdomain
        log.debug(f"Schema extracted from headers: {subdomain}")

        response = call_next(request)
        return response
    

    
# class TenantMiddleware(BaseHTTPMiddleware):
#     def dispatch(self, request: Request, call_next):
#         host = request.url.netloc
#         url_components = host.split('.')

#         if len(url_components) < 2:
#             subdomain = "public"
#         else:
#             subdomain = url_components[0]

#         request.state.schema = subdomain
#         log.debug(f"schema extracted from incoming url: {subdomain}")
#         response = call_next(request)
#         return response
