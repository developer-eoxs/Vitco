odoo.define("ks_curved_backend_theme.ks_app_sidebar", function (require) {
  "use strict";

  var Widget = require("web.Widget");

  var ksAppsBar = Widget.extend({
    template: "ks_curved_backend_theme.side_appbar",
    events: _.extend({}, Widget.prototype.events, {
      "click .ks_app": "_ksAppClicked",
      "click .left_sidebar_arrow": "_ksToggleVerticalMenus",
    }),
    /**
     * @override
     * @param {web.Widget} parent
     * @param {Object} menuData
     * @param {Object[]} menuData.children
     */
    init: function (parent, menuData) {
      this._super.apply(this, arguments);
      this._activeApp = undefined;
      this._ks_fav_bar = parent.ks_favorite_bar;
      this._apps = _.map(menuData.children, function (appMenuData) {
        return {
          actionID: parseInt(appMenuData.action.split(",")[1]),
          web_icon_data: appMenuData.web_icon_data,
          web_icon: appMenuData.web_icon,
          menuID: appMenuData.id,
          name: appMenuData.name,
          xmlID: appMenuData.xmlid,
        };
      });
    },

    willStart: async function () {
      const _super = this._super.bind(this);
      const data = await this._rpc({
        route: "/ks_curved_theme/get_fav_icons",
        params: { ks_app_icons: this._apps },
      });
      this._apps = data;
    },

    start: function () {
      var temp_this = this;
      return this._super.apply(this, arguments).then(function () {
        if (
          !document.body.classList.contains("ks_vertical_body_panel") &&
          !temp_this.$el.children(".ks_app_sidebar_menu").children().length
        ) {
          temp_this.$el.parents(".ks_left_sidebar_panel").addClass("d-none");
        } else {
          temp_this.$el.parents(".ks_left_sidebar_panel").removeClass("d-none");
        }
      });
    },

    /**
     * @returns {Object[]}
     */
    getApps: function () {
      return this._apps;
    },

    fav_bar_menu: function () {
      return this._ks_fav_bar;
    },
    /**
     * @private
     * @param {Object} app
     */
    _openApp: function (app) {
      // this._setActiveApp(app);
      this.trigger_up("app_clicked", {
        action_id: app.actionID,
        menu_id: app.menuID,
      });
    },
    /**
     * @private
     * @param {Object} app
     */
    _setActiveApp: function (menuID) {
      var $oldActiveApp = this.$(".ks_app.active");
      $oldActiveApp.removeClass("active");
      var $newActiveApp = this.$('.ks_app[data-menu-id="' + menuID + '"]');
      $newActiveApp.addClass("active");
    },
    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    /**
     * Called when clicking on an item in the apps menu.
     *
     * @private
     * @param {MouseEvent} ev
     */
    _ksAppClicked: function (ev) {
      var $target = $(ev.currentTarget);
      var actionID = $target.data("action-id");
      var menuID = $target.data("menu-id");
      var app = _.findWhere(this._apps, {
        actionID: actionID,
        menuID: menuID,
      });
      this._openApp(app);
      ev.preventDefault();
      $target.blur();
    },
    _ksToggleVerticalMenus: function () {
      document.body.classList.toggle("ks_verticalmenus_expanded");
    },
  });

  return ksAppsBar;
});
