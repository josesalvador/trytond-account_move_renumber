# This file is part of the account_move_renumber module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountMoveRenumberTestCase(ModuleTestCase):
    'Test Account Move Renumber module'
    module = 'account_move_renumber'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountMoveRenumberTestCase))
    return suite