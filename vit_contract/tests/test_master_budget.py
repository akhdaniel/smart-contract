from odoo.tests.common import TransactionCase
from odoo.addons.vit_contract.tests.common import VitContractCommon

from odoo.exceptions import UserError
from odoo.tests import tagged

import logging
_logger = logging.getLogger(__name__)

@tagged('post_install', '-at_install')
class MasterBudgetTestCase(VitContractCommon):

	def test_vit_master_budget_count(cls):
		_logger.info(' -------------------- test record count -----------------------------------------')
		cls.assertEqual(
		    4,
		    len(cls.master_budgets)
		)