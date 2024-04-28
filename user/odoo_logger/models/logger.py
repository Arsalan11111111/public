# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, http, _
import json
import requests
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)


class OdooLogger(models.AbstractModel):
    _name = 'odoo.logger'
    _description = 'Odoo Logger'

    def odoolog(self, title, content='', type='info'):
        if type == 'debug':
            _logger.debug(
                '''
                
                |||||||||||  %s  |||||||||||
                
                %s
                
                ''' % (title, content)
            )
        elif type == 'error':
            _logger.error(
                '''
                
                |||||||||||  %s  |||||||||||
                
                %s
                
                ''' % (title, content)
            )
        else:
            _logger.info(
                '''
                
                |||||||||||  %s  |||||||||||
                
                %s
                
                ''' % (title, content)
            )
