odoo.define('lims_barcode.MainMenu', function (require) {
"use strict";

var core = require('web.core');
var Session = require('web.session');
var AbstractAction = require('web.AbstractAction');

var MainMenu = AbstractAction.extend({
    contentTemplate: 'lims_main_menu',
    events: {
        'click .button_receipt_sop': '_onReceiptSopBtnClick',
        'click .button_wip_sop': '_onWipSopBtnClick',
        'click .button_create_batch_sop': '_onCreateBatchSopBtnClick',
    },

    /**
     * @override
     */
    start: function() {
        core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
        return this._super();
    },
    /**
     * @override
     */
    destroy: function () {
        core.bus.off('barcode_scanned', this, this._onBarcodeScanned);
        this._super();
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    _onBarcodeScanned: function(barcode) {
        var self = this;
        if (!$.contains(document, this.el)) {
            return;
        }
        Session.rpc('/lims_scan_advanced/scan_from_main_menu', {
            barcode: barcode,
        }).then(function (result) {
            if (result.action) {
                self.do_action(result.action);
            } else if (result.warning) {
                self.do_warn(result.warning);
            }
        });
    },

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * @private
     */
    _onReceiptSopBtnClick: function () {
        this.do_action('lims_scan.sop_scan_receipt_action');
    },
    /**
     * @private
     */
    _onWipSopBtnClick: function () {
        this.do_action('lims_scan.sop_scan_wip_wizard_action');
    },
    /**
     * @private
     */
    _onCreateBatchSopBtnClick: function () {
        this.do_action('lims_scan.sop_scan_batch_wizard_action');
    },
});

core.action_registry.add('lims_barcode_main_menu', MainMenu);

return {
    MainMenu: MainMenu,
};

});
