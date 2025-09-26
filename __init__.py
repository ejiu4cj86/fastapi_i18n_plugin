import gettext
from pathlib import Path

from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from typing import Callable

# Define a type hint for the gettext function
GetText = Callable[[str], str]

async def get_locale_from_request(request: Request) -> str:
    return request.state.locale

async def get_gettext_func(request: Request) -> GetText:
    return request.state._

class FastAPIi18n:
    def __init__(self, localedir: Path, supported_locales: list[str], default_locale: str):
        self.localedir = localedir
        self.supported_locales = supported_locales
        self.default_locale = default_locale
        self.router = APIRouter()

        @self.router.get("/api/set-language/{locale}")
        async def set_language(locale: str, request: Request):
            if locale in self.supported_locales:
                response = JSONResponse(content={"status": "success", "locale": locale})
                response.set_cookie(key="locale", value=locale, max_age=30 * 24 * 3600)
                return response
            return JSONResponse(content={"status": "error", "message": "Unsupported locale"}, status_code=400)

        @self.router.get("/api/translations/{locale}")
        async def get_translations(locale: str):
            if locale not in self.supported_locales:
                return JSONResponse(status_code=404, content={"error": "Unsupported locale"})
            try:
                translation = gettext.translation("messages", localedir=self.localedir, languages=[locale])
                translations_dict = {}
                if hasattr(translation, '_catalog'):
                    for msgid, msgstr in translation._catalog.items():
                        if isinstance(msgid, str) and isinstance(msgstr, str):
                            translations_dict[msgid] = msgstr
                else:
                    raise RuntimeError("Could not access translation catalog. _catalog attribute missing.")
                return JSONResponse(content=translations_dict)
            except Exception as e:
                return JSONResponse(status_code=500, content={"error": f"Failed to load translations: {e}"})

    def init_app(self, app: FastAPI):
        app.add_middleware(I18nMiddleware, localedir=self.localedir, supported_locales=self.supported_locales, default_locale=self.default_locale)
        app.include_router(self.router)

class I18nMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, localedir: Path, supported_locales: list[str], default_locale: str):
        super().__init__(app)
        self.localedir = localedir
        self.supported_locales = supported_locales
        self.default_locale = default_locale

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        locale = request.cookies.get("locale", self.default_locale)
        if locale not in self.supported_locales:
            locale = self.default_locale

        try:
            translation = gettext.translation("messages", localedir=self.localedir, languages=[locale])
            request.state._ = translation.gettext
            request.state.locale = locale
        except FileNotFoundError:
            request.state._ = gettext.gettext
            request.state.locale = locale
        except Exception as e:
            request.state._ = gettext.gettext
            request.state.locale = locale

        request.app.state.jinja_env.globals["_"] = request.state._
        request.app.state.jinja_env.globals["locale"] = locale

        response = await call_next(request)
        return response
