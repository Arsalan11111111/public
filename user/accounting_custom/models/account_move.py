from odoo import _, fields, models, api
from odoo.osv import expression
import logging

import re
from collections import Counter

from datetime import timedelta,date,datetime
from dateutil.relativedelta import relativedelta
import datetime
_logger = logging.getLogger(__name__)

from odoo.tools.misc import format_date, get_lang


class InhAccountMove(models.Model):
    _inherit = 'stock.picking'


class InhAccountMove(models.Model):
    _inherit = 'account.move'

    delivery_address_tree = fields.Char("Delivery Address", compute = "_get_delivery_address")
    partners_tree = fields.Char("Partners",compute="_get_partners_tree")
    labels_tree = fields.Char("Labels", compute = "_get_labels_tree")

    def _get_labels_tree(self):
        for rec in self:
            if len(rec.invoice_line_ids) > 0:
                name = " "
                for lines in rec.invoice_line_ids:
                    if not lines.name:
                        name = name + ' '
                    else:
                        name = name + " " + lines.name + ", "
                name = name.rstrip(', ')
                rec.labels_tree = name
            else:
                rec.labels_tree = " "
    def _get_partners_tree(self):
        for rec in self:
            if len(rec.invoice_line_ids)>0:
                partner_ids =rec.invoice_line_ids.partner_id.ids
                partner_name = ''
                for lines in partner_ids:
                    lines = self.env['res.partner'].browse(lines)
                    partner_name = partner_name + ' '+ lines.name + ','
                partner_name = partner_name.rstrip(', ')
                rec.partners_tree = partner_name
            else:
                rec.partners_tree = ' '
    def _get_delivery_address(self):
        for rec in self:
            if rec.partner_delivery_address_id.name:
                fname = rec.partner_delivery_address_id.name
            else:
                fname = ''

            if rec.child_delivery_address_id.name:
                lname = rec.child_delivery_address_id.name
            else:
                lname = ''


            rec.delivery_address_tree = fname + ' ' + lname

class InhAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    partner_vat_computed = fields.Char("Partner VAT", compute="_get_partner_vat")
    remaining_days = fields.Integer(string="Remaining Days", compute='difference_date_remainig')

    def _get_partner_vat(self):
        for rec in self:
            if rec.partner_id.vat:
                rec.partner_vat_computed = rec.partner_id.vat
            else:
                rec.partner_vat_computed = ' '
    @api.depends('date_maturity')
    def difference_date_remainig(self):
        # fmt = '%Y-%m-%d'
        # today = date.today()
        for record in self:
            if record.date_maturity:
                # d1 = datetime.strptime(today, '%Y-%m-%d')

                # d2 = datetime.strptime(record.date_maturity, '%Y-%m-%d')
                # record.remaining_days =str(record/.date_maturity)
                # record.remaining_days =str((d2-d1).days)

                record.remaining_days = relativedelta(datetime.date.today(),record.date_maturity).days;
            else:

                record.remaining_days =0

       
        # return today.day - due_date.day - ((today.month, today.day) < (due_date.month, due_date.day))s



