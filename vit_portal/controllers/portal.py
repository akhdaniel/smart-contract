
import base64
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

class VendorPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        contract_count = request.env['vit.kontrak'].search_count([
            ('partner_id', 'child_of', partner.id)
        ])
        values['contract_count'] = contract_count
        return values

    @http.route(['/my/contracts', '/my/contracts/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_contracts(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        domain = [('partner_id', 'child_of', partner.id)]

        contract_count = request.env['vit.kontrak'].search_count(domain)
        
        pager = portal_pager(
            url="/my/contracts",
            total=contract_count,
            page=page,
            step=self._items_per_page
        )
        
        contracts = request.env['vit.kontrak'].search(
            domain,
            limit=self._items_per_page,
            offset=pager['offset']
        )
        
        values.update({
            'contracts': contracts,
            'page_name': 'contract',
            'pager': pager,
            'default_url': '/my/contracts',
        })
        return request.render("vit_portal.portal_my_contracts", values)

    @http.route(['/my/contracts/<int:contract_id>'], type='http', auth="user", website=True)
    def portal_contract_detail(self, contract_id, **kw):
        try:
            contract_sudo = self._document_check_access('vit.kontrak', contract_id)
        except (AccessError, MissingError):
            return request.redirect('/my')
            
        values = {
            'contract': contract_sudo,
            'page_name': 'contract',
        }
        return request.render("vit_portal.portal_contract_detail", values)

    @http.route('/my/contracts/syarat/upload', type='http', auth="user", methods=['POST'], website=True)
    def portal_syarat_upload(self, **post):
        syarat_id = post.get('syarat_id')
        upload = post.get('attachment')

        if not syarat_id or not upload:
            return request.redirect('/my')

        syarat = request.env['vit.syarat_termin'].browse(int(syarat_id))
        if not syarat.exists():
            return request.redirect('/my')

        # Check access to the parent contract
        contract = syarat.termin_id.kontrak_id
        try:
            self._document_check_access('vit.kontrak', contract.id)
        except (AccessError, MissingError):
            return request.redirect('/my')

        encoded_file = base64.b64encode(upload.read())
        syarat.write({'document': encoded_file})

        return request.redirect('/my/contracts/%s' % contract.id)
