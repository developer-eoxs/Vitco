odoo.define(
  "ks_curved_backend_theme.ks_left_sidebar_panel",
  function (require) {
    "use strict";

     var config = require("web.config");
    // To check the device

    var Menu = require("web.Menu");
    var AppsMenu = require("web.AppsMenu");
    var SystrayMenu = require("web.SystrayMenu");
    var UserMenu = require("web.UserMenu");
    var dom = require("web.dom");
    var session = require("web.session");
    var ksAppSidebar = require("ks_curved_backend_theme.ks_app_sidebar");
    var ksBookmarks = require("ks_curved_backend_theme.ks_bookmarks");
    var core = require('web.core');
    var QWeb = core.qweb;

    Menu.include({
      events: _.extend({}, Menu.prototype.events, {
        "click #ks_app_drawer_toggle": "_ksAppsDrawerClick",
        "click button.phone-menu-btn": "_ksOpenMobileDrawer",
        "click div.overlay": "_ksCloseMobileDrawer",
        "click div.ks-phone-menu-list .o_menu_sections a[data-menu]":
          "_ksMobileDrawerMenu",
        //            "click .dropdown-menu.show": "_ksMenuBodyClick",
      }),

      custom_events: {
        ks_update_fav_icon: "_ksUpdateFavIcon",
        ks_manage_drawer: "_ksManagerDrawer",
      },

      init: function () {
        return this._super.apply(this, arguments);
      },

      willStart: function () {
        var self = this;
        var ks_fields_data = self
          ._rpc({
            model: "ks.global.config",
            method: "ks_get_value_from_scope",
            args: [
              [
                "ks_menu_bar",
                "ks_favorite_bar",
                "ks_company_logo",
                "ks_favtbar_autohide",
                "ks_favtbar_position",
                "ks_show_app_name",
                "ks_user_menu_placement",
                "ks_menubar_autohide",
              ],
            ],
          })
          .then(function (res) {
            if (res) {
              self.ks_menu_bar = res.ks_menu_bar;
              self.ks_favorite_bar = res.ks_favorite_bar;
              self.ks_favtbar_autohide = res.ks_favtbar_autohide;
              self.ks_menubar_autohide = res.ks_menubar_autohide;
              self.ks_favtbar_position = res.ks_favtbar_position;
              self.ks_company_logo = res.ks_company_logo;
              self.ks_show_app_name = res.ks_show_app_name;
              self.ks_user_menu_placement = res.ks_user_menu_placement;
            }
            if (self.ks_menu_bar == "Vertical")
              document.body.classList.add("ks_vertical_body_panel");
            if (
              self.ks_favtbar_autohide &&
              self.ks_favorite_bar &&
              self.ks_menu_bar == "Horizontal"
            )
              document.body.classList.add("ks_favtbar_autohide");
            if (self.ks_menubar_autohide && screen.width > 1024)
              document.body.classList.add("ks_menubar_autohide");
            if (
              self.ks_favtbar_position == "Bottom" &&
              self.ks_menu_bar == "Horizontal"
            )
              document.body.classList.add("ks_favtbar_bottom");
            if (
              self.ks_user_menu_placement == "Top" &&
              self.ks_menu_bar == "Vertical"
            )
              document.body.classList.add("ks_user_menu_top");
            if (!self.ks_show_app_name && self.ks_favorite_bar)
              document.body.classList.add("ks_hide_app_names");
            if (self.ks_menu_bar == "Horizontal" && !self.ks_favorite_bar)
              document.body.classList.add("ks_hide_leftpanel");
          if ((self.ks_menu_bar == "Horizontal" && self.ks_favorite_bar && self.ks_favtbar_position == "Left") || (self.ks_menu_bar == "Vertical" && !self.ks_menubar_autohide))
              document.body.classList.add("ks_leftpanel_active");
          });
        return Promise.all([
          this._super.apply(this, arguments),
          ks_fields_data,
        ]);
      },

      start: function () {
        var self = this;

        this.$menu_apps = this.$(".o_menu_apps");
        if (this.ks_menu_bar == "Horizontal") {
          this.$menu_brand_placeholder = this.$(".o_menu_brand");
          this.$section_placeholder = this.$(".o_menu_sections");
        } else if (this.ks_menu_bar == "Vertical") {
          this.$menu_brand_placeholder = this.$el
            .siblings(".ks_vertical_menus")
            .find(".o_menu_brand");
          this.$section_placeholder = this.$el
            .siblings(".ks_vertical_menus")
            .find(".o_menu_sections");
          this.$menu_icon = this.$el
            .siblings(".ks_vertical_menus")
            .find(".ks_vertical_app_icon");

          // Vertical app menu drawer open.
          $("div.ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar").on(
            "click",
            "button.phone-menu-btn",
            self._ksOpenMobileDrawer.bind(self)
          );
          // Vertical app menu drawer close.
          $("div.ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar").on(
            "click",
            "div.overlay",
            self._ksCloseMobileDrawer.bind(self)
          );

          // Vertical menu binding
          $("div.ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar").on(
            "click",
            "a[data-menu]",
            self._ksMobileDrawerMenu.bind(self)
          );

          // Vertical user data append and binding.
          var ks_user_action = QWeb.render('UserMenu.Actions');
          $('div.ks_user_action').html(ks_user_action);
          $("div.ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar").on(
            "click",
            ".ks-phone-menu-list .ks-phone-profile a[data-menu]",
            function (ev) {
              ev.preventDefault();
              var menu = $(this).data("menu");
              self.ksMobileUserMenu[
                "_onMenu" + menu.charAt(0).toUpperCase() + menu.slice(1)
              ]();
              self._ksCloseMobileDrawer();
            }
          );
        }

        this._ksUpdateFavIcon();

        this._updateMenuBrand();
        this.$right_sidebar = this.$el.siblings(".ks_right_sidebar_panel");
        this._bookmark_bar = new ksBookmarks();
        this._bookmark_bar.appendTo(this.$right_sidebar);

        // Navbar's menus event handlers
        var on_secondary_menu_click = function (ev) {
          ev.preventDefault();
          var menu_id = $(ev.currentTarget).data("menu");
          var action_id = $(ev.currentTarget).data("action-id");
          self._on_secondary_menu_click(menu_id, action_id);
        };
        var menu_ids = _.keys(this.$menu_sections);
        var primary_menu_id, $section;
        for (var i = 0; i < menu_ids.length; i++) {
          primary_menu_id = menu_ids[i];
          $section = this.$menu_sections[primary_menu_id];
          $section.on(
            "click",
            "a[data-menu]",
            self,
            on_secondary_menu_click.bind(this)
          );
        }

        // Apps Menu
        this._appsMenu = new AppsMenu(self, this.menu_data);
        if (this.ks_menu_bar == "Horizontal")
          var appsMenuProm = this._appsMenu.appendTo(this.$menu_apps);
        else if (this.ks_menu_bar == "Vertical")
          var appsMenuProm = this._appsMenu
            .appendTo(
              this.$el.siblings(".ks_left_sidebar_panel").find(".o_menu_apps")
            )
            .then(function () {
              self.$el
                .siblings(".ks_left_sidebar_panel")
                .on(
                  "click",
                  "#ks_app_drawer_toggle",
                  self._ksAppsDrawerClick.bind(self)
                );
            });

        // Systray Menu
        this.systray_menu = new SystrayMenu(this);
        this.ksMobileUserMenu = new UserMenu(self);
        var systrayMenuProm = this.systray_menu
          .attachTo($(".o_menu_systray"))
          .then(function () {
//            self.systray_menu.on_attach_callback();
            $(".ks-menu-systray .o_user_menu").remove();

            // At this point, we know we are in the DOM
            if (self.ks_menu_bar == "Horizontal") {
              dom.initAutoMoreMenu(self.$section_placeholder, {
                maxWidth: function () {
                  return (
                    self.$el.width() -
                    (self.$menu_apps.outerWidth(true) +
                      self.$menu_brand_placeholder.outerWidth(true) +
                      self.systray_menu.$el.outerWidth(true))
                  );
                },
                sizeClass: "SM",
              });
            }
          });
        if (this.ks_menu_bar == "Vertical") {
          this._userMenu = new UserMenu(self);
          var userMenuProm = this._userMenu.appendTo($(".ks_user_menu"));
        }

        // Handle mobile drawer's user action.
        this.$el.on(
          "click",
          ".ks-phone-menu-list .ks-phone-profile a[data-menu]",
          function (ev) {
            ev.preventDefault();
            var menu = $(this).data("menu");
            self.ksMobileUserMenu[
              "_onMenu" + menu.charAt(0).toUpperCase() + menu.slice(1)
            ]();
            self._ksCloseMobileDrawer();
          }
        );
        return Promise.all([appsMenuProm, systrayMenuProm]);
      },

      change_menu_section: function (primary_menu_id) {
        if (primary_menu_id && this.ks_favorite_bar)
          this._appsBar._setActiveApp(primary_menu_id);
        this._super.apply(this, arguments);
        if (primary_menu_id && this.ks_menu_bar == "Vertical") {
          var active_menu = this.menu_data.children.find(
            (x) => x.id === primary_menu_id
          );
          var $menu_icon = this.$menu_icon;
          if (active_menu) {
            $menu_icon.attr({
              alt: active_menu.name,
              title: active_menu.name,
              src: "data:image/png;base64," + active_menu.web_icon_data,
            });
          }
        }
        // For Frequency of Apps 👇
        if (primary_menu_id) {
          this._rpc({
            route: "/ks_app_frequency/update",
            params: {
              menu_id: primary_menu_id,
            },
          });
        }

        let tabContent = document.querySelectorAll(".tabContent .item");
        let ksTabs = document.querySelectorAll(".ks-tabs li");
        ksTabs.forEach((el, i) => {
          el.addEventListener("click", () => {
            ksTabs.forEach((rm) => {
              rm.classList.remove("active");
            });
            el.classList.add("active");
            tabContent.forEach((tabCont) => {
              tabCont.classList.remove("active");
            });
            tabContent[i].classList.add("active");
          });
        });
      },
      //--------------------------------------------------------------------------
      // Handlers
      //--------------------------------------------------------------------------

      /**
       * Show & hide app drawer
       *
       * @private
       * @param {MouseEvent} event
       */
      _ksAppsDrawerClick: function (event) {
        // To prevent opening default app
        event.stopPropagation();
        event.preventDefault();
        document.body.classList.toggle("ks_appsmenu_active");
        if (document.body.classList.contains("ks_appsmenu_active")) {
          document.body.classList.remove("brightness");
          this.trigger_up("ks_manage_drawer", {
            drawer_status: "open",
          });
        } else {
          document.body.classList.add("brightness");
          this.trigger_up("ks_manage_drawer", {
            drawer_status: "close",
          });
        }
        var owl = $(".owl-carousel");
        owl.owlCarousel({
          ltr: true,
          dots: true,
          dotsEach: true,
          items: 1,
          animateIn: "fadeIn",
          //                animateOut:'bounceOutDown',
          //                animateIn:'bounceInDown',
          //                startPosition: 'left',
          //                rtl: false,
          //                center: true,
          //                animateOut: 'fadeOut',
          //                animateOut: 'slideOutUp',
          //                animateIn: 'slideInUp'
        });
        //            owl.on('mousewheel', '.owl-stage', function (ev) {
        //                if (ev.originalEvent.deltaX>0) {
        //                    owl.trigger('next.owl');
        //                } else {
        //                    owl.trigger('prev.owl');
        //                }
        //                ev.preventDefault();
        //            });
      },

      _ksUpdateFavIcon: function () {
        this._appsBar = new ksAppSidebar(this, this.menu_data);
        this.$menu_apps_sidebar = this.$el
          .siblings(".ks_left_sidebar_panel")
          .find(".inner-sidebar");
        $("div.ks_favt_apps").remove();
        this._appsBar.prependTo(this.$menu_apps_sidebar);
      },

      _ksManagerDrawer: function (drawer_status) {
        if (drawer_status.data && drawer_status.data.drawer_status) {
          if (drawer_status.data.drawer_status == "open") {
            if ($("html").attr("data-drawer-font-style") == "dark")
              $("html").attr("data-color-mode", "ks-dark");
            else if ($("html").attr("data-drawer-font-style") == "light")
              $("html").attr("data-color-mode", "ks-light");

            // Manage App drawer theme color.
            document.body.style.removeProperty("--body-background");
            document.body.style.removeProperty("--nav-link-color");
            document.body.style.removeProperty("--ks-over-link");

            $("ul.o_menu_systray").removeClass("ks_color_theme_dark_header");
            $('.o_main_navbar button.phone-menu-btn').removeClass("ks_color_theme_dark_header");
            $('.ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar button.phone-menu-btn').removeClass("ks_color_theme_dark_header");
          }
          if (drawer_status.data.drawer_status == "close") {
            $("html").attr("data-color-mode", session.ks_current_color_mode);

            if (session.ks_current_color_mode == "ks-light") {
              // Apply Color theme back.
              document.body.style.setProperty(
                "--body-background",
                session.ks_color_theme["body-background"]
              );

              document.body.style.setProperty(
                "--nav-link-color",
                session.ks_color_theme["nav-link-color"]
              );

              document.body.style.setProperty(
                "--ks-over-link",
                session.ks_color_theme["ks-over-link"]
              );
            }

            if (session.ks_color_theme.ks_header_icon_clr) {
              $("ul.o_menu_systray").addClass("ks_color_theme_dark_header");
              $('.o_main_navbar button.phone-menu-btn').addClass("ks_color_theme_dark_header");
              $('.ks_left_sidebar_panel .ks_app_sidebar .inner-sidebar button.phone-menu-btn').addClass("ks_color_theme_dark_header");
            }
          }
        }
      },

      _ksOpenMobileDrawer: function () {
        // Append user's info
        var ks_user_name = $(
          ".o_user_menu div.ks-user-info-inside-dropdown span.oe_topbar_name"
        ).text();
        var ks_user_img_src = $(
          "li.o_user_menu img.rounded-circle.oe_topbar_avatar"
        ).attr("src");
        if (ks_user_name) {
          $("div.ks-phone-profile .ks_user_name").text(ks_user_name);
        }
        if (ks_user_img_src) {
          $("div.ks-phone-profile .ks-user-profile-img img").attr(
            "src",
            ks_user_img_src
          );
        }

        if ($("div.ks-phone-side-menu").length) {
          $("div.ks-phone-side-menu").addClass("active-menu");
          $("div.ks-phone-menu-list").append(
            $("ul.o_menu_sections")[0].outerHTML
          );
          setTimeout(() => {
            $("div.ks-phone-menu-list").addClass("menu-show");
          }, 200);
        }
      },

      _ksCloseMobileDrawer: function () {
        if ($("div.ks-phone-menu-list").hasClass("menu-show")) {
          $("div.ks-phone-menu-list").removeClass("menu-show");
          $("div.ks-phone-menu-list").find("ul.o_menu_sections").remove();
          setTimeout(() => {
            $("div.ks-phone-side-menu").removeClass("active-menu");
          }, 200);
        }
      },

      _ksMobileDrawerMenu: function (ev) {
        var self = this;
        ev.preventDefault();
        var menu_id = $(ev.currentTarget).data("menu");
        var action_id = $(ev.currentTarget).data("action-id");
        self._on_secondary_menu_click(menu_id, action_id);
        self._ksCloseMobileDrawer();
      },
    });
  }
);
