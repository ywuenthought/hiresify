# Copyright (c) 2025 Yifeng Wu
# All rights reserved.
# This file is not licensed for use, modification, or distribution without
# explicit written permission from the copyright holder.

"""Define middlewares to wrap around the application."""

import typing as ty

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class HTTPSOnlyMiddleware(BaseHTTPMiddleware):
    """A middleware that only allows for receiving HTTPS requests."""

    def __init__(self, app: ASGIApp) -> None:
        """Initialize an instance of HTTPSOnlyMiddleware."""
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: ty.Callable[[Request], ty.Awaitable[Response]],
    ) -> Response:
        """Dispatch an action on the given request."""
        if request.url.scheme != "https":
            raise HTTPException(
                detail="Only HTTPS requests are allowed.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        return await call_next(request)
