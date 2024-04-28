odoo.define('mail_see_recipients.mail_chatter', function (require) {
    "use strict";

    var chatManager = require("mail.chat_manager");
    var Chatter = require("mail.Chatter");

    /**
     * extended mail_thread to change the function open_composer
     **/

    var Mail_Chatter_Mail = Chatter.include({
        events: {
            "click .o_chatter_button_new_message": "on_open_composer_new_message",
            'click .o_chatter_button_log_note': '_onOpenComposerNote',
            'click .o_chatter_button_schedule_activity': '_onScheduleActivity',
        },

        init: function () {
            this._super.apply(this, arguments);
        },

        willStart: function () {
            return chatManager.is_ready;
        },

        // composer toggle
        on_open_composer_new_message: function () {
            this.open_composer_message();
        },

        open_composer_message: function (options) {
            this.followers = this.fields.followers;

            /* updated default value in context */
            var context = {
                    default_parent_id: this.id,
                    partner_ids: this.followers.followers,
                    force_notify_only_partners: true
                };
            if (this.context.default_model && this.context.default_res_id) {
                    context.default_model = this.context.default_model;
                    context.default_res_id = this.context.default_res_id;
                }

            /* open action to compose mail */
            var action = {
                type: 'ir.actions.act_window',
                res_model: 'mail.compose.message',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: context,
            };
            this.do_action(action, {
                on_close: this.trigger_up.bind(this, 'reload'),
                }).then(this.trigger.bind(this, 'close_composer'));
        }
    });
    return Mail_Chatter_Mail;
});
