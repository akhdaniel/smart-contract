{
    'name': 'Vendor Portal',
    'version': '17.0.1.0.0',
    'summary': 'Portal for vendors to manage their contracts, documents, and payments.',
    'author': 'Gemini',
    'depends': [
        'portal',
        'vit_contract',
        'website',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
