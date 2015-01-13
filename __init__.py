# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .account import *


def register():
    Pool.register(
        Move,
        RenumberMovesStart,
        module='account_move_renumber', type_='model')
    Pool.register(
        RenumberMoves,
        module='account_move_renumber', type_='wizard')
