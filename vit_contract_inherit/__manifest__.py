#-*- coding: utf-8 -*-

{
	"name": "Vit Contract Inherited",
	"version": "1.0",
	"depends": [
		"base",
		"vit_contract",
        "ps_m2m_field_attachment_preview",
	],
	"author": "Akhmad Daniel Sembiring",
	"category": "Utility",
	"website": "http://vitraining.com",
	"images": [
		"static/description/images/main_screenshot.jpg"
	],
	"price": "100",
	"license": "OPL-1",
	"currency": "USD",
	"summary": "",
	"description": "",
	"data": [
        'security/groups.xml',
        'security/ir.model.access.csv',
        "view/menu.xml",
        "view/menu_operation.xml",
        'view/record_rule_vendor.xml',
		"view/izin_prinsip.xml",
        "view/job_izin_prinsip.xml",
        "view/budget_rkap.xml",
		#"view/kanwil_kancab.xml",
		"view/kontrak.xml",
        "view/izin_prinsip.xml",
        "view/izin_prinsip_line.xml",
		#"view/partner.xml",
		"view/payment.xml",
		"view/syarat_termin.xml",
        "view/termin.xml",
        "view/droping.xml",
        "view/kanwil_provinsi.xml",
        
	],
	"installable": True,
	"auto_install": False,
	"application": True,
	"odooVersion": 17
}