from odoo.tests.common import TransactionCase
from odoo.addons.vit_contract.tests.common import VitContractCommon

from odoo.exceptions import UserError
from odoo.tests import tagged

import logging
_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class SyaratTerminTestCase(VitContractCommon):

	def test_vit_syarat_termin_count(cls):
		_logger.info(' -------------------- test record count -----------------------------------------')
		cls.assertEqual(
		    4,
		    len(cls.syarat_termins)
		)