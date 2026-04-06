from odoo import api, http
import odoo.modules.registry
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.addons.web.controllers.session import Session
from odoo.addons.web.controllers.dataset import DataSet


ALLOWED_ORIGIN = "https://smc-vendor.xerpium.com"
CORS_HEADERS = [
    ("Access-Control-Allow-Origin", ALLOWED_ORIGIN),
    ("Access-Control-Allow-Credentials", "true"),
    ("Access-Control-Allow-Headers", "Content-Type"),
    ("Access-Control-Allow-Methods", "POST, OPTIONS"),
    ("Vary", "Origin"),
]


def _set_cors_headers():
    origin = request.httprequest.headers.get("Origin")
    if origin != ALLOWED_ORIGIN:
        return
    for header, value in CORS_HEADERS:
        request.future_response.headers[header] = value


def _options_response():
    return request.make_response("", headers=CORS_HEADERS)


class VendorPortalCorsSession(Session):
    @http.route(
        "/web/session/authenticate",
        type="http",
        auth="none",
        csrf=False,
        methods=["OPTIONS"],
        cors=ALLOWED_ORIGIN,
    )
    def vendor_portal_authenticate_options(self, **kwargs):
        return _options_response()

    @http.route(
        "/web/session/get_session_info",
        type="http",
        auth="none",
        csrf=False,
        methods=["OPTIONS"],
        cors=ALLOWED_ORIGIN,
    )
    def vendor_portal_session_info_options(self, **kwargs):
        return _options_response()

    @http.route(
        "/web/session/destroy",
        type="http",
        auth="none",
        csrf=False,
        methods=["OPTIONS"],
        cors=ALLOWED_ORIGIN,
    )
    def vendor_portal_destroy_options(self, **kwargs):
        return _options_response()

    @http.route(
        "/web/session/authenticate",
        type="json",
        auth="none",
        csrf=False,
        cors=ALLOWED_ORIGIN,
    )
    def authenticate(self, db, login, password, base_location=None):
        _set_cors_headers()
        if not http.db_filter([db]):
            raise AccessError("Database not found.")

        pre_uid = request.session.authenticate(db, login, password)
        if pre_uid != request.session.uid:
            return {"uid": None}

        request.session.db = db
        registry = odoo.modules.registry.Registry(db)
        with registry.cursor() as cr:
            env = api.Environment(cr, request.session.uid, request.session.context)
            if not request.db:
                http.root.session_store.rotate(request.session, env)
                request.future_response.set_cookie(
                    "session_id",
                    request.session.sid,
                    max_age=http.get_session_max_inactivity(env),
                    httponly=True,
                    secure=True,
                    samesite="None",
                )
            return env["ir.http"].session_info()

    @http.route(
        "/web/session/get_session_info",
        type="json",
        auth="user",
        csrf=False,
        cors=ALLOWED_ORIGIN,
    )
    def get_session_info(self):
        _set_cors_headers()
        request.session.touch()
        return request.env["ir.http"].session_info()

    @http.route(
        "/web/session/destroy",
        type="json",
        auth="user",
        csrf=False,
        cors=ALLOWED_ORIGIN,
    )
    def destroy(self):
        _set_cors_headers()
        request.session.logout()


class VendorPortalCorsDataset(DataSet):
    @http.route(
        [
            "/web/dataset/call_kw",
            "/web/dataset/call_kw/",
            "/web/dataset/call_kw/<path:path>",
        ],
        type="http",
        auth="none",
        csrf=False,
        methods=["OPTIONS"],
        cors=ALLOWED_ORIGIN,
    )
    def vendor_portal_call_kw_options(self, **kwargs):
        return _options_response()

    @http.route(
        [
            "/web/dataset/call_kw",
            "/web/dataset/call_kw/",
            "/web/dataset/call_kw/<path:path>",
        ],
        type="json",
        auth="user",
        csrf=False,
        cors=ALLOWED_ORIGIN,
    )
    def call_kw(self, model, method, args, kwargs, path=None):
        _set_cors_headers()
        return self._call_kw(model, method, args, kwargs)
