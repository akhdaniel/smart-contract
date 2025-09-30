from odoo.tests.common import TransactionCase
from odoo.addons.vit_contract.tests.common import VitContractCommon

from odoo.exceptions import UserError
from odoo.tests import tagged

import logging
_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class JobIzinPrinsipTestCase(VitContractCommon):

	def test_vit_job_izin_prinsip_count(cls):
		_logger.info(' -------------------- test record count -----------------------------------------')
		cls.assertEqual(
		    4,
		    len(cls.job_izin_prinsips)
		)