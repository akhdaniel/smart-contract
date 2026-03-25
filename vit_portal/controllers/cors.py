from odoo import http
from odoo.http import request

ALLOWED_ORIGIN = 'https://smc-vendor.xerpium.com'
ALLOWED_METHODS = 'GET, POST, OPTIONS'
ALLOWED_HEADERS = 'Authorization, Content-Type, Accept, Origin, X-Requested-With'


class CorsController(http.Controller):
    @http.route('/web/session/authenticate', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def preflight_authenticate(self, **kw):
        headers = {
            'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': ALLOWED_METHODS,
            'Access-Control-Allow-Headers': ALLOWED_HEADERS,
        }
        return request.make_response('', headers=headers)

    @http.route('/web/<path:path>', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def preflight_web(self, path, **kw):
        headers = {
            'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
            'Access-Control-Allow-Credentials': 'true',
            'Access-Control-Allow-Methods': ALLOWED_METHODS,
            'Access-Control-Allow-Headers': ALLOWED_HEADERS,
        }
        return request.make_response('', headers=headers)
