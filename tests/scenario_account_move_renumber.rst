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
    >>> today = datetime.date.today()

Create database::

    >>> config = config.set_trytond()
    >>> config.pool.test = True

Install account_move_renumber::

    >>> Module = Model.get('ir.module.module')
    >>> modules = Module.find([
    ...         ('name', '=', 'account_move_renumber'),
    ...         ])
    >>> Module.install([x.id for x in modules], config.context)
    >>> Wizard('ir.module.module.install_upgrade').execute('upgrade')

Create company::

    >>> Currency = Model.get('currency.currency')
    >>> CurrencyRate = Model.get('currency.currency.rate')
    >>> Company = Model.get('company.company')
    >>> Party = Model.get('party.party')
    >>> company_config = Wizard('company.company.config')
    >>> company_config.execute('company')
    >>> company = company_config.form
    >>> party = Party(name='Dunder Mifflin')
    >>> party.save()
    >>> company.party = party
    >>> currencies = Currency.find([('code', '=', 'USD')])
    >>> if not currencies:
    ...     currency = Currency(name='U.S. Dollar', symbol='$', code='USD',
    ...         rounding=Decimal('0.01'), mon_grouping='[3, 3, 0]',
    ...         mon_decimal_point='.', mon_thousands_sep=',')
    ...     currency.save()
    ...     CurrencyRate(date=today + relativedelta(month=1, day=1),
    ...         rate=Decimal('1.0'), currency=currency).save()
    ... else:
    ...     currency, = currencies
    >>> company.currency = currency
    >>> company_config.execute('add')
    >>> company, = Company.find()

Reload the context::

    >>> User = Model.get('res.user')
    >>> config._context = User.get_preferences(True, config.context)

Create fiscal year::

    >>> FiscalYear = Model.get('account.fiscalyear')
    >>> Sequence = Model.get('ir.sequence')
    >>> SequenceStrict = Model.get('ir.sequence.strict')
    >>> fiscalyear = FiscalYear(name='%s' % today.year)
    >>> fiscalyear.start_date = today + relativedelta(month=1, day=1)
    >>> fiscalyear.end_date = today + relativedelta(month=12, day=31)
    >>> fiscalyear.company = company
    >>> post_move_sequence = Sequence(name='%s' % today.year,
    ...     code='account.move', company=company)
    >>> post_move_sequence.save()
    >>> fiscalyear.post_move_sequence = post_move_sequence
    >>> fiscalyear.save()
    >>> FiscalYear.create_period([fiscalyear.id], config.context)
    >>> period = fiscalyear.periods[0]

Create chart of accounts::

    >>> AccountTemplate = Model.get('account.account.template')
    >>> Account = Model.get('account.account')
    >>> account_template, = AccountTemplate.find([('parent', '=', None)])
    >>> create_chart = Wizard('account.create_chart')
    >>> create_chart.execute('account')
    >>> create_chart.form.account_template = account_template
    >>> create_chart.form.company = company
    >>> create_chart.execute('create_account')
    >>> receivable, = Account.find([
    ...         ('kind', '=', 'receivable'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> payable, = Account.find([
    ...         ('kind', '=', 'payable'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> revenue, = Account.find([
    ...         ('kind', '=', 'revenue'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> expense, = Account.find([
    ...         ('kind', '=', 'expense'),
    ...         ('company', '=', company.id),
    ...         ])
    >>> cash, = Account.find([
    ...         ('kind', '=', 'other'),
    ...         ('company', '=', company.id),
    ...         ('name', '=', 'Main Cash'),
    ...         ])
    >>> create_chart.form.account_receivable = receivable
    >>> create_chart.form.account_payable = payable
    >>> create_chart.execute('create_properties')

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
    ...     move.save()
    ...     Move.post([move.id], config.context)

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
