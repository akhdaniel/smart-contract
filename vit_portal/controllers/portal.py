
import base64
from odoo import http
from odoo.exceptions import AccessError, MissingError
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

    def _portal_bank_values(self, contract):
        banks = contract.partner_id.sudo().bank_ids
        return {
            'selected_bank_id': contract.partner_bank_id.id if contract.partner_bank_id else False,
            'selected_bank': {
                'id': contract.partner_bank_id.id,
                'display_name': contract.partner_bank_id.display_name,
                'bank_name': contract.payment_bank_name,
                'acc_number': contract.payment_bank_acc_number,
                'acc_holder': contract.payment_bank_acc_holder,
            } if contract.partner_bank_id else False,
            'bank_accounts': [{
                'id': bank.id,
                'display_name': bank.display_name,
                'bank_name': bank.bank_id.name if bank.bank_id else '',
                'acc_number': bank.acc_number or '',
                'acc_holder': getattr(bank, 'acc_holder_name', False) or bank.partner_id.display_name,
            } for bank in banks],
        }

    @http.route('/my/contracts/payment-bank/info', type='json', auth='user', website=True)
    def portal_payment_bank_info(self, contract_id, **kw):
        try:
            contract = self._document_check_access('vit.kontrak', int(contract_id))
        except (AccessError, MissingError):
            return {'error': 'Kontrak tidak ditemukan atau tidak bisa diakses.'}
        return self._portal_bank_values(contract.sudo())

    @http.route('/my/contracts/payment-bank/save', type='json', auth='user', methods=['POST'], website=True)
    def portal_payment_bank_save(self, contract_id, partner_bank_id=False, bank_name=False, acc_number=False, **kw):
        try:
            contract = self._document_check_access('vit.kontrak', int(contract_id))
        except (AccessError, MissingError):
            return {'error': 'Kontrak tidak ditemukan atau tidak bisa diakses.'}

        contract = contract.sudo()
        if contract.stage_id.display_name != 'On Progress':
            return {'error': 'Rekening pembayaran hanya bisa diubah saat kontrak On Progress.'}

        partner_bank = False
        if partner_bank_id:
            partner_bank = request.env['res.partner.bank'].sudo().browse(int(partner_bank_id)).exists()
            if not partner_bank or partner_bank.partner_id != contract.partner_id:
                return {'error': 'Rekening tidak sesuai vendor kontrak.'}
        else:
            bank_name = (bank_name or '').strip()
            acc_number = (acc_number or '').strip()
            if not bank_name or not acc_number:
                return {'error': 'Nama Bank dan Nomor Rekening wajib diisi.'}

            bank = request.env['res.bank'].sudo().search([('name', '=ilike', bank_name)], limit=1)
            if not bank:
                bank = request.env['res.bank'].sudo().create({'name': bank_name})

            partner_bank = request.env['res.partner.bank'].sudo().search([
                ('partner_id', '=', contract.partner_id.id),
                ('acc_number', '=', acc_number),
                ('bank_id', '=', bank.id),
            ], limit=1)
            if not partner_bank:
                partner_bank = request.env['res.partner.bank'].sudo().create({
                    'partner_id': contract.partner_id.id,
                    'bank_id': bank.id,
                    'acc_number': acc_number,
                })

        contract.write({'partner_bank_id': partner_bank.id})
        contract.termin_ids.sudo().write({
            'nama_bank': partner_bank.bank_id.name if partner_bank.bank_id else '',
            'nomor_rekening': partner_bank.acc_number or '',
        })
        return self._portal_bank_values(contract)

    @http.route('/my/contracts/payment-bank/delete', type='json', auth='user', methods=['POST'], website=True)
    def portal_payment_bank_delete(self, contract_id, partner_bank_id=False, **kw):
        try:
            contract = self._document_check_access('vit.kontrak', int(contract_id))
        except (AccessError, MissingError):
            return {'error': 'Kontrak tidak ditemukan atau tidak bisa diakses.'}

        contract = contract.sudo()
        if contract.stage_id.display_name != 'On Progress':
            return {'error': 'Rekening pembayaran hanya bisa dihapus saat kontrak On Progress.'}
        if not partner_bank_id:
            return {'error': 'Rekening yang akan dihapus belum dipilih.'}

        partner_bank = request.env['res.partner.bank'].sudo().browse(int(partner_bank_id)).exists()
        if not partner_bank or partner_bank.partner_id != contract.partner_id:
            return {'error': 'Rekening tidak sesuai vendor kontrak.'}

        if contract.partner_bank_id == partner_bank:
            contract.write({'partner_bank_id': False})
            contract.termin_ids.sudo().write({
                'nama_bank': False,
                'nomor_rekening': False,
            })
        try:
            partner_bank.unlink()
        except Exception as error:
            return {'error': str(error)}

        request.env.invalidate_all()
        contract = request.env['vit.kontrak'].sudo().browse(contract.id).exists()
        return self._portal_bank_values(contract)
