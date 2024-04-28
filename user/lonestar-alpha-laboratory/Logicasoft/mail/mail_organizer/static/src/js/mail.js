/*******************************************************************************
*
*    Copyright (c) 2017 LogicaSoft SPRL (<http://www.logicasoft.eu>).
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Affero General Public License as published
*    by the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Affero General Public License for more details.
*
*    You should have received a copy of the GNU Affero General Public License
*    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
*******************************************************************************/
odoo.define('lgk_mail_organizer.organizer_wizard', function(require) {
    'use strict';

    var Widget = require('web.Widget');
    var fieldRegistry = require('web.field_registry');

    Widget.include({
        init: function(){
            this._super.apply(this, arguments);
        },

        events: {
            'click .o_assign': '_onClickAssignTo',
            'click .o_remove': '_onClickRemove',
        },

        _onClickAssignTo: function(event){
            if(this.actions[Object.keys(this.actions)[0]]){
                var message_id = $(event.currentTarget).data('message-id');
                var action = {
                    type: 'ir.actions.act_window',
                    name: 'Assign message to',
                    res_model: 'mail.organizer',
                    view_mode: 'form',
                    view_type: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: {
                        default_message_id: message_id,
                    }
                };
                this.do_action(action)
            }
        },

        _onClickRemove: function(event){
            if(this.actions[Object.keys(this.actions)[0]]){
                var message_id = $(event.currentTarget).data('message-id');
                var action = {
                    type: 'ir.actions.act_window',
                    name: 'Delete message',
                    res_model: 'mail.remover',
                    view_mode: 'form',
                    view_type: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: {
                        default_message_id: message_id,
                    },
                };
                this.do_action(action);
            }
        },
    });
});