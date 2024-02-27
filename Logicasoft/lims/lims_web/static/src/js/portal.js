/** @odoo-module alias=lims_web.portal */

import core from 'web.core';
import websiteNavbarData from 'website.navbar';
import Dialog from 'web.Dialog';
import publicWidget from 'web.public.widget';
import {registry} from '@web/core/registry';

var _t = core._t;
var qweb = core.qweb;

publicWidget.registry.portalSearchPanel.include({
    /**
     * @override
     */
    start: function () {
        this._super.apply(this, arguments);
        this.$('input[name="search"]').attr('placeholder', _t('Search'));
    },
});

var LimsConfigDialog = Dialog.extend({
    events: _.extend({}, Dialog.prototype.events, {
        'click input.o_switch_lims_config': '_onSwitchClick',
        'click a.o_remove_inactive_page': '_onRemoveInactivePageClick',
    }),

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onSwitchClick: function (ev) {
        var $currentTarget = $(ev.currentTarget);
        this._rpc({
            route: '/my/lims_config_handler',
            params: {
                data: $currentTarget.data(),
            },
        });
    },
    /**
     * @private
     * @param {MouseEvent} ev
     */
    _onRemoveInactivePageClick: function (ev) {
        var $currentTarget = $(ev.currentTarget);
        this._rpc({
            model: 'lims.portal.configuration',
            method: 'unlink',
            args: [[$currentTarget.data('id')]],
        }).then(function () {
            $currentTarget.closest('tr').toggleClass('table-danger');
            $currentTarget.find('i.fa').remove();
        });
    },
});

var LimsConfigMenu = websiteNavbarData.WebsiteNavbarActionWidget.extend({
    xmlDependencies: ['/lims_web/static/src/xml/portal_configuration.xml'],
    actions: _.extend({}, websiteNavbarData.WebsiteNavbarActionWidget.prototype.actions || {}, {
        'lims_configuration': '_openLimsConfiguration',
    }),

    /**
     * @override
     */
    start: function () {
        var self = this;
        var $currentPage = this.$el.closest('body').find('div.o_current_page');
        this.currentPage = {
            'page': $currentPage.data('page'),
            'fields': $currentPage.data('fields'),
            'options': $currentPage.data('options'),
        };
        this._rpc({
            model: 'lims.portal.configuration',
            method: 'search_read',
            fields: ['name'],
            domain: [
                ['page', 'ilike', $currentPage.data('page')],
                ['inactive', '=', true],
            ],
        }).then(function (res) {
            self.inactiveRecords = res;
        });
        this._rpc({
            model: 'lims.portal.configuration',
            method: 'search_read',
            fields: ['name'],
            domain: [
                ['type', '=', 'page'],
                ['inactive', '=', true],
            ],
        }).then(function (res) {
            self.inactivePages = res;
        });
    },

    /**
     * @private
     */
    _openLimsConfiguration: function () {
        var self = this;
        var dialog = new LimsConfigDialog(this, {
            title: _t('Lims Portal Configuration'),
            buttons: [{
                text: _t('Close'),
                close: true,
            }],
            $content: qweb.render('lims_web.lims_portal_configuration', {
                fields: _.map(self.currentPage.fields),
                options: _.map(self.currentPage.options),
                page: self.currentPage.page,
                inactivePages: self.inactivePages,
            }),
        }).open();
        dialog.opened(function () {
            _.each(self.inactiveRecords, function (inactiveRecord) {
                dialog.$el.find('input.o_switch_lims_config[data-name="%s"]'
                    .replace('%s', inactiveRecord.name)).prop('checked', false);
            });
        });
        dialog.on('closed', this, function (ev) {
            self.$el.toggleClass('disabled text-warning');
            document.location.reload();
        });
    },
});

registry.category("website_navbar_widgets").add("LimsConfigMenu", {
    Widget: LimsConfigMenu,
    selector: '#configuration_lims',
});

export default {
    LimsConfigMenu: LimsConfigMenu,
};
