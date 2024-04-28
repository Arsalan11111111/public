odoo.define('lims_scan_advanced.LimsBarcodeHandler', function (require) {
"use strict";

var fieldRegistry = require('web.field_registry');
var AbstractField = require('web.AbstractField');

var LimsBarcodeHandler = AbstractField.extend({
    /**
     * override
     */
    init: function() {
        this._super.apply(this, arguments);
        this.trigger_up('activeBarcode', {
            name: this.name,
            commands: {
                'O-CMD.SRCP': _.bind(this.do_action, this, 'lims_scan.sop_scan_receipt_action', {clear_breadcrumbs: true}),
                'O-CMD.SWIP': _.bind(this.do_action, this, 'lims_scan.sop_scan_wip_wizard_action', {clear_breadcrumbs: true}),
                'O-CMD.BCRE': _.bind(this.do_action, this, 'lims_scan.sop_scan_batch_wizard_action', {clear_breadcrumbs: true}),
            },
        });
    },
});

fieldRegistry.add('lims_barcode_handler', LimsBarcodeHandler);

});
