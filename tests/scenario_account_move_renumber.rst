==============================
Account Move Renumber Scenario
==============================

=============
General Setup
=============

Imports::

    >>> import datetime
    >>> from dateutil.relativedelta import relativedelta
    >>> from decimal import Decimal
    >>> from proteus import config, Model, Wizard
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company
    >>> from trytond.modules.account.tests.tools import create_fiscalyear, \
    ...     create_chart, get_accounts, create_tax, set_tax_code
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install account_move_renumber::

    >>> Module = Model.get('ir.module')
    >>> modules = Module.find([
    ...         ('name', '=', 'account_move_renumber'),
    ...         ])
    >>> Module.install([x.id for x in modules], config.context)
    >>> Wizard('ir.module.install_upgrade').execute('upgrade')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create fiscal year::

    >>> fiscalyear = create_fiscalyear(company)
    >>> fiscalyear.click('create_period')
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> _ = create_chart(company)
    >>> accounts = get_accounts(company)
    >>> receivable = accounts['receivable']
    >>> revenue = accounts['revenue']
    >>> expense = accounts['expense']
    >>> cash = accounts['cash']

Create parties::

    >>> Party = Model.get('party.party')
    >>> customer = Party(name='Customer')
    >>> customer.save()

Configure Cash Journal to allow cancel moves::

    >>> Journal = Model.get('account.journal')
    >>> journal_cash, = Journal.find([
    ...         ('code', '=', 'CASH'),
    ...         ])
    >>> journal_cash.update_posted = True
    >>> journal_cash.save()

Create and post Moves in Cash Journal::

    >>> Move = Model.get('account.move')
    >>> for i in range(10):
    ...     move = Move()
    ...     move.period = period
    ...     move.journal = journal_cash
    ...     move.date = period.start_date
    ...     line = move.lines.new()
    ...     line.account = cash
    ...     line.debit = Decimal(42 + i)
    ...     line = move.lines.new()
    ...     line.account = receivable
    ...     line.credit = Decimal(42 + i)
    ...     line.party = customer
    ...     move.click('post')

Check post numbers::

    >>> moves = Move.find([], order=[('id', 'ASC')])
    >>> len(moves)
    10
    >>> all(move.post_number == str(i + 1) for i, move in enumerate(moves))
    True

Cancel and delete some moves::

    >>> Move.draft([m.id for m in moves[2:4]], config.context)
    >>> moves[2].delete()
    >>> moves[3].delete()

Renumber moves::

    >>> renumber_moves = Wizard('account.move.renumber')
    >>> renumber_moves.form.fiscalyear = fiscalyear
    >>> renumber_moves.form.first_number = 1
    >>> renumber_moves.execute('renumber')

Check post numbers after renumbering::

    >>> moves = Move.find([], order=[('id', 'ASC')])
    >>> len(moves)
    8
    >>> all(move.post_number == str(i + 1) for i, move in enumerate(moves))
    True
    >>> moves[-1].post_number
    u'8'
