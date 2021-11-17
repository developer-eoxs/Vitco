odoo.define("ks_curved_backend_theme.FormController", function (require) {
  "use strict";

  var KsFormController = require("web.FormController");
  var KsFormRenderer = require("web.FormRenderer");
  var Session = require("web.session");

  KsFormRenderer.include({
    events: _.extend({}, KsFormRenderer.prototype.events, {
      "dblclick .o_form_sheet_bg": "_ksOnFormviewDblClick",
//      "click span.phone-sm-btns": "_ksToggleStatusButton",
    }),

//    init: function (parent, state, params) {
//        this._super.apply(this, arguments);
//        $(document).on("click", function (event) {
//            var $trigger = $(".phone-sm-btns");
//            if ($trigger !== event.target && !$trigger.has(event.target).length) {
//              $(".o_statusbar_buttons").removeClass("show");
//            }
//          });
//    },

    _updateView: function ($newContent) {
      this._super(...arguments);
      var temp_this = this;
      if (this.$el.children(".o_chatter.oe_chatter").length) {
        this._rpc({
          model: "ks.global.config",
          method: "ks_get_value_from_scope",
          args: [["ks_chatter"]],
        }).then(function (result) {
          if (result.ks_chatter && result.ks_chatter == "ks_chatter_right") {
            temp_this.$el.addClass("ks-right-content");
          }
        });
      }
    },

    _ksOnFormviewDblClick: function (ev) {
      var $target = $(ev.target);
      var temp_this = this;
      this._rpc({
        model: "ks.global.config",
        method: "ks_get_value_from_scope",
        args: [["ks_click_edit"]],
      }).then(function (result) {
        if (
          result.ks_click_edit &&
          temp_this.mode == "readonly" &&
          !$target.is(".o_form_label, .o_field_widget") &&
          Session.ks_curved_backend_theme_data
        ) {
          temp_this.getParent()._ksOnClickEditMode();
        }
      });
    },

    _renderTagHeader: function (node) {
      const $statusbar = this._super.apply(this, arguments);
      // Collapse statusbar buttons on mobile devices.
      // Check if status button is more than 1 then enable dropdown.
      if ($statusbar.find("button:not(.o_invisible_modifier)").length > 0) {
        return $statusbar.prepend(
          $('<span class="phone-sm-btns"><i class="fa fa-cog"></i> Action</span>').bind('click', function(ev){
            $(".o_statusbar_buttons").toggleClass("show");
          })
        );
      }

      return $statusbar;
    },

    _ksToggleStatusButton: function (ev) {
      $(".o_statusbar_buttons").toggleClass("show");
    },
  });

  KsFormController.include({
    custom_events: _.extend({}, KsFormController.prototype.custom_events, {
      ks_click_to_edit: "_ksOnClickEditMode",
    }),
    _ksOnClickEditMode: function (ev) {
      if (this.is_action_enabled("edit")) {
        this._setMode("edit");
      }
    },
  });
});
