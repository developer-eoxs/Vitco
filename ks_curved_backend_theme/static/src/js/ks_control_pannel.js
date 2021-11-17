odoo.define('ks_curved_backend_theme.ControlPanel', function (require) {
"use strict";

var config = require('web.config');
var ControlPanelRenderer = require('web.ControlPanelRenderer');

ControlPanelRenderer.include({
    events:_.extend({}, ControlPanelRenderer.prototype.events, {
        'click .ks-phone-controll-option': '_ksMobileViewSwitcher',
        'click .ks-phone-sr-btn': '_ksSearchButtonOpen',
        'click .ks-search-close': '_ksSearchButtonClose',
        'click .ks_fullscreen': '_onksFullScreen',
        'click .ks-phone-category-btn': '_ksSearchPanelOpen',
    }),

    _onksFullScreen(ev) {
        var ks_window = document.documentElement;
        var ks_elem_class = ev.currentTarget.classList;
        if (window.innerHeight == screen.height) {
            if ($("button.ks_fullscreen").hasClass("fa-expand")) {
                alert(_t("Browser is in fullscreen mode."));
            } else {
                try {
                    ks_elem_class.remove("fa-compress");
                    ks_elem_class.add("fa-expand");
                    if (document.exitFullscreen) {
                        document.exitFullscreen();
                    } else if (document.webkitExitFullscreen) {
                        /* Safari */
                        document.webkitExitFullscreen();
                    } else if (document.msExitFullscreen) {
                        /* IE11 */
                        document.msExitFullscreen();
                    }
                } catch (err) {
                    alert(_t("Unable to perform this operation."));
                }
            }
        } else {
            ks_elem_class.remove("fa-expand");
            ks_elem_class.add("fa-compress");
            if (ks_window.requestFullscreen) {
                ks_window.requestFullscreen();
            } else if (ks_window.webkitRequestFullscreen) {
                /* Safari */
                ks_window.webkitRequestFullscreen();
            } else if (ks_window.msRequestFullscreen) {
                /* IE11 */
                ks_window.msRequestFullscreen();
            }
        }

        document.addEventListener("fullscreenchange", (event) => {
            if (document.fullscreenElement) {
                $("button.ks_fullscreen").removeClass("fa-expand");
                $("button.ks_fullscreen").addClass("fa-compress");
            } else {
                $("button.ks_fullscreen").removeClass("fa-compress");
                $("button.ks_fullscreen").addClass("fa-expand");
            }
        });
    },

    _toggleMobileQuickSearchView: function () {
        this.$('.o_cp_searchview').toggleClass('o_searchview_quick');
        this.$('.breadcrumb').toggleClass('o_hidden',
            this.$('.o_cp_searchview').hasClass('o_searchview_quick'));
        this.$('.o_toggle_searchview_full')
            .toggleClass('o_hidden')
            .toggleClass('btn-secondary', !!this.state.query.length);
        this._renderSearchviewInput();
    },

    _renderSearchviewInput: function () {
        if (!this.withBreadcrumbs || (!this.$('.o_toggle_searchview_full').hasClass('o_hidden') && this.$('.o_mobile_search').hasClass('o_hidden'))) {
            this.$('.o_toggle_searchview_full').toggleClass('btn-secondary', !!this.state.query.length);
            this.searchBar.$el.detach().insertAfter(this.$('.o_mobile_search'));
        } else {
            this.searchBar.$el.detach().insertAfter(this.$('.ks-top-icons'));
        }
    },

    _ksMobileViewSwitcher() {
        $(".o_cp_switch_buttons").toggleClass("show");
        $(".o_cp_switch_buttons .dropdown-menu").toggleClass("show");
    },

    _ksSearchButtonOpen() {
      $(".ks_search_responsive").addClass("show");
      // Hide breadcrumb text and search icon.
      $(".o_cp_top_left .breadcrumb-item").addClass("d-none");
      $(".o_cp_top_right .ks-phone-sr-btn").addClass("d-none");
    },

    _ksSearchButtonClose() {
      $(".ks_search_responsive").removeClass("show");
      $(".o_cp_top_left .breadcrumb-item").removeClass("d-none");
      $(".o_cp_top_right .ks-phone-sr-btn").removeClass("d-none");
    },

    _ksSearchPanelOpen() {
      $(".ks_search_panel").addClass("show");
    },

});

});

odoo.define("ks_curved_backend_theme.AbstractController", function (require) {
  "use strict";

var AbstractController = require('web.AbstractController');
var config = require('web.config');
var core = require('web.core');
var QWeb = core.qweb;

var ksAbstractController = AbstractController.include({

    init: function (parent, model, renderer, params) {
        this._super.apply(this, arguments);
        if (config.device.isMobile && this._searchPanel && this._searchPanel.sections){
            this._controlPanel.$el.find('.o_control_panel').append(QWeb.render('ks_control_search_panel', {filters: this._searchPanel.sections}));
        }
    },
    _renderSwitchButtons: function () {
        var self = this;
        var views = _.filter(this.actionViews, {multiRecord: this.isMultiRecord});

        if (views.length <= 1) {
            return $();
        }

        var template = config.device.isMobile ? 'ControlPanel.SwitchButtons.Mobile' : 'ControlPanel.SwitchButtons';
        var $switchButtons = $(QWeb.render(template, {
            viewType: this.viewType,
            views: views,
        }));
        // create bootstrap tooltips
        _.each(views, function (view) {
            $switchButtons.filter('.o_cp_switch_' + view.type).tooltip();
        });
        // add onclick event listener
        var $switchButtonsFiltered = $switchButtons.filter('button');
        $switchButtonsFiltered.click(_.debounce(function (event) {
            var viewType = $(event.target).data('view-type');
            self.trigger_up('switch_view', {view_type: viewType});
        }, 200, true));

        // set active view's icon as view switcher button's icon in mobile
        if (config.device.isMobile) {
            var activeView = _.findWhere(views, {type: this.viewType});
            $switchButtons.find('.o_switch_view_button_icon').addClass('fa fa-lg ' + activeView.icon);
        }
        return $switchButtons;
    },
});

});