# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.account_move_renumber.tests.test_account_move_renumber import suite
except ImportError:
    from .test_account_move_renumber import suite

__all__ = ['suite']
