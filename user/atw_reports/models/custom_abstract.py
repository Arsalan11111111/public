# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from num2words import num2words

import logging
_logger = logging.getLogger(__name__)


class CustomAbstract(models.AbstractModel):
    _name = 'custom.abstract'
    _description = '''
        This abstract model consists of general methods
        need for the custom reports.
    '''

    @api.model
    def get_amount_to_words(self, amount):
        """
            Need to call the num2words method twice because
            by default the digit after point is pronounced
            as Example: ".88" = eight eight, but expected eighty eight 
        """
        amount = round(amount, 3)
        amount_split_list = str(amount).split(".")
        rial_digit = int(amount_split_list[0])
        baisa_digit = int(amount_split_list[1])

        _logger.debug(
            '''
            Amount Split List: %s
            Omani Rial: %s 
            Baisa: %s
            
            ''' % (amount_split_list, rial_digit, baisa_digit)
        )

        rial = num2words(rial_digit, lang='en_IN')
        baisa = num2words(baisa_digit, lang='en_IN')
        amount_words = 'Rial Omani ' + rial.capitalize() + ' & ' \
            + baisa + ' Baisa Only.'
        amount_words = amount_words.replace(",", "")
        return amount_words