class PartnerLedgerCustomHandler(models.AbstractModel):
    _inherit = 'account.partner.ledger.report.handler'  

    def _get_report_line_move_line(self, options, aml_query_result, partner_line_id, init_bal_by_col_group, level_shift=0):
        if aml_query_result['payment_id']:
            caret_type = 'account.payment'
        else:
            caret_type = 'account.move.line'

        columns = []
        report = self.env['account.report']
        for column in options['columns']:
            col_expr_label = column['expression_label']
            if col_expr_label == 'ref':
                col_value = report._format_aml_name(aml_query_result['name'], aml_query_result['ref'], aml_query_result['move_name'])
            else:
                col_value = aml_query_result[col_expr_label] if column['column_group_key'] == aml_query_result['column_group_key'] else None

            if col_value is None:
                columns.append({})
            else:
                col_class = 'number'


                if col_expr_label == 'date_maturity':
                    formatted_value = format_date(self.env, fields.Date.from_string(col_value))
                    col_class = 'date'
                elif col_expr_label == 'amount_currency':
                    currency = self.env['res.currency'].browse(aml_query_result['currency_id'])
                    formatted_value = report.format_value(col_value, currency=currency, figure_type=column['figure_type'])
                elif col_expr_label == 'balance':
                    col_value += init_bal_by_col_group[column['column_group_key']]
                    formatted_value = report.format_value(col_value, figure_type=column['figure_type'], blank_if_zero=column['blank_if_zero'])
                # elif col_expr_label == 'remaining_days':
                #     formatted_value = report.format_value(col_value, currency=currency, figure_type=column['figure_type'])
                else:
                    if col_expr_label == 'ref':
                        col_class = 'o_account_report_line_ellipsis'
                    elif col_expr_label not in ('debit', 'credit'):
                        col_class = ''
                    formatted_value = report.format_value(col_value, figure_type=column['figure_type'])

                columns.append({
                    'name': formatted_value,
                    'no_format': col_value,
                    'class': col_class,
                })

        return {
            'id': report._get_generic_line_id('account.move.line', aml_query_result['id'], parent_line_id=partner_line_id),
            'parent_id': partner_line_id,
            'name': format_date(self.env, aml_query_result['date']),
            'class': 'text-muted' if aml_query_result['key'] == 'indirectly_linked_aml' else 'text',  # do not format as date to prevent text centering
            'columns': columns,
            'caret_options': caret_type,
            'level': 4 + level_shift,
        }





