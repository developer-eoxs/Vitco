odoo.define("ks_curved_backend_theme.ks_appdrawer_edit", function (require) {
  "use strict";

  var Widget = require("web.Widget");
  var SystrayMenu = require("web.SystrayMenu");

  var KsAppdrawerEdit = Widget.extend({
    template: "ks_appdrawer_edit",
    events: {
      "click #ks_customize_appdrawer": "_ksShowFavIcons",
    },
    init: function () {
      var self = this;
      this._super.apply(this, arguments);
    },

    _ksShowFavIcons: function (ev) {
      ev.preventDefault();
      var self = this;
      document.body.classList.add("ks_appsmenu_edit");

      $("div.ks_appdrawer_inner_app_div")
        .find("span.ks_fav_icon")
        .removeClass("d-none");
      $("div.ks_appdrawer_div")
        .find("div.ks-app-drawer-close")
        .removeClass("d-none");

      $("div.ks_appdrawer_inner_app_div")
        .find("div.dropdown-item")
        .each((app_div, item) => {
          if ($(item).find("span.ks_rmv_fav").length) {
            $(item).addClass("ks_add_visible");
          }
        });
    },
  });

  KsAppdrawerEdit.prototype.sequence = 51;
  SystrayMenu.Items.push(KsAppdrawerEdit);

  return {
    KsAppdrawerEdit: KsAppdrawerEdit,
  };
});
