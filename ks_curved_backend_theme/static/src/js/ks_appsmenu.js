odoo.define("ks_curved_backend_theme.ks_appsmenu", function(require) {
    "use strict";

    var AppsMenu = require("web.AppsMenu");
    var session = require("web.session");
    var config = require("web.config");
    var core = require("web.core");
    var QWeb = core.qweb;

    function ks_GetReducedMenuData(memo, menu) {
        if (menu.action) {
            var key = menu.parent_id ? menu.parent_id[1] + "/" : "";
            menu["ks_title"] = (key + menu.name).toLowerCase();
            memo[key + menu.name] = menu;
        }
        if (menu.children.length) {
            _.reduce(menu.children, ks_GetReducedMenuData, memo);
        }
        return memo;
    }

    AppsMenu.include({
        // FixMe: Bootstrap events not working
        events: _.extend({}, AppsMenu.prototype.events, {
            "keydown .ks_menu_search_box input": "_ksSearchValuesMovement",
            "input .ks_menu_search_box input": "_ksSearchMenuListTime",
            "click .ks-menu-search-value": "_ksSearchValuesSelecter",

            "shown.bs.dropdown": "_ksSearchFocus",
            "hidden.bs.dropdown": "_ksSearchResetvalues",
            "hide.bs.dropdown": "_ksHideAppsMenuList",
            "click .ks_rmv_fav": "_ksRemoveFavApps",
            "click .ks_add_fav": "_ksAddFavApps",
            "click .ks_close_app_drawer": "_ksHideFavIcons",
        }),
        /**
         * @overrideks_appsmenu_active
         * @param {web.Widget} parent
         * @param {Object} menuData
         * @param {Object[]} menuData.children
         */
        init: function(parent, menuData) {
            this._super.apply(this, arguments);
            for (let i in this._apps) {
                this._apps[i].web_icon_data = menuData.children[i].web_icon_data;
            }
            var today = new Date();
            var curHr = today.getHours();
            var message = "Hi, ";
            if (curHr < 12) {
                message = "Good Morning, ";
            } else if (curHr < 18) {
                message = "Good Afternoon, ";
            } else {
                message = "Good Evening, ";
            }
            this.ks_user_id = session.uid;
            this.ks_user_name = message + session.name;
            this._ks_fuzzysearchableMenus = _.reduce(
                menuData.children,
                ks_GetReducedMenuData, {}
            );
        },
        /**
         * @override
         **/
        willStart: async function() {
            const _super = this._super.bind(this);
            const data = await this._rpc({
                route: "/ks_app_frequency/render",
            });

            const ks_fav_apps = await this._rpc({
                route: "/ks_curved_theme/get_fav_icons",
                params: { ks_app_icons: this._apps },
            });

            this._apps = ks_fav_apps;
            this._ks_frequent_apps = [];
            data.forEach((item, index) => {
                var frequent_app = this._apps.filter((app) => {
                    if (app.menuID == item) return app;
                });
                this._ks_frequent_apps.push(frequent_app[0]);
            });
            return _super(...arguments);
        },
        /**
         * @override
         **/
        start: function() {
            this.$search_container = this.$(".ks_menu_search");
            this.$search_input = this.$(".ks_menu_search_box input");
            this.$search_results = this.$(".ks-search-values");
            return this._super.apply(this, arguments);
        },
        /**
         * Open the first app in the list of apps
         */
        openFirstApp: function() {
            if (!this._apps.length) {
                return;
            }
            var firstApp = this._apps[0];
            this._openApp(firstApp);
            // Code to display appdrawer
            this.trigger_up("ks_manage_drawer", {
                drawer_status: 'open'
            });
            document.body.classList.add("ks_appsmenu_active");
            document.body.classList.remove("brightness");
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * Called when clicking on an item in the apps menu
         * To hide the App drawer on clicking apps
         * @override
         * @param {MouseEvent} ev
         */
        _onAppsMenuItemClicked: function(ev) {
            this._super.apply(this, arguments);
            document.body.classList.toggle("ks_appsmenu_active");
            if (document.body.classList.contains("ks_appsmenu_active")) {
                document.body.classList.remove("brightness");
                this.trigger_up("ks_manage_drawer", {
                    drawer_status: 'open'
                });
            } else {
                document.body.classList.add("brightness");
                this.trigger_up("ks_manage_drawer", {
                    drawer_status: 'close'
                });
            }

            //      setTimeout(function () {
            //        document.body.classList.toggle("ks_appsmenu_active");
            //        if (document.body.classList.contains("ks_appsmenu_active")) {
            //          document.body.classList.remove("brightness");
            //        } else {
            //          document.body.classList.add("brightness");
            //        }
            //      }, 1000);
            ev.preventDefault();
            ev.stopPropagation();
            // 2 secs delay before hiding div
        },
        /**
         * To split the object into chunks of 12
         * @returns {Object[]}
         */
        _getSplittedApps: function() {
            var apps = this._apps;
            var i,
                j,
                app_list = [],
                chunk = 12;
            for (i = 0, j = apps.length; i < j; i += chunk) {
                app_list.push(apps.slice(i, i + chunk));
            }
            return app_list;
        },
        /**
         * To get frequent apps of current user
         * @returns {Object[]}
         */
        _getFrequentApps: function() {
            return this._ks_frequent_apps;
        },

        _ksHideFavIcons: function(ev) {
            ev.preventDefault();
            var self = this;
            document.body.classList.remove("ks_appsmenu_edit");

            $("div.ks_appdrawer_inner_app_div")
                .find("span.ks_fav_icon")
                .addClass("d-none");
            $("div.ks_appdrawer_div")
                .find("div.ks-app-drawer-close")
                .addClass("d-none");
        },

        //--------------------------------------------------------------------------
        // Searching
        //--------------------------------------------------------------------------
        // FixMe: Optimize the code and correct Naming (Copied)

        _ksSearchFocus: function() {
            // ToDo: Only for mobile, check its usage
            if (!config.device.isMobile) {
                this.$search_input.focus();
            }
        },

        _ksSearchMenuListTime: function() {
            this._ks_search_def = new Promise((resolve) => {
                setTimeout(resolve, 50);
            });
            this._ks_search_def.then(this._ksSearchMenusList.bind(this));
        },

        _ksSearchResetvalues: function() {
            this.$search_container.removeClass("ks-find-values");
            this.$search_results.empty();
            this.$search_input.val("");
        },

        _ksSearchMenusList: function() {
            var query = this.$search_input.val();
            if (query === "") {
                this.$search_container.removeClass("ks-find-values");
                this.$search_results.empty();
                return;
            }
            query = query.toLowerCase();
            var _newdata_app = _.filter(
                this._ks_fuzzysearchableMenus,
                function(menu) {
                    return (
                        menu.ks_title && !menu.parent_id && menu.ks_title.includes(query)
                    );
                }
            );
            var _newdata_items = _.filter(
                this._ks_fuzzysearchableMenus,
                function(menu) {
                    return (
                        menu.ks_title && menu.parent_id && menu.ks_title.includes(query)
                    );
                }
            );
            this.$search_container.toggleClass(
                "ks-find-values",
                Boolean(_newdata_app.length + _newdata_items.length)
            );
            this.$search_results.html(
                QWeb.render("ks_curved_backend_theme.ks_search_menu_items", {
                    ks_menu_items: _newdata_items,
                    ks_menu_app: _newdata_app,
                })
            );
        },

        _ksSearchValuesSelecter: function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            const $current_value = $(ev.currentTarget),
                data = $current_value.data();
            this.trigger_up("menu_clicked", {
                action_id: data.actionId,
                id: data.menuId,
                previous_menu_id: data.parentId,
            });
            core.bus.trigger("change_menu_section", data.menuId);
            // To Toggle app Drawer
            //      setTimeout(function () {
            document.body.classList.toggle("ks_appsmenu_active");
            if (document.body.classList.contains("ks_appsmenu_active")) {
                document.body.classList.remove("brightness");
                this.trigger_up("ks_manage_drawer", {
                    drawer_status: 'open'
                });
            } else {
                document.body.classList.add("brightness");
                this.trigger_up("ks_manage_drawer", {
                    drawer_status: 'close'
                });
            }
            //      }, 2000);
        },

        _ksSearchValuesMovement: function(ev) {
            var all = this.$search_results.find(".ks-menu-search-value"),
                pre_focused = all.filter(".active") || $(all[0]);
            var offset = all.index(pre_focused),
                key = ev.key;
            if (!all.length) {
                return;
            }
            if (key === "Tab") {
                ev.preventDefault();
                key = ev.shiftKey ? "ArrowUp" : "ArrowDown";
            }
            switch (key) {
                case "Enter":
                    pre_focused.click();
                    break;
                case "ArrowUp":
                    offset--;
                    break;
                case "ArrowDown":
                    offset++;
                    break;
                default:
                    return;
            }
            if (offset < 0) {
                offset = all.length + offset;
            } else if (offset >= all.length) {
                offset -= all.length;
            }

            const new_focused = $(all[offset]);
            pre_focused.removeClass("active");
            new_focused.addClass("active");
            this.$search_results.scrollTo(new_focused, {
                offset: {
                    top: this.$search_results.height() * -0.5,
                },
            });
        },

        _ksHideAppsMenuList: function(ev) {
            return !this.$("input").is(":focus");
        },

        _ksAddFavApps: async function(ev) {
            ev.preventDefault();
            const result = await this._rpc({
                route: "/ks_curved_theme/set_fav_icons",
                params: {
                    ks_app_id: ev.currentTarget.previousElementSibling.getAttribute(
                        "data-menu-id"
                    ),
                },
            });
            if (result) {
                this.trigger_up("ks_update_fav_icon");
                this._ksRemFromFav(ev);
            }
        },

        _ksRemoveFavApps: async function(ev) {
            ev.preventDefault();
            const result = await this._rpc({
                route: "/ks_curved_theme/rmv_fav_icons",
                params: {
                    ks_app_id: ev.currentTarget.previousElementSibling.getAttribute(
                        "data-menu-id"
                    ),
                },
            });
            if (result) {
                this.trigger_up("ks_update_fav_icon");
                this._ksAddToFav(ev);
            }
        },

        _ksAddToFav: function(ev) {
            // Change Class.
            $(ev.currentTarget).removeClass("ks_rmv_fav");
            $(ev.currentTarget).addClass("ks_add_fav");

            // Change icon
            $(ev.currentTarget)
                .find("img")
                .attr("src", "ks_curved_backend_theme/static/src/images/star.svg");

            // Deactive app
            $(ev.currentTarget.parentElement).removeClass('ks_add_visible');
        },

        _ksRemFromFav: function(ev) {
            // Change Class.
            $(ev.currentTarget).removeClass("ks_add_fav");
            $(ev.currentTarget).addClass("ks_rmv_fav");

            // Change icon
            $(ev.currentTarget)
                .find("img")
                .attr("src", "ks_curved_backend_theme/static/src/images/fav_ic.svg");

            // Active App
            $(ev.currentTarget.parentElement).removeClass('ks_add_visible');
            $(ev.currentTarget.parentElement).addClass('ks_add_visible');
        },

        /**
         * @private
         * @param {Object} app
         */
        _setActiveApp: function(app) {
            var $oldActiveApp = this.$(".o_app.active");
            $oldActiveApp.removeClass("active");
            var $newActiveApp = this.$(
                '.o_app[data-action-id="' + app.actionID + '"]'
            );
            //Do not set active on frequent apps menu
            //$newActiveApp.addClass('active');
        },
    });
});