def _get_aml_values(self, options, partner_ids, offset=0, limit=None):
        rslt = {partner_id: [] for partner_id in partner_ids}

        partner_ids_wo_none = [x for x in partner_ids if x]
        directly_linked_aml_partner_clauses = []
        directly_linked_aml_partner_params = []
        indirectly_linked_aml_partner_params = []
        indirectly_linked_aml_partner_clause = 'aml_with_partner.partner_id IS NOT NULL'
        if None in partner_ids:
            directly_linked_aml_partner_clauses.append('account_move_line.partner_id IS NULL')
        if partner_ids_wo_none:
            directly_linked_aml_partner_clauses.append('account_move_line.partner_id IN %s')
            directly_linked_aml_partner_params.append(tuple(partner_ids_wo_none))
            indirectly_linked_aml_partner_clause = 'aml_with_partner.partner_id IN %s'
            indirectly_linked_aml_partner_params.append(tuple(partner_ids_wo_none))
        directly_linked_aml_partner_clause = '(' + ' OR '.join(directly_linked_aml_partner_clauses) + ')'

        ct_query = self.env['res.currency']._get_query_currency_table(options)
        queries = []
        all_params = []
        lang = self.env.lang or get_lang(self.env).code
        journal_name = f"COALESCE(journal.name->>'{lang}', journal.name->>'en_US')" if \
            self.pool['account.journal'].name.translate else 'journal.name'
        account_name = f"COALESCE(account.name->>'{lang}', account.name->>'en_US')" if \
            self.pool['account.account'].name.translate else 'account.name'
        report = self.env.ref('account_reports.partner_ledger_report')
        for column_group_key, group_options in report._split_options_per_column_group(options).items():
            tables, where_clause, where_params = report._query_get(group_options, 'strict_range')

            all_params += [
                column_group_key,
                *where_params,
                *directly_linked_aml_partner_params,
                column_group_key,
                *indirectly_linked_aml_partner_params,
                *where_params,
                group_options['date']['date_from'],
                group_options['date']['date_to'],
            ]

            # For the move lines directly linked to this partner
            queries.append(f'''
                SELECT
                    account_move_line.id,
                    account_move_line.date,
                    account_move_line.date_maturity,
                    account_move_line.name,
                    account_move_line.ref,
                    account_move_line.remaining_days,
                    account_move_line.company_id,
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    account_move_line.partner_id,
                    account_move_line.currency_id,
                    account_move_line.amount_currency,
                    account_move_line.matching_number,
                    ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                    ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                    ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                    account_move.name                                                                AS move_name,
                    account_move.move_type                                                           AS move_type,
                    account.code                                                                     AS account_code,
                    {account_name}                                                                   AS account_name,
                    journal.code                                                                     AS journal_code,
                    {journal_name}                                                                   AS journal_name,
                    %s                                                                               AS column_group_key,
                    'directly_linked_aml'                                                            AS key
                FROM {tables}
                JOIN account_move ON account_move.id = account_move_line.move_id
                LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                LEFT JOIN res_company company               ON company.id = account_move_line.company_id
                LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
                LEFT JOIN account_account account           ON account.id = account_move_line.account_id
                LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
                WHERE {where_clause} AND {directly_linked_aml_partner_clause}
                ORDER BY account_move_line.date, account_move_line.id
            ''')

            # For the move lines linked to no partner, but reconciled with this partner. They will appear in grey in the report
            queries.append(f'''
                SELECT
                    account_move_line.id,
                    account_move_line.date,
                    account_move_line.date_maturity,
                    account_move_line.name,
                    account_move_line.ref,
                    account_move_line.remaining_days,
                    account_move_line.company_id,
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    aml_with_partner.partner_id,
                    account_move_line.currency_id,
                    account_move_line.amount_currency,
                    account_move_line.matching_number,
                    CASE WHEN aml_with_partner.balance > 0 THEN 0 ELSE ROUND(
                        partial.amount * currency_table.rate, currency_table.precision
                    ) END                                                                               AS debit, 
                    CASE WHEN aml_with_partner.balance < 0 THEN 0 ELSE ROUND(
                        partial.amount * currency_table.rate, currency_table.precision
                    ) END                                                                               AS credit, 
                    - sign(aml_with_partner.balance) * ROUND(
                        partial.amount * currency_table.rate, currency_table.precision
                    )                                                                                   AS balance, 
                    account_move.name                                                                   AS move_name,
                    account_move.move_type                                                              AS move_type,
                    account.code                                                                        AS account_code,
                    {account_name}                                                                      AS account_name,
                    journal.code                                                                        AS journal_code,
                    {journal_name}                                                                      AS journal_name,
                    %s                                                                                  AS column_group_key,
                    'indirectly_linked_aml'                                                             AS key
                FROM {tables}
                    LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id,
                    account_partial_reconcile partial,
                    account_move,
                    account_move_line aml_with_partner,
                    account_journal journal,
                    account_account account
                WHERE
                    (account_move_line.id = partial.debit_move_id OR account_move_line.id = partial.credit_move_id)
                    AND account_move_line.partner_id IS NULL
                    AND account_move.id = account_move_line.move_id
                    AND (aml_with_partner.id = partial.debit_move_id OR aml_with_partner.id = partial.credit_move_id)
                    AND {indirectly_linked_aml_partner_clause}
                    AND journal.id = account_move_line.journal_id
                    AND account.id = account_move_line.account_id
                    AND {where_clause}
                    AND partial.max_date BETWEEN %s AND %s
                ORDER BY account_move_line.date, account_move_line.id
            ''')

        query = '(' + ') UNION ALL ('.join(queries) + ')'

        if offset:
            query += ' OFFSET %s '
            all_params.append(offset)

        if limit:
            query += ' LIMIT %s '
            all_params.append(limit)

        self._cr.execute(query, all_params)
        for aml_result in self._cr.dictfetchall():
            if aml_result['key'] == 'indirectly_linked_aml':

                # Append the line to the partner found through the reconciliation.
                if aml_result['partner_id'] in rslt:
                    rslt[aml_result['partner_id']].append(aml_result)

                # Balance it with an additional line in the Unknown Partner section but having reversed amounts.
                if None in rslt:
                    rslt[None].append({
                        **aml_result,
                        'debit': aml_result['credit'],
                        'credit': aml_result['debit'],
                        'balance': -aml_result['balance'],
                    })
            else:
                rslt[aml_result['partner_id']].append(aml_result)

        return rslt
