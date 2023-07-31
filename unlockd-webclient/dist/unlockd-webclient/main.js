"use strict";
(self["webpackChunkunlockd_webclient"] = self["webpackChunkunlockd_webclient"] || []).push([["main"],{

/***/ 3966:
/*!***************************************!*\
  !*** ./src/app/app-routing.module.ts ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AppRoutingModule: () => (/* binding */ AppRoutingModule)
/* harmony export */ });
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/router */ 7947);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ 1699);



const routes = [];
class AppRoutingModule {}
AppRoutingModule.ɵfac = function AppRoutingModule_Factory(t) {
  return new (t || AppRoutingModule)();
};
AppRoutingModule.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdefineNgModule"]({
  type: AppRoutingModule
});
AppRoutingModule.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdefineInjector"]({
  imports: [_angular_router__WEBPACK_IMPORTED_MODULE_1__.RouterModule.forRoot(routes), _angular_router__WEBPACK_IMPORTED_MODULE_1__.RouterModule]
});

(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵsetNgModuleScope"](AppRoutingModule, {
    imports: [_angular_router__WEBPACK_IMPORTED_MODULE_1__.RouterModule],
    exports: [_angular_router__WEBPACK_IMPORTED_MODULE_1__.RouterModule]
  });
})();

/***/ }),

/***/ 6401:
/*!**********************************!*\
  !*** ./src/app/app.component.ts ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AppComponent: () => (/* binding */ AppComponent)
/* harmony export */ });
/* harmony import */ var _app_login_dialog_login_dialog_component__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../app/login-dialog/login-dialog.component */ 3274);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ 1699);
/* harmony import */ var _app_lightning_service__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../app/lightning.service */ 707);
/* harmony import */ var _angular_material_dialog__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/material/dialog */ 7401);
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/router */ 7947);
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/common */ 6575);
/* harmony import */ var _angular_material_button__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @angular/material/button */ 895);
/* harmony import */ var _angular_material_icon__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @angular/material/icon */ 6515);
/* harmony import */ var _angular_material_menu__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @angular/material/menu */ 8128);









function AppComponent_span_17_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](1, "Welcome, ");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](2, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate1"](" ", ctx_r0.userTitle, " ");
  }
}
function AppComponent_span_18_button_47_Template(rf, ctx) {
  if (rf & 1) {
    const _r7 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "button", 56);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function AppComponent_span_18_button_47_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r7);
      const ctx_r6 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r6.logout());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](1, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](2, "logout");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](3, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](4, "Logout");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
  }
}
function AppComponent_span_18_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "span")(1, "span")(2, "button", 45)(3, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](4, "admin_panel_settings");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](5, "mat-menu", null, 46)(7, "button", 47)(8, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](9, "calendar_month");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](10, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](11, "semesters");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](12, "button", 48)(13, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](14, "cast for education");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](15, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](16, "Courses");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](17, "button", 49)(18, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](19, "group");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](20, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](21, "Users");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](22, "button", 50)(23, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](24, "event_list");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](25, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](26, "Roles");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](27, "button", 45)(28, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](29, "more_vert");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](30, "mat-menu", null, 51)(32, "button", 52)(33, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](34, "person");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](35, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](36, "profile");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](37, "button", 53)(38, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](39, "list");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](40, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](41, "My Course List");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](42, "button", 54)(43, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](44, "checklist");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](45, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](46, "Course Sign Ups");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](47, AppComponent_span_18_button_47_Template, 5, 0, "button", 55);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const _r3 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵreference"](6);
    const _r4 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵreference"](31);
    const ctx_r1 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("matMenuTriggerFor", _r3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](25);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("matMenuTriggerFor", _r4);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](20);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx_r1.logoutButtonVisible);
  }
}
function AppComponent_button_19_Template(rf, ctx) {
  if (rf & 1) {
    const _r9 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "button", 57);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function AppComponent_button_19_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r9);
      const ctx_r8 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r8.loginChallenge());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](1, "Login");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
  }
}
class AppComponent {
  constructor(lightningService, dialog, router) {
    this.lightningService = lightningService;
    this.dialog = dialog;
    this.router = router;
    this.title = 'unlockd-webclient';
    this.qrcodesrc = '';
    this.loginComplete = false;
    this.loginButtonVisible = false;
    this.logoutButtonVisible = false;
    this.userTitle = "Lightning User";
  }
  ngOnInit() {
    if (localStorage.getItem("token") === null) {
      this.loginButtonVisible = true;
      this.logoutButtonVisible = false;
    } else {
      this.loginButtonVisible = false;
      this.logoutButtonVisible = true;
    }
    if (localStorage.getItem("usertitle") === null) {
      console.log('usertitle not found in localstorage');
    } else {
      this.userTitle = localStorage.getItem("usertitle") || "";
    }
    if (localStorage.getItem("role") === null) {
      console.log('role not found in localstorage');
    } else {
      var role_str = localStorage.getItem("role") || "";
      console.log('roleObject: ', JSON.parse(role_str));
      //this.role = JSON.parse(role_str);
    }
    // Subscribe to the login user in lightning service to know if we need to run auth again
    this.lightningService.login_user.subscribe(value => {
      console.log('lightning service requesting re-authentication');
      // Only do this if there is an old token in localstorage
      if (localStorage.getItem('token')) {
        console.log('found an old token');
        this.loginChallenge();
      }
    });
  }
  loginChallenge() {
    console.log('App Component Login pressed');
    this.lightningService.loginChallenge().subscribe(authchall => {
      this.authchall = authchall;
      this.qrcodesrc = 'http://54.219.218.253/generate_qr/' + authchall.lnurl;
      // open the login dialog
      this.dialog.open(_app_login_dialog_login_dialog_component__WEBPACK_IMPORTED_MODULE_0__.LoginDialogComponent, {
        data: {
          lnurl: this.authchall,
          qrcodesrc: this.qrcodesrc
        }
      });
    });
  }
  closeDialog() {
    this.dialog.closeAll();
  }
  logout() {
    this.lightningService.doLogout();
    this.loginButtonVisible = true;
    this.logoutButtonVisible = false;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    //localStorage.removeItem('role');
    this.router.navigate(['']);
  }
}
AppComponent.ɵfac = function AppComponent_Factory(t) {
  return new (t || AppComponent)(_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdirectiveInject"](_app_lightning_service__WEBPACK_IMPORTED_MODULE_1__.LightningService), _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdirectiveInject"](_angular_material_dialog__WEBPACK_IMPORTED_MODULE_3__.MatDialog), _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdirectiveInject"](_angular_router__WEBPACK_IMPORTED_MODULE_4__.Router));
};
AppComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdefineComponent"]({
  type: AppComponent,
  selectors: [["app-root"]],
  decls: 187,
  vars: 3,
  consts: [["role", "banner", 1, "toolbar"], ["width", "40", "alt", "Angular Logo", "src", "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTAgMjUwIj4KICAgIDxwYXRoIGZpbGw9IiNERDAwMzEiIGQ9Ik0xMjUgMzBMMzEuOSA2My4ybDE0LjIgMTIzLjFMMTI1IDIzMGw3OC45LTQzLjcgMTQuMi0xMjMuMXoiIC8+CiAgICA8cGF0aCBmaWxsPSIjQzMwMDJGIiBkPSJNMTI1IDMwdjIyLjItLjFWMjMwbDc4LjktNDMuNyAxNC4yLTEyMy4xTDEyNSAzMHoiIC8+CiAgICA8cGF0aCAgZmlsbD0iI0ZGRkZGRiIgZD0iTTEyNSA1Mi4xTDY2LjggMTgyLjZoMjEuN2wxMS43LTI5LjJoNDkuNGwxMS43IDI5LjJIMTgzTDEyNSA1Mi4xem0xNyA4My4zaC0zNGwxNy00MC45IDE3IDQwLjl6IiAvPgogIDwvc3ZnPg=="], ["mat-button", "", "routerLink", "/"], ["mat-button", "", "routerLink", "/pages/news"], ["mat-button", "", "routerLink", "/pages/about"], ["mat-button", "", "routerLink", "/course-list"], ["mat-button", "", "routerLink", "/pages/membership"], ["mat-button", "", "routerLink", "/pages/opportunities"], ["mat-button", "", "routerLink", "/pages/contact"], [1, "spacer"], [4, "ngIf"], ["mat-raised-button", "", 3, "click", 4, "ngIf"], ["role", "main", 1, "content"], ["id", "container"], ["id", "recent"], [1, "tag"], [1, "fourcolcontent", "post"], ["href", "#"], ["id", "comments", 1, "fourcolside"], [1, "clear"], [1, "divider"], ["id", "older"], [1, "fourcolside", "post"], ["href", "https://discord.gg/QXQkq4dhdx"], ["id", "navigate"], [1, "fourcolside"], ["href", "https://github.com/unlockd-gg/ExampleGame"], ["href", "https://github.com/unlockd-gg/online-subsystem"], ["href", "https://github.com/unlockd-gg/metagame"], ["href", "https://github.com/unlockd-gg/backend"], ["href", "https://github.com/unlockd-gg/UnrealEngine"], ["href", "https://github.com/unlockd-gg/socketIO-server"], ["href", "https://github.com/unlockd-gg/launcher"], ["href", "/img/btc_donations.png"], ["href", "https://getalby.com/element.png"], ["href", "https://uetopia.com"], ["href", "https://github.com/uetopia/"], [1, "fourcolsidesmall"], ["href", "http://www.gregponchak.com"], ["id", "header"], ["id", "headerinner"], ["id", "title", 1, "fourcolside"], ["id", "description", 1, "fourcolside"], ["id", "navigation", 1, "fourcolside"], ["href", "https://github.com/unlockd-gg/"], ["mat-icon-button", "", "aria-label", "Example icon-button with a menu", 3, "matMenuTriggerFor"], ["adminmenu", "matMenu"], ["mat-menu-item", "", "routerLink", "admin-semesters"], ["mat-menu-item", "", "routerLink", "admin-courses"], ["mat-menu-item", "", "routerLink", "admin-users"], ["mat-menu-item", "", "routerLink", "admin-roles"], ["menu", "matMenu"], ["mat-menu-item", "", "routerLink", "profile"], ["mat-menu-item", "", "routerLink", "enrollment-list"], ["mat-menu-item", "", "routerLink", "semester-signup"], ["mat-menu-item", "", 3, "click", 4, "ngIf"], ["mat-menu-item", "", 3, "click"], ["mat-raised-button", "", 3, "click"]],
  template: function AppComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "div", 0);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](1, "img", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](2, "button", 2);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](3, "HOME");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](4, "button", 3);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](5, "NEWS");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](6, "button", 4);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](7, "ABOUT");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](8, "button", 5);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](9, "COURSES");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](10, "button", 6);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](11, "MEMBERSHIP");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](12, "button", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](13, "OPPORTUNITIES");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](14, "button", 8);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](15, "CONTACT");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](16, "div", 9);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](17, AppComponent_span_17_Template, 4, 1, "span", 10);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](18, AppComponent_span_18_Template, 48, 3, "span", 10);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](19, AppComponent_button_19_Template, 2, 0, "button", 11);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](20, "div", 12)(21, "div", 13)(22, "div", 14)(23, "div", 15);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](24, "Now");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](25, "div", 16)(26, "h3")(27, "a", 17);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](28, "uetopia is unlockd");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](29, " We are moving beyond only supporting Unreal Engine, and aim to support all multiplayer game engines. Godot, Unity, and Lumberyard devs - LFG! We are also making some changes to support our ethics and mission. Open source, decentralization, and bitcoin. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](30, "div", 18)(31, "h5")(32, "a", 17);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](33, "21");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](34, "div", 19);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](35, "div", 20);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](36, "div", 21)(37, "div", 15);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](38, "Mission");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](39, "div", 22)(40, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](41, "Bitcoin Only");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](42, " We are exclusively focused on bitcoin. No site token, no shi*coins. It's btc and lightning ftw. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](43, "div", 22)(44, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](45, "Support developers");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](46, " Indie and small studios need backend game solutions. Providing complete open source access allows devs and studios to run a customized backend. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](47, "div", 22)(48, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](49, "Promote decentralization");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](50, " Multiplayer games still require high performance, realtime, dedicated servers. Especially in the case of competitive games, or games with an economy, these servers need to be under control of the game developer. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](51, "div", 22)(52, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](53, "Encourage self custody");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](54, " We remind users to withdraw sats from the site at the end of a gaming session. We will provide help and instructions on how to do this. Lightning makes deposit and withdraw quick and easy. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](55, "div", 19);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](56, "div", 20);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](57, "div", 21)(58, "div", 15);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](59, "TASKS");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](60, "div", 22)(61, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](62, "Convert backend to python 3 runtime");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](63, " Python 2.7 is no longer supported, and we need to convert. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](64, "div", 22)(65, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](66, "Convert metagame to python 3 runtime");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](67, " Python 2.7 is no longer supported, and we need to convert. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](68, "div", 22)(69, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](70, "Convert examplegame to use pub/priv key auth");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](71, " Remove firebase auth and replace with lnurl login. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](72, "div", 22)(73, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](74, "Integrate lightning deposit/withdraw");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](75, " Remove braintree payments, and replace with lightning. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](76, "div", 22)(77, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](78, "Remove uetopia references throughout");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](79, " uetopia is mentioned throughout the codebase, and we need to replace it. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](80, "div", 22)(81, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](82, "Sunsetting uetopia");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](83, " The uetopia website and legacy functionality will be retained until January 2024. Users and games should run a backend instance or find an alternative before this time. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](84, "div", 22)(85, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](86, "Community Discord");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](87, "a", 23);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](88, "Discord Server");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](89, " up and running. Stop by and chat about games. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](90, "div", 19);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](91, "div", 20);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](92, "div", 24)(93, "div", 15);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](94, "Navigate");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](95, "div", 25)(96, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](97, "Repositories");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](98, "ul")(99, "li")(100, "a", 26);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](101, "Example Game");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](102, "li")(103, "a", 27);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](104, "Unreal Engine Plugin");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](105, "li")(106, "a", 28);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](107, "Metagame");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](108, "li")(109, "a", 29);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](110, "Backend");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](111, "li")(112, "a", 30);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](113, "Unreal Engine");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](114, "li")(115, "a", 31);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](116, "SocketIO Server");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](117, "li")(118, "a", 32);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](119, "Launcher");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](120, "div", 25)(121, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](122, "Social");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](123, "ul")(124, "li")(125, "a", 23);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](126, "Discord");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](127, "li")(128, "a", 17);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](129, "Twitter");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](130, "li")(131, "a", 17);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](132, "Blog");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](133, "div", 25)(134, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](135, "Support");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](136, "ul")(137, "li")(138, "a", 33);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](139, "bitcoin donations");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](140, "li")(141, "a", 34);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](142, "lightning donations");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](143, "div", 25)(144, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](145, "uetopia/legacy");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](146, "ul")(147, "li")(148, "a", 35);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](149, "Backend");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](150, "li")(151, "a", 36);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](152, "Repositories");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](153, "div", 19);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](154, "div", 19)(155, "div", 20);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](156, "div", 25);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](157, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](158, "div", 25);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](159, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](160, "div", 25);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](161, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](162, "div", 37);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](163, "This page designed and coded by ");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](164, "a", 38);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](165, "Greg Ponchak");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](166, ".");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](167, "div", 39)(168, "div", 40)(169, "div", 41)(170, "h1")(171, "a", 17);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](172, "unlockd.gg");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](173, "div", 42)(174, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](175, "Open Game Backend");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](176, "div", 25);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](177, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](178, "div", 43)(179, "a", 17);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](180, "Home");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](181, "a", 44);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](182, "Contribute");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](183, "a", 23);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](184, "Discuss");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](185, "div", 19);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](186, "router-outlet");
    }
    if (rf & 2) {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](17);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.logoutButtonVisible);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.logoutButtonVisible);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.loginButtonVisible);
    }
  },
  dependencies: [_angular_common__WEBPACK_IMPORTED_MODULE_5__.NgIf, _angular_router__WEBPACK_IMPORTED_MODULE_4__.RouterOutlet, _angular_router__WEBPACK_IMPORTED_MODULE_4__.RouterLink, _angular_material_button__WEBPACK_IMPORTED_MODULE_6__.MatButton, _angular_material_button__WEBPACK_IMPORTED_MODULE_6__.MatIconButton, _angular_material_icon__WEBPACK_IMPORTED_MODULE_7__.MatIcon, _angular_material_menu__WEBPACK_IMPORTED_MODULE_8__.MatMenu, _angular_material_menu__WEBPACK_IMPORTED_MODULE_8__.MatMenuItem, _angular_material_menu__WEBPACK_IMPORTED_MODULE_8__.MatMenuTrigger],
  styles: ["*[_ngcontent-%COMP%]\n{\n\tlist-style:none;\n\ttext-decoration:none;\n\tborder:0;\n\tfont-weight:400;\n\tmargin:0;\n\tpadding:0;\n}\n\nbody[_ngcontent-%COMP%]\n{\n\tbackground:#fff;\n\tfont-family:helvetica, arial, sans-serif;\n\tcolor:#333;\n\tline-height:18px;\n\tfont-size:11px;\n}\n\na[_ngcontent-%COMP%]\n{\n\tcolor:#BE04F4;\n\ttext-decoration:none;\n}\n\na[_ngcontent-%COMP%]:hover\n{\n\ttext-decoration:none;\n}\n\nb[_ngcontent-%COMP%]\n{\n\tfont-weight:700;\n}\n\nblockquote[_ngcontent-%COMP%]\n{\n\tcolor:#aaa;\n\tpadding:10px;\n}\n\nh1[_ngcontent-%COMP%], h1[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\ttext-decoration:none;\n\tline-height:30px;\n\tfont-size:30px;\n\tcolor:#333;\n}\n\nh2[_ngcontent-%COMP%], h2[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\ttext-decoration:none;\n\tline-height:26px;\n\tfont-size:26px;\n\tcolor:#333;\n}\n\nh3[_ngcontent-%COMP%], h3[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\ttext-decoration:none;\n\tline-height:22px;\n\tfont-size:22px;\n\tcolor:#333;\n}\n\nh4[_ngcontent-%COMP%], h4[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\ttext-decoration:none;\n\tline-height:18px;\n\tfont-size:18px;\n\tcolor:#333;\n}\n\nh5[_ngcontent-%COMP%], h5[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\ttext-decoration:none;\n\tline-height:14px;\n\tfont-size:14px;\n\tcolor:#333;\n}\n\np[_ngcontent-%COMP%]\n{\n\tmargin-bottom:10px;\n}\n\nsmall[_ngcontent-%COMP%]\n{\n\tfont-size:10px;\n}\n\n.clear[_ngcontent-%COMP%]\n{\n\tclear:both;\n}\n\n#container[_ngcontent-%COMP%]\n{\n\twidth:960px;\n\tmargin:110px auto;\n}\n\n.fourcolcontent[_ngcontent-%COMP%]\n{\n\tfloat:left;\n\twidth:710px;\n\tpadding-right:10px;\n\tposition:relative;\n}\n\n.fourcolside[_ngcontent-%COMP%]\n{\n\tfloat:left;\n\twidth:230px;\n\tpadding-right:10px;\n\tposition:relative;\n}\n\n.fourcolsidesmall[_ngcontent-%COMP%]\n{\n\tfont-size:7px;\n\tfloat:left;\n\twidth:230px;\n\tpadding-right:10px;\n\tposition:relative;\n}\n\n.divider[_ngcontent-%COMP%]\n{\n\theight:7px;\n\twidth:100%;\n\tbackground:#333;\n\tmargin:30px 0;\n}\n\n.tag[_ngcontent-%COMP%]\n{\n\ttext-align:right;\n\tright:965px;\n\tposition:absolute;\n\tbackground:#BE04F4;\n\tcolor:#fff;\n\ttext-transform:uppercase;\n\tpadding:2px;\n}\n\n#header[_ngcontent-%COMP%]\n{\n\theight:55px;\n\tbackground:#fff;\n\tleft:0;\n\tposition:fixed !important;\n\tposition:absolute;\n\tright:0;\n\ttop:0;\n}\n\n#headerinner[_ngcontent-%COMP%]\n{\n\tmargin:0 auto;\n\twidth:960px;\n}\n\n#header[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]\n{\n\toverflow:hidden;\n}\n\n#title[_ngcontent-%COMP%]   h1[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tcolor:#333;\n\tfont-size:21px;\n\tline-height:80px;\n\tfont-weight:700;\n}\n\n#description[_ngcontent-%COMP%]   h3[_ngcontent-%COMP%]\n{\n\tcolor:#333;\n\tfont-size:16px;\n\tline-height:80px;\n}\n\n#navigation[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tline-height:80px;\n\tpadding:0 10px;\n}\n\n#recent[_ngcontent-%COMP%]   .post[_ngcontent-%COMP%]   h3[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tfont-size:36px;\n\tline-height:36px;\n\tcolor:#333;\n\tpadding-bottom:10px;\n\tfont-weight:700;\n}\n\n#recent[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]   h5[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tfont-size:72px;\n\ttext-align:center;\n\tline-height:72px;\n\tpadding-top:36px;\n\tdisplay:block;\n\tfont-weight:700;\n}\n\n#comments[_ngcontent-%COMP%]\n{\n\ttext-align:center;\n}\n\n#recent[_ngcontent-%COMP%], #older[_ngcontent-%COMP%], #navigate[_ngcontent-%COMP%]\n{\n\tposition:relative;\n}\n\n#older[_ngcontent-%COMP%]   .post[_ngcontent-%COMP%]\n{\n\tcolor:#aaa;\n\tmax-height:144px;\n\toverflow:hidden;\n\tborder-bottom:7px solid #fff;\n\tmargin-bottom:3px;\n}\n\n#older[_ngcontent-%COMP%]   .post[_ngcontent-%COMP%]:hover\n{\n\tborder-bottom:7px solid #BE04F4;\n\tcolor:#888;\n}\n\n#older[_ngcontent-%COMP%]   .post[_ngcontent-%COMP%]:hover   h3[_ngcontent-%COMP%]\n{\n\tcolor:#333;\n}\n\n#older[_ngcontent-%COMP%]   .more[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tfont-size:60px;\n\tline-height:60px;\n\ttext-transform:uppercase;\n\tcolor:#aaa;\n\tbackground:#ddd;\n\tmargin-top:10px;\n\tdisplay:block;\n\ttext-align:center;\n\tpadding:10px;\n}\n\n#older[_ngcontent-%COMP%]   .more[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]:hover\n{\n\tcolor:#999;\n\tbackground:#ccc;\n}\n\n#navigate[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]   ul[_ngcontent-%COMP%]   li[_ngcontent-%COMP%]\n{\n\tdisplay:inline;\n}\n\n#navigate[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]   ul[_ngcontent-%COMP%]   li[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tdisplay:block;\n\tcolor:#aaa;\n\tpadding:2px;\n}\n\n#navigate[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]   ul[_ngcontent-%COMP%]   li[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]:hover\n{\n\tcolor:#ff00c0;\n}\n\n#older[_ngcontent-%COMP%]   .post[_ngcontent-%COMP%]   h3[_ngcontent-%COMP%], #navigate[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]   h3[_ngcontent-%COMP%]\n{\n\tfont-size:18px;\n\tline-height:18px;\n\tcolor:#999;\n}\n\n\n/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8uL3NyYy9hcHAvYXBwLmNvbXBvbmVudC5jc3MiXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IkFBQUE7O0NBRUMsZUFBZTtDQUNmLG9CQUFvQjtDQUNwQixRQUFRO0NBQ1IsZUFBZTtDQUNmLFFBQVE7Q0FDUixTQUFTO0FBQ1Y7O0FBRUE7O0NBRUMsZUFBZTtDQUNmLHdDQUF3QztDQUN4QyxVQUFVO0NBQ1YsZ0JBQWdCO0NBQ2hCLGNBQWM7QUFDZjs7QUFFQTs7Q0FFQyxhQUFhO0NBQ2Isb0JBQW9CO0FBQ3JCOztBQUVBOztDQUVDLG9CQUFvQjtBQUNyQjs7QUFFQTs7Q0FFQyxlQUFlO0FBQ2hCOztBQUVBOztDQUVDLFVBQVU7Q0FDVixZQUFZO0FBQ2I7O0FBRUE7O0NBRUMsb0JBQW9CO0NBQ3BCLGdCQUFnQjtDQUNoQixjQUFjO0NBQ2QsVUFBVTtBQUNYOztBQUVBOztDQUVDLG9CQUFvQjtDQUNwQixnQkFBZ0I7Q0FDaEIsY0FBYztDQUNkLFVBQVU7QUFDWDs7QUFFQTs7Q0FFQyxvQkFBb0I7Q0FDcEIsZ0JBQWdCO0NBQ2hCLGNBQWM7Q0FDZCxVQUFVO0FBQ1g7O0FBRUE7O0NBRUMsb0JBQW9CO0NBQ3BCLGdCQUFnQjtDQUNoQixjQUFjO0NBQ2QsVUFBVTtBQUNYOztBQUVBOztDQUVDLG9CQUFvQjtDQUNwQixnQkFBZ0I7Q0FDaEIsY0FBYztDQUNkLFVBQVU7QUFDWDs7QUFFQTs7Q0FFQyxrQkFBa0I7QUFDbkI7O0FBRUE7O0NBRUMsY0FBYztBQUNmOztBQUVBOztDQUVDLFVBQVU7QUFDWDs7QUFFQTs7Q0FFQyxXQUFXO0NBQ1gsaUJBQWlCO0FBQ2xCOztBQUVBOztDQUVDLFVBQVU7Q0FDVixXQUFXO0NBQ1gsa0JBQWtCO0NBQ2xCLGlCQUFpQjtBQUNsQjs7QUFFQTs7Q0FFQyxVQUFVO0NBQ1YsV0FBVztDQUNYLGtCQUFrQjtDQUNsQixpQkFBaUI7QUFDbEI7O0FBRUE7O0NBRUMsYUFBYTtDQUNiLFVBQVU7Q0FDVixXQUFXO0NBQ1gsa0JBQWtCO0NBQ2xCLGlCQUFpQjtBQUNsQjs7QUFFQTs7Q0FFQyxVQUFVO0NBQ1YsVUFBVTtDQUNWLGVBQWU7Q0FDZixhQUFhO0FBQ2Q7O0FBRUE7O0NBRUMsZ0JBQWdCO0NBQ2hCLFdBQVc7Q0FDWCxpQkFBaUI7Q0FDakIsa0JBQWtCO0NBQ2xCLFVBQVU7Q0FDVix3QkFBd0I7Q0FDeEIsV0FBVztBQUNaOztBQUVBOztDQUVDLFdBQVc7Q0FDWCxlQUFlO0NBQ2YsTUFBTTtDQUNOLHlCQUF5QjtDQUN6QixpQkFBaUI7Q0FDakIsT0FBTztDQUNQLEtBQUs7QUFDTjs7QUFFQTs7Q0FFQyxhQUFhO0NBQ2IsV0FBVztBQUNaOztBQUVBOztDQUVDLGVBQWU7QUFDaEI7O0FBRUE7O0NBRUMsVUFBVTtDQUNWLGNBQWM7Q0FDZCxnQkFBZ0I7Q0FDaEIsZUFBZTtBQUNoQjs7QUFFQTs7Q0FFQyxVQUFVO0NBQ1YsY0FBYztDQUNkLGdCQUFnQjtBQUNqQjs7QUFFQTs7Q0FFQyxnQkFBZ0I7Q0FDaEIsY0FBYztBQUNmOztBQUVBOztDQUVDLGNBQWM7Q0FDZCxnQkFBZ0I7Q0FDaEIsVUFBVTtDQUNWLG1CQUFtQjtDQUNuQixlQUFlO0FBQ2hCOztBQUVBOztDQUVDLGNBQWM7Q0FDZCxpQkFBaUI7Q0FDakIsZ0JBQWdCO0NBQ2hCLGdCQUFnQjtDQUNoQixhQUFhO0NBQ2IsZUFBZTtBQUNoQjs7QUFFQTs7Q0FFQyxpQkFBaUI7QUFDbEI7O0FBRUE7O0NBRUMsaUJBQWlCO0FBQ2xCOztBQUVBOztDQUVDLFVBQVU7Q0FDVixnQkFBZ0I7Q0FDaEIsZUFBZTtDQUNmLDRCQUE0QjtDQUM1QixpQkFBaUI7QUFDbEI7O0FBRUE7O0NBRUMsK0JBQStCO0NBQy9CLFVBQVU7QUFDWDs7QUFFQTs7Q0FFQyxVQUFVO0FBQ1g7O0FBRUE7O0NBRUMsY0FBYztDQUNkLGdCQUFnQjtDQUNoQix3QkFBd0I7Q0FDeEIsVUFBVTtDQUNWLGVBQWU7Q0FDZixlQUFlO0NBQ2YsYUFBYTtDQUNiLGlCQUFpQjtDQUNqQixZQUFZO0FBQ2I7O0FBRUE7O0NBRUMsVUFBVTtDQUNWLGVBQWU7QUFDaEI7O0FBRUE7O0NBRUMsY0FBYztBQUNmOztBQUVBOztDQUVDLGFBQWE7Q0FDYixVQUFVO0NBQ1YsV0FBVztBQUNaOztBQUVBOztDQUVDLGFBQWE7QUFDZDs7QUFFQTs7Q0FFQyxjQUFjO0NBQ2QsZ0JBQWdCO0NBQ2hCLFVBQVU7QUFDWCIsInNvdXJjZXNDb250ZW50IjpbIipcclxue1xyXG5cdGxpc3Qtc3R5bGU6bm9uZTtcclxuXHR0ZXh0LWRlY29yYXRpb246bm9uZTtcclxuXHRib3JkZXI6MDtcclxuXHRmb250LXdlaWdodDo0MDA7XHJcblx0bWFyZ2luOjA7XHJcblx0cGFkZGluZzowO1xyXG59XHJcblxyXG5ib2R5XHJcbntcclxuXHRiYWNrZ3JvdW5kOiNmZmY7XHJcblx0Zm9udC1mYW1pbHk6aGVsdmV0aWNhLCBhcmlhbCwgc2Fucy1zZXJpZjtcclxuXHRjb2xvcjojMzMzO1xyXG5cdGxpbmUtaGVpZ2h0OjE4cHg7XHJcblx0Zm9udC1zaXplOjExcHg7XHJcbn1cclxuXHJcbmFcclxue1xyXG5cdGNvbG9yOiNCRTA0RjQ7XHJcblx0dGV4dC1kZWNvcmF0aW9uOm5vbmU7XHJcbn1cclxuXHJcbmE6aG92ZXJcclxue1xyXG5cdHRleHQtZGVjb3JhdGlvbjpub25lO1xyXG59XHJcblxyXG5iXHJcbntcclxuXHRmb250LXdlaWdodDo3MDA7XHJcbn1cclxuXHJcbmJsb2NrcXVvdGVcclxue1xyXG5cdGNvbG9yOiNhYWE7XHJcblx0cGFkZGluZzoxMHB4O1xyXG59XHJcblxyXG5oMSxoMSBhXHJcbntcclxuXHR0ZXh0LWRlY29yYXRpb246bm9uZTtcclxuXHRsaW5lLWhlaWdodDozMHB4O1xyXG5cdGZvbnQtc2l6ZTozMHB4O1xyXG5cdGNvbG9yOiMzMzM7XHJcbn1cclxuXHJcbmgyLGgyIGFcclxue1xyXG5cdHRleHQtZGVjb3JhdGlvbjpub25lO1xyXG5cdGxpbmUtaGVpZ2h0OjI2cHg7XHJcblx0Zm9udC1zaXplOjI2cHg7XHJcblx0Y29sb3I6IzMzMztcclxufVxyXG5cclxuaDMsaDMgYVxyXG57XHJcblx0dGV4dC1kZWNvcmF0aW9uOm5vbmU7XHJcblx0bGluZS1oZWlnaHQ6MjJweDtcclxuXHRmb250LXNpemU6MjJweDtcclxuXHRjb2xvcjojMzMzO1xyXG59XHJcblxyXG5oNCxoNCBhXHJcbntcclxuXHR0ZXh0LWRlY29yYXRpb246bm9uZTtcclxuXHRsaW5lLWhlaWdodDoxOHB4O1xyXG5cdGZvbnQtc2l6ZToxOHB4O1xyXG5cdGNvbG9yOiMzMzM7XHJcbn1cclxuXHJcbmg1LGg1IGFcclxue1xyXG5cdHRleHQtZGVjb3JhdGlvbjpub25lO1xyXG5cdGxpbmUtaGVpZ2h0OjE0cHg7XHJcblx0Zm9udC1zaXplOjE0cHg7XHJcblx0Y29sb3I6IzMzMztcclxufVxyXG5cclxucFxyXG57XHJcblx0bWFyZ2luLWJvdHRvbToxMHB4O1xyXG59XHJcblxyXG5zbWFsbFxyXG57XHJcblx0Zm9udC1zaXplOjEwcHg7XHJcbn1cclxuXHJcbi5jbGVhclxyXG57XHJcblx0Y2xlYXI6Ym90aDtcclxufVxyXG5cclxuI2NvbnRhaW5lclxyXG57XHJcblx0d2lkdGg6OTYwcHg7XHJcblx0bWFyZ2luOjExMHB4IGF1dG87XHJcbn1cclxuXHJcbi5mb3VyY29sY29udGVudFxyXG57XHJcblx0ZmxvYXQ6bGVmdDtcclxuXHR3aWR0aDo3MTBweDtcclxuXHRwYWRkaW5nLXJpZ2h0OjEwcHg7XHJcblx0cG9zaXRpb246cmVsYXRpdmU7XHJcbn1cclxuXHJcbi5mb3VyY29sc2lkZVxyXG57XHJcblx0ZmxvYXQ6bGVmdDtcclxuXHR3aWR0aDoyMzBweDtcclxuXHRwYWRkaW5nLXJpZ2h0OjEwcHg7XHJcblx0cG9zaXRpb246cmVsYXRpdmU7XHJcbn1cclxuXHJcbi5mb3VyY29sc2lkZXNtYWxsXHJcbntcclxuXHRmb250LXNpemU6N3B4O1xyXG5cdGZsb2F0OmxlZnQ7XHJcblx0d2lkdGg6MjMwcHg7XHJcblx0cGFkZGluZy1yaWdodDoxMHB4O1xyXG5cdHBvc2l0aW9uOnJlbGF0aXZlO1xyXG59XHJcblxyXG4uZGl2aWRlclxyXG57XHJcblx0aGVpZ2h0OjdweDtcclxuXHR3aWR0aDoxMDAlO1xyXG5cdGJhY2tncm91bmQ6IzMzMztcclxuXHRtYXJnaW46MzBweCAwO1xyXG59XHJcblxyXG4udGFnXHJcbntcclxuXHR0ZXh0LWFsaWduOnJpZ2h0O1xyXG5cdHJpZ2h0Ojk2NXB4O1xyXG5cdHBvc2l0aW9uOmFic29sdXRlO1xyXG5cdGJhY2tncm91bmQ6I0JFMDRGNDtcclxuXHRjb2xvcjojZmZmO1xyXG5cdHRleHQtdHJhbnNmb3JtOnVwcGVyY2FzZTtcclxuXHRwYWRkaW5nOjJweDtcclxufVxyXG5cclxuI2hlYWRlclxyXG57XHJcblx0aGVpZ2h0OjU1cHg7XHJcblx0YmFja2dyb3VuZDojZmZmO1xyXG5cdGxlZnQ6MDtcclxuXHRwb3NpdGlvbjpmaXhlZCAhaW1wb3J0YW50O1xyXG5cdHBvc2l0aW9uOmFic29sdXRlO1xyXG5cdHJpZ2h0OjA7XHJcblx0dG9wOjA7XHJcbn1cclxuXHJcbiNoZWFkZXJpbm5lclxyXG57XHJcblx0bWFyZ2luOjAgYXV0bztcclxuXHR3aWR0aDo5NjBweDtcclxufVxyXG5cclxuI2hlYWRlciAuZm91cmNvbHNpZGVcclxue1xyXG5cdG92ZXJmbG93OmhpZGRlbjtcclxufVxyXG5cclxuI3RpdGxlIGgxIGFcclxue1xyXG5cdGNvbG9yOiMzMzM7XHJcblx0Zm9udC1zaXplOjIxcHg7XHJcblx0bGluZS1oZWlnaHQ6ODBweDtcclxuXHRmb250LXdlaWdodDo3MDA7XHJcbn1cclxuXHJcbiNkZXNjcmlwdGlvbiBoM1xyXG57XHJcblx0Y29sb3I6IzMzMztcclxuXHRmb250LXNpemU6MTZweDtcclxuXHRsaW5lLWhlaWdodDo4MHB4O1xyXG59XHJcblxyXG4jbmF2aWdhdGlvbiBhXHJcbntcclxuXHRsaW5lLWhlaWdodDo4MHB4O1xyXG5cdHBhZGRpbmc6MCAxMHB4O1xyXG59XHJcblxyXG4jcmVjZW50IC5wb3N0IGgzIGFcclxue1xyXG5cdGZvbnQtc2l6ZTozNnB4O1xyXG5cdGxpbmUtaGVpZ2h0OjM2cHg7XHJcblx0Y29sb3I6IzMzMztcclxuXHRwYWRkaW5nLWJvdHRvbToxMHB4O1xyXG5cdGZvbnQtd2VpZ2h0OjcwMDtcclxufVxyXG5cclxuI3JlY2VudCAuZm91cmNvbHNpZGUgaDUgYVxyXG57XHJcblx0Zm9udC1zaXplOjcycHg7XHJcblx0dGV4dC1hbGlnbjpjZW50ZXI7XHJcblx0bGluZS1oZWlnaHQ6NzJweDtcclxuXHRwYWRkaW5nLXRvcDozNnB4O1xyXG5cdGRpc3BsYXk6YmxvY2s7XHJcblx0Zm9udC13ZWlnaHQ6NzAwO1xyXG59XHJcblxyXG4jY29tbWVudHNcclxue1xyXG5cdHRleHQtYWxpZ246Y2VudGVyO1xyXG59XHJcblxyXG4jcmVjZW50LCNvbGRlciwjbmF2aWdhdGVcclxue1xyXG5cdHBvc2l0aW9uOnJlbGF0aXZlO1xyXG59XHJcblxyXG4jb2xkZXIgLnBvc3Rcclxue1xyXG5cdGNvbG9yOiNhYWE7XHJcblx0bWF4LWhlaWdodDoxNDRweDtcclxuXHRvdmVyZmxvdzpoaWRkZW47XHJcblx0Ym9yZGVyLWJvdHRvbTo3cHggc29saWQgI2ZmZjtcclxuXHRtYXJnaW4tYm90dG9tOjNweDtcclxufVxyXG5cclxuI29sZGVyIC5wb3N0OmhvdmVyXHJcbntcclxuXHRib3JkZXItYm90dG9tOjdweCBzb2xpZCAjQkUwNEY0O1xyXG5cdGNvbG9yOiM4ODg7XHJcbn1cclxuXHJcbiNvbGRlciAucG9zdDpob3ZlciBoM1xyXG57XHJcblx0Y29sb3I6IzMzMztcclxufVxyXG5cclxuI29sZGVyIC5tb3JlIGFcclxue1xyXG5cdGZvbnQtc2l6ZTo2MHB4O1xyXG5cdGxpbmUtaGVpZ2h0OjYwcHg7XHJcblx0dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlO1xyXG5cdGNvbG9yOiNhYWE7XHJcblx0YmFja2dyb3VuZDojZGRkO1xyXG5cdG1hcmdpbi10b3A6MTBweDtcclxuXHRkaXNwbGF5OmJsb2NrO1xyXG5cdHRleHQtYWxpZ246Y2VudGVyO1xyXG5cdHBhZGRpbmc6MTBweDtcclxufVxyXG5cclxuI29sZGVyIC5tb3JlIGE6aG92ZXJcclxue1xyXG5cdGNvbG9yOiM5OTk7XHJcblx0YmFja2dyb3VuZDojY2NjO1xyXG59XHJcblxyXG4jbmF2aWdhdGUgLmZvdXJjb2xzaWRlIHVsIGxpXHJcbntcclxuXHRkaXNwbGF5OmlubGluZTtcclxufVxyXG5cclxuI25hdmlnYXRlIC5mb3VyY29sc2lkZSB1bCBsaSBhXHJcbntcclxuXHRkaXNwbGF5OmJsb2NrO1xyXG5cdGNvbG9yOiNhYWE7XHJcblx0cGFkZGluZzoycHg7XHJcbn1cclxuXHJcbiNuYXZpZ2F0ZSAuZm91cmNvbHNpZGUgdWwgbGkgYTpob3ZlclxyXG57XHJcblx0Y29sb3I6I2ZmMDBjMDtcclxufVxyXG5cclxuI29sZGVyIC5wb3N0IGgzLCNuYXZpZ2F0ZSAuZm91cmNvbHNpZGUgaDNcclxue1xyXG5cdGZvbnQtc2l6ZToxOHB4O1xyXG5cdGxpbmUtaGVpZ2h0OjE4cHg7XHJcblx0Y29sb3I6Izk5OTtcclxufVxyXG5cclxuIl0sInNvdXJjZVJvb3QiOiIifQ== */", "[_nghost-%COMP%] {\n    font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif, \"Apple Color Emoji\", \"Segoe UI Emoji\", \"Segoe UI Symbol\";\n    font-size: 14px;\n    color: #333;\n    box-sizing: border-box;\n    -webkit-font-smoothing: antialiased;\n    -moz-osx-font-smoothing: grayscale;\n  }\n\n  h1[_ngcontent-%COMP%], h2[_ngcontent-%COMP%], h3[_ngcontent-%COMP%], h4[_ngcontent-%COMP%], h5[_ngcontent-%COMP%], h6[_ngcontent-%COMP%] {\n    margin: 8px 0;\n  }\n\n  p[_ngcontent-%COMP%] {\n    margin: 0;\n  }\n\n  .spacer[_ngcontent-%COMP%] {\n    flex: 1;\n  }\n\n  .toolbar[_ngcontent-%COMP%] {\n    position: absolute;\n    top: 0;\n    left: 0;\n    right: 0;\n    height: 60px;\n    display: flex;\n    align-items: center;\n    background-color: #1976d2;\n    color: white;\n    font-weight: 600;\n  }\n\n  .toolbar[_ngcontent-%COMP%]   img[_ngcontent-%COMP%] {\n    margin: 0 16px;\n  }\n\n  .toolbar[_ngcontent-%COMP%]   #twitter-logo[_ngcontent-%COMP%] {\n    height: 40px;\n    margin: 0 8px;\n  }\n\n  .toolbar[_ngcontent-%COMP%]   #youtube-logo[_ngcontent-%COMP%] {\n    height: 40px;\n    margin: 0 16px;\n  }\n\n  .toolbar[_ngcontent-%COMP%]   #twitter-logo[_ngcontent-%COMP%]:hover, .toolbar[_ngcontent-%COMP%]   #youtube-logo[_ngcontent-%COMP%]:hover {\n    opacity: 0.8;\n  }\n\n  .content[_ngcontent-%COMP%] {\n    display: flex;\n    margin: 82px auto 32px;\n    padding: 0 16px;\n    max-width: 960px;\n    flex-direction: column;\n    align-items: center;\n  }\n\n  svg.material-icons[_ngcontent-%COMP%] {\n    height: 24px;\n    width: auto;\n  }\n\n  svg.material-icons[_ngcontent-%COMP%]:not(:last-child) {\n    margin-right: 8px;\n  }\n\n  .card[_ngcontent-%COMP%]   svg.material-icons[_ngcontent-%COMP%]   path[_ngcontent-%COMP%] {\n    fill: #888;\n  }\n\n  .card-container[_ngcontent-%COMP%] {\n    display: flex;\n    flex-wrap: wrap;\n    justify-content: center;\n    margin-top: 16px;\n  }\n\n  .card[_ngcontent-%COMP%] {\n    all: unset;\n    border-radius: 4px;\n    border: 1px solid #eee;\n    background-color: #fafafa;\n    height: 40px;\n    width: 200px;\n    margin: 0 8px 16px;\n    padding: 16px;\n    display: flex;\n    flex-direction: row;\n    justify-content: center;\n    align-items: center;\n    transition: all 0.2s ease-in-out;\n    line-height: 24px;\n  }\n\n  .card-container[_ngcontent-%COMP%]   .card[_ngcontent-%COMP%]:not(:last-child) {\n    margin-right: 0;\n  }\n\n  .card.card-small[_ngcontent-%COMP%] {\n    height: 16px;\n    width: 168px;\n  }\n\n  .card-container[_ngcontent-%COMP%]   .card[_ngcontent-%COMP%]:not(.highlight-card) {\n    cursor: pointer;\n  }\n\n  .card-container[_ngcontent-%COMP%]   .card[_ngcontent-%COMP%]:not(.highlight-card):hover {\n    transform: translateY(-3px);\n    box-shadow: 0 4px 17px rgba(0, 0, 0, 0.35);\n  }\n\n  .card-container[_ngcontent-%COMP%]   .card[_ngcontent-%COMP%]:not(.highlight-card):hover   .material-icons[_ngcontent-%COMP%]   path[_ngcontent-%COMP%] {\n    fill: rgb(105, 103, 103);\n  }\n\n  .card.highlight-card[_ngcontent-%COMP%] {\n    background-color: #1976d2;\n    color: white;\n    font-weight: 600;\n    border: none;\n    width: auto;\n    min-width: 30%;\n    position: relative;\n  }\n\n  .card.card.highlight-card[_ngcontent-%COMP%]   span[_ngcontent-%COMP%] {\n    margin-left: 60px;\n  }\n\n  svg#rocket[_ngcontent-%COMP%] {\n    width: 80px;\n    position: absolute;\n    left: -10px;\n    top: -24px;\n  }\n\n  svg#rocket-smoke[_ngcontent-%COMP%] {\n    height: calc(100vh - 95px);\n    position: absolute;\n    top: 10px;\n    right: 180px;\n    z-index: -10;\n  }\n\n  a[_ngcontent-%COMP%], a[_ngcontent-%COMP%]:visited, a[_ngcontent-%COMP%]:hover {\n    color: #1976d2;\n    text-decoration: none;\n  }\n\n  a[_ngcontent-%COMP%]:hover {\n    color: #125699;\n  }\n\n  .terminal[_ngcontent-%COMP%] {\n    position: relative;\n    width: 80%;\n    max-width: 600px;\n    border-radius: 6px;\n    padding-top: 45px;\n    margin-top: 8px;\n    overflow: hidden;\n    background-color: rgb(15, 15, 16);\n  }\n\n  .terminal[_ngcontent-%COMP%]::before {\n    content: \"\\2022 \\2022 \\2022\";\n    position: absolute;\n    top: 0;\n    left: 0;\n    height: 4px;\n    background: rgb(58, 58, 58);\n    color: #c2c3c4;\n    width: 100%;\n    font-size: 2rem;\n    line-height: 0;\n    padding: 14px 0;\n    text-indent: 4px;\n  }\n\n  .terminal[_ngcontent-%COMP%]   pre[_ngcontent-%COMP%] {\n    font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;\n    color: white;\n    padding: 0 1rem 1rem;\n    margin: 0;\n  }\n\n  .circle-link[_ngcontent-%COMP%] {\n    height: 40px;\n    width: 40px;\n    border-radius: 40px;\n    margin: 8px;\n    background-color: white;\n    border: 1px solid #eeeeee;\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    cursor: pointer;\n    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);\n    transition: 1s ease-out;\n  }\n\n  .circle-link[_ngcontent-%COMP%]:hover {\n    transform: translateY(-0.25rem);\n    box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.2);\n  }\n\n  footer[_ngcontent-%COMP%] {\n    margin-top: 8px;\n    display: flex;\n    align-items: center;\n    line-height: 20px;\n  }\n\n  footer[_ngcontent-%COMP%]   a[_ngcontent-%COMP%] {\n    display: flex;\n    align-items: center;\n  }\n\n  .github-star-badge[_ngcontent-%COMP%] {\n    color: #24292e;\n    display: flex;\n    align-items: center;\n    font-size: 12px;\n    padding: 3px 10px;\n    border: 1px solid rgba(27,31,35,.2);\n    border-radius: 3px;\n    background-image: linear-gradient(-180deg,#fafbfc,#eff3f6 90%);\n    margin-left: 4px;\n    font-weight: 600;\n  }\n\n  .github-star-badge[_ngcontent-%COMP%]:hover {\n    background-image: linear-gradient(-180deg,#f0f3f6,#e6ebf1 90%);\n    border-color: rgba(27,31,35,.35);\n    background-position: -.5em;\n  }\n\n  .github-star-badge[_ngcontent-%COMP%]   .material-icons[_ngcontent-%COMP%] {\n    height: 16px;\n    width: 16px;\n    margin-right: 4px;\n  }\n\n  svg#clouds[_ngcontent-%COMP%] {\n    position: fixed;\n    bottom: -160px;\n    left: -230px;\n    z-index: -10;\n    width: 1920px;\n  }\n\n  \n\n  @media screen and (max-width: 767px) {\n    .card-container[_ngcontent-%COMP%]    > *[_ngcontent-%COMP%]:not(.circle-link), .terminal[_ngcontent-%COMP%] {\n      width: 100%;\n    }\n\n    .card[_ngcontent-%COMP%]:not(.highlight-card) {\n      height: 16px;\n      margin: 8px 0;\n    }\n\n    .card.highlight-card[_ngcontent-%COMP%]   span[_ngcontent-%COMP%] {\n      margin-left: 72px;\n    }\n\n    svg#rocket-smoke[_ngcontent-%COMP%] {\n      right: 120px;\n      transform: rotate(-5deg);\n    }\n  }\n\n  @media screen and (max-width: 575px) {\n    svg#rocket-smoke[_ngcontent-%COMP%] {\n      display: none;\n      visibility: hidden;\n    }\n  }"]
});


/***/ }),

/***/ 8629:
/*!*******************************!*\
  !*** ./src/app/app.module.ts ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AppModule: () => (/* binding */ AppModule)
/* harmony export */ });
/* harmony import */ var _angular_platform_browser__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/platform-browser */ 6480);
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/common/http */ 4860);
/* harmony import */ var _app_routing_module__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./app-routing.module */ 3966);
/* harmony import */ var _app_component__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./app.component */ 6401);
/* harmony import */ var _angular_platform_browser_animations__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/platform-browser/animations */ 4987);
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! @angular/forms */ 8849);
/* harmony import */ var _angular_material_input__WEBPACK_IMPORTED_MODULE_17__ = __webpack_require__(/*! @angular/material/input */ 26);
/* harmony import */ var _angular_material_select__WEBPACK_IMPORTED_MODULE_16__ = __webpack_require__(/*! @angular/material/select */ 6355);
/* harmony import */ var _angular_material_form_field__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! @angular/material/form-field */ 1333);
/* harmony import */ var _angular_material_dialog__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @angular/material/dialog */ 7401);
/* harmony import */ var _angular_material_button__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @angular/material/button */ 895);
/* harmony import */ var _angular_material_icon__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @angular/material/icon */ 6515);
/* harmony import */ var _angular_material_menu__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @angular/material/menu */ 8128);
/* harmony import */ var _angular_material_datepicker__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! @angular/material/datepicker */ 2226);
/* harmony import */ var _angular_material_core__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! @angular/material/core */ 5309);
/* harmony import */ var _angular_material_checkbox__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! @angular/material/checkbox */ 6658);
/* harmony import */ var _angular_material_list__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! @angular/material/list */ 3228);
/* harmony import */ var _angular_material_grid_list__WEBPACK_IMPORTED_MODULE_18__ = __webpack_require__(/*! @angular/material/grid-list */ 647);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ 1699);



















class AppModule {}
AppModule.ɵfac = function AppModule_Factory(t) {
  return new (t || AppModule)();
};
AppModule.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdefineNgModule"]({
  type: AppModule,
  bootstrap: [_app_component__WEBPACK_IMPORTED_MODULE_1__.AppComponent]
});
AppModule.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdefineInjector"]({
  imports: [_angular_platform_browser__WEBPACK_IMPORTED_MODULE_3__.BrowserModule, _app_routing_module__WEBPACK_IMPORTED_MODULE_0__.AppRoutingModule, _angular_common_http__WEBPACK_IMPORTED_MODULE_4__.HttpClientModule, _angular_platform_browser_animations__WEBPACK_IMPORTED_MODULE_5__.BrowserAnimationsModule, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_6__.MatDialogModule, _angular_material_button__WEBPACK_IMPORTED_MODULE_7__.MatButtonModule, _angular_material_icon__WEBPACK_IMPORTED_MODULE_8__.MatIconModule, _angular_material_menu__WEBPACK_IMPORTED_MODULE_9__.MatMenuModule, _angular_material_core__WEBPACK_IMPORTED_MODULE_10__.MatNativeDateModule, _angular_material_datepicker__WEBPACK_IMPORTED_MODULE_11__.MatDatepickerModule, _angular_material_checkbox__WEBPACK_IMPORTED_MODULE_12__.MatCheckboxModule, _angular_material_list__WEBPACK_IMPORTED_MODULE_13__.MatListModule, _angular_forms__WEBPACK_IMPORTED_MODULE_14__.FormsModule, _angular_forms__WEBPACK_IMPORTED_MODULE_14__.ReactiveFormsModule, _angular_material_form_field__WEBPACK_IMPORTED_MODULE_15__.MatFormFieldModule, _angular_material_select__WEBPACK_IMPORTED_MODULE_16__.MatSelectModule, _angular_material_input__WEBPACK_IMPORTED_MODULE_17__.MatInputModule, _angular_material_grid_list__WEBPACK_IMPORTED_MODULE_18__.MatGridListModule]
});

(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵsetNgModuleScope"](AppModule, {
    declarations: [_app_component__WEBPACK_IMPORTED_MODULE_1__.AppComponent],
    imports: [_angular_platform_browser__WEBPACK_IMPORTED_MODULE_3__.BrowserModule, _app_routing_module__WEBPACK_IMPORTED_MODULE_0__.AppRoutingModule, _angular_common_http__WEBPACK_IMPORTED_MODULE_4__.HttpClientModule, _angular_platform_browser_animations__WEBPACK_IMPORTED_MODULE_5__.BrowserAnimationsModule, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_6__.MatDialogModule, _angular_material_button__WEBPACK_IMPORTED_MODULE_7__.MatButtonModule, _angular_material_icon__WEBPACK_IMPORTED_MODULE_8__.MatIconModule, _angular_material_menu__WEBPACK_IMPORTED_MODULE_9__.MatMenuModule, _angular_material_core__WEBPACK_IMPORTED_MODULE_10__.MatNativeDateModule, _angular_material_datepicker__WEBPACK_IMPORTED_MODULE_11__.MatDatepickerModule, _angular_material_checkbox__WEBPACK_IMPORTED_MODULE_12__.MatCheckboxModule, _angular_material_list__WEBPACK_IMPORTED_MODULE_13__.MatListModule, _angular_forms__WEBPACK_IMPORTED_MODULE_14__.FormsModule, _angular_forms__WEBPACK_IMPORTED_MODULE_14__.ReactiveFormsModule, _angular_material_form_field__WEBPACK_IMPORTED_MODULE_15__.MatFormFieldModule, _angular_material_select__WEBPACK_IMPORTED_MODULE_16__.MatSelectModule, _angular_material_input__WEBPACK_IMPORTED_MODULE_17__.MatInputModule, _angular_material_grid_list__WEBPACK_IMPORTED_MODULE_18__.MatGridListModule]
  });
})();

/***/ }),

/***/ 707:
/*!**************************************!*\
  !*** ./src/app/lightning.service.ts ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   LightningService: () => (/* binding */ LightningService)
/* harmony export */ });
/* harmony import */ var C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ 1670);
/* harmony import */ var rxjs__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! rxjs */ 2513);
/* harmony import */ var rxjs_operators__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! rxjs/operators */ 3738);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/core */ 1699);
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/common/http */ 4860);





class LightningService {
  constructor(http) {
    var _this = this;
    this.http = http;
    // TODO:  Fix this so it's not hardcoded to our local dev environment
    this.apiUrl = 'https://willdev.net/api'; // URL to web api - in quotes - no trailing slash:  'http://54.176.48.9'
    this.authChallengeResponse = '';
    this.weblnButtonUrl = '';
    this.emailaddress = '';
    this.auth_token = '';
    this.signinActive = false;
    this.signinEmailValidation = false;
    this.showEmailPopUp = new rxjs__WEBPACK_IMPORTED_MODULE_1__.Subject();
    this.showEmailValidationPopUp = new rxjs__WEBPACK_IMPORTED_MODULE_1__.Subject();
    this.signInComplete = false;
    this.showCloseDialog = new rxjs__WEBPACK_IMPORTED_MODULE_1__.Subject();
    // keep track of fake pubkey in the case of a non-lighting login
    this.fake_pub_key = "";
    this.user = {
      id: 0,
      title: 'Service Test User',
      address: '',
      emailvalidated: false,
      travel_request_active: false,
      member: false
    };
    this.sub_user = new rxjs__WEBPACK_IMPORTED_MODULE_1__.Subject();
    this.login_user = new rxjs__WEBPACK_IMPORTED_MODULE_1__.Subject();
    this.pollSignedIn = /*#__PURE__*/(0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      const response = yield fetch(_this.apiUrl + '/me?bech_32_url=' + _this.authChallengeResponse);
      const result = yield response.json();
      console.log(result);
      console.log(result.user);
      if (result.auth_token) {
        console.log('found auth_token');
        // User can still be none here.  Check first.
        if (result.user) {
          console.log('found user');
          _this.user = result.user;
          _this.update_user(result.user['title'], result.user['address']);
        }
        _this.auth_token = result.auth_token;
        localStorage.setItem('token', result.auth_token);
        //localStorage.setItem('user', JSON.stringify(result.user));
        _this.signinActive = false;
        if (result.do_email_validation) {
          console.log('do email validation');
          _this.showEmailPopUp.next(true);
        } else {
          console.log('no email validation - close dialog');
          _this.showCloseDialog.next(true);
          _this.getUserData();
        }
      }
      return result.user != null;
    });
    this.checkSignedIn = /*#__PURE__*/(0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      const result = yield _this.pollSignedIn();
      console.log(result);
      if (!result) {
        _this.startPolling();
      } else {
        console.log('login success');
        // window.location.reload();
        _this.signInComplete = true;
      }
    });
    this.getUserData = /*#__PURE__*/(0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      const response = yield fetch(_this.apiUrl + '/users/data', {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      const result = yield response.json();
      console.log(result);
      console.log(result.user);
      if (result.user) {
        console.log('found user');
        _this.user = result.user;
        _this.sub_user.next(true);
      } else {
        _this.login_user.next(true);
      }
      if (result.role) {
        console.log('found role');
        console.log(result.role);
        //this.role = result.role;
        // add the role to localstorage
        //localStorage.setItem('role', JSON.stringify(result.role));
      }

      return {
        User: _this.user
      };
    });
  }
  /** GET login challenge from the server */
  // this is just a lnurl string
  loginChallenge() {
    console.log('Lightning Service Login Challenge');
    const auth_url = `${this.apiUrl}/auth`;
    return this.http.get(auth_url).pipe((0,rxjs_operators__WEBPACK_IMPORTED_MODULE_2__.tap)(
    // Log the result or error
    {
      //next: (data) => this.log(data['lnurl']), // this works
      //next: (data) => this.authChallengeResponse = data['lnurl'], // this too
      next: data => this.registerACR(data['lnurl']),
      error: error => this.log('error')
    }));
  }
  registerACR(aCR) {
    console.log('register ACR');
    console.log(aCR);
    this.authChallengeResponse = aCR;
    this.signinActive = true;
    this.startPolling();
  }
  getLnUrl() {
    console.log('Lightning Service Get lnUrl');
    return this.authChallengeResponse;
  }
  startPolling() {
    if (!this.signinActive) {
      return;
    }
    window.setTimeout(this.checkSignedIn, 1000);
  }
  startEmailValidation(emailaddress) {
    var _this2 = this;
    return (0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      console.log('lightning.service startEmailValidation');
      _this2.emailaddress = emailaddress;
      const response = yield fetch(_this2.apiUrl + '/user/email/' + emailaddress + '/start', {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${_this2.auth_token}`
        }
      });
      _this2.showEmailValidationPopUp.next(true);
      const result = yield response.json();
    })();
  }
  validateEmail(emailaddress, verificationcode) {
    var _this3 = this;
    return (0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      console.log('lightning.service startEmailValidation');
      _this3.emailaddress = emailaddress;
      const response = yield fetch(_this3.apiUrl + '/user/email/' + emailaddress + '/validate/' + verificationcode, {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${_this3.auth_token}`
        }
      });
      _this3.showEmailValidationPopUp.next(true);
      const result = yield response.json();
      if (result['success'] == true) {
        console.log('success true');
        // get user data again.
        _this3.getUserData();
        _this3.signinActive = false;
        _this3.showCloseDialog.next(true);
      }
    })();
  }
  startEmailValidationNoLightning(emailaddress) {
    var _this4 = this;
    return (0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      console.log('lightning.service startEmailValidation without lightning');
      _this4.emailaddress = emailaddress;
      const response = yield fetch(_this4.apiUrl + '/user/email/' + emailaddress + '/start-no-lightning');
      _this4.showEmailValidationPopUp.next(true);
      const result = yield response.json();
      _this4.fake_pub_key = result['publickey'];
    })();
  }
  validateEmailNoLightning(emailaddress, verificationcode) {
    var _this5 = this;
    return (0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      console.log('lightning.service startEmailValidation without lightning');
      _this5.emailaddress = emailaddress;
      const response = yield fetch(_this5.apiUrl + '/user/email/' + emailaddress + '/validate-no-lightning/' + verificationcode + "/" + _this5.fake_pub_key);
      _this5.showEmailValidationPopUp.next(true);
      const result = yield response.json();
      if (result['success'] == true) {
        console.log('success true');
        // save the JWT token here.
        _this5.auth_token = result.auth_token;
        localStorage.setItem('token', result.auth_token);
        _this5.signinActive = false;
        _this5.showCloseDialog.next(true);
      }
    })();
  }
  update_user(title, address) {
    console.log('lightning service update user');
    this.user['address'] = address;
    this.user['title'] = title;
    this.sub_user.next(true);
  }
  doLogout() {}
  requestLogin() {
    this.login_user.next(true);
  }
  /** Log */
  log(message) {
    console.log(message);
    //this.messageService.add(`HeroService: ${message}`);
  }
}

LightningService.ɵfac = function LightningService_Factory(t) {
  return new (t || LightningService)(_angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵinject"](_angular_common_http__WEBPACK_IMPORTED_MODULE_4__.HttpClient));
};
LightningService.ɵprov = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵdefineInjectable"]({
  token: LightningService,
  factory: LightningService.ɵfac,
  providedIn: 'root'
});


/***/ }),

/***/ 3274:
/*!********************************************************!*\
  !*** ./src/app/login-dialog/login-dialog.component.ts ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   LoginDialogComponent: () => (/* binding */ LoginDialogComponent)
/* harmony export */ });
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common */ 6575);
/* harmony import */ var _angular_material_dialog__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/material/dialog */ 7401);
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/forms */ 8849);
/* harmony import */ var _angular_material_button__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/material/button */ 895);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/core */ 1699);
/* harmony import */ var _lightning_service__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../lightning.service */ 707);
//import { BrowserModule } from '@angular/platform-browser';


//import { FormControl } from '@angular/forms';








function LoginDialogComponent_div_2_div_1_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div")(1, "p")(2, "a", 5);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](3, "Connect to browser");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](4, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](5, "If the link above does not work for you, please install the ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](6, "a", 6);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](7, "getalby web extension.");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](8, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](9, "Or, scan a QR code using ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](10, "a", 7);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](11, "your favorite lightning wallet");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](12, " that supports lnurl-auth ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const ctx_r6 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵattribute"]("href", ctx_r6.weblnurl, _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵsanitizeUrl"]);
  }
}
function LoginDialogComponent_div_2_div_2_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Login with a QR code. ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](2, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](3, " Scan this QR code with ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](4, "a", 7);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](5, "your favorite lightning wallet");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](6, " that supports lnurl-auth");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](7, ". ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](8, "a", 8);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelement"](9, "img", 9);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const ctx_r7 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](9);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("src", ctx_r7.qrcodesrc, _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵsanitizeUrl"]);
  }
}
function LoginDialogComponent_div_2_div_3_Template(rf, ctx) {
  if (rf & 1) {
    const _r10 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Login with an email address. ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](2, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](3, " Enter your email address to recieve a temporary login code");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](4, ". ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](5, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](6, " This login functionality is provided as a temporary convenience, and will no longer be available once lnurl-auth is working on iphone/safari. Please use lightning.");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](7, " Email address: ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](8, "input", 10);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("ngModelChange", function LoginDialogComponent_div_2_div_3_Template_input_ngModelChange_8_listener($event) {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r10);
      const ctx_r9 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r9.emailaddress = $event);
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](9, "button", 11);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_2_div_3_Template_button_click_9_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r10);
      const ctx_r11 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r11.submitEmailNoLightning());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](10, "Submit Email");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const ctx_r8 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](8);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngModel", ctx_r8.emailaddress);
  }
}
function LoginDialogComponent_div_2_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 3);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](1, LoginDialogComponent_div_2_div_1_Template, 13, 1, "div", 4);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](2, LoginDialogComponent_div_2_div_2_Template, 10, 1, "div", 4);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](3, LoginDialogComponent_div_2_div_3_Template, 11, 1, "div", 4);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx_r0.loginmodebrowser);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx_r0.loginmodeQR);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx_r0.loginmodeEmail);
  }
}
function LoginDialogComponent_div_3_Template(rf, ctx) {
  if (rf & 1) {
    const _r13 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 3)(1, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](2, "You are logged in with lightning. ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](3, "h1", 0);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](4, "Required: Validate email");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](5, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](6, "We require your email address so we can email you with updates.");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](7, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](8, "We will never sell your email address, or give it away to anyone.");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](9, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](10, " Email address: ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](11, "input", 10);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("ngModelChange", function LoginDialogComponent_div_3_Template_input_ngModelChange_11_listener($event) {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r13);
      const ctx_r12 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r12.emailaddress = $event);
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](12, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](13);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const ctx_r1 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](11);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngModel", ctx_r1.emailaddress);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtextInterpolate1"](" ", ctx_r1.emailaddress, "");
  }
}
function LoginDialogComponent_div_4_Template(rf, ctx) {
  if (rf & 1) {
    const _r15 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 3)(1, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](2, "Please check your email for the 6 digit security code ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](3, "h1", 0);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](4, "Required: Validate email");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](5, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](6, " VerificationCode: ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](7, "input", 12);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("ngModelChange", function LoginDialogComponent_div_4_Template_input_ngModelChange_7_listener($event) {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r15);
      const ctx_r14 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r14.emailaddressverificationcode = $event);
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](8, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](9);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const ctx_r2 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](7);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngModel", ctx_r2.emailaddressverificationcode);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtextInterpolate1"](" ", ctx_r2.emailaddressverificationcode, "");
  }
}
function LoginDialogComponent_div_5_button_2_Template(rf, ctx) {
  if (rf & 1) {
    const _r20 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "button", 11);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_5_button_2_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r20);
      const ctx_r19 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r19.changeLoginMode("browser"));
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Login with browser");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
}
function LoginDialogComponent_div_5_button_3_Template(rf, ctx) {
  if (rf & 1) {
    const _r22 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "button", 18);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_5_button_3_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r22);
      const ctx_r21 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r21.changeLoginMode("qrcode"));
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Login with QR code");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
}
function LoginDialogComponent_div_5_button_4_Template(rf, ctx) {
  if (rf & 1) {
    const _r24 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "button", 18);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_5_button_4_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r24);
      const ctx_r23 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r23.changeLoginMode("email"));
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Login with Email");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
}
function LoginDialogComponent_div_5_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 13)(1, "div", 14);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](2, LoginDialogComponent_div_5_button_2_Template, 2, 0, "button", 15);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](3, LoginDialogComponent_div_5_button_3_Template, 2, 0, "button", 16);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](4, LoginDialogComponent_div_5_button_4_Template, 2, 0, "button", 16);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](5, "button", 17);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](6, "Close");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()()();
  }
  if (rf & 2) {
    const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", !ctx_r3.loginmodebrowser);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", !ctx_r3.loginmodeQR);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", !ctx_r3.loginmodeEmail);
  }
}
function LoginDialogComponent_div_6_Template(rf, ctx) {
  if (rf & 1) {
    const _r26 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 3)(1, "div", 14)(2, "button", 11);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_6_Template_button_click_2_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r26);
      const ctx_r25 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r25.submitEmail());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](3, "Submit Email");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](4, "button", 17);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](5, "Close");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()()();
  }
}
function LoginDialogComponent_div_7_button_2_Template(rf, ctx) {
  if (rf & 1) {
    const _r30 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "button", 11);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_7_button_2_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r30);
      const ctx_r29 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r29.validateEmail());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Verify Email");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
}
function LoginDialogComponent_div_7_button_3_Template(rf, ctx) {
  if (rf & 1) {
    const _r32 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "button", 11);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_7_button_3_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r32);
      const ctx_r31 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r31.validateEmailNoLightning());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Verify Email NL");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
}
function LoginDialogComponent_div_7_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 3)(1, "div", 14);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](2, LoginDialogComponent_div_7_button_2_Template, 2, 0, "button", 15);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](3, LoginDialogComponent_div_7_button_3_Template, 2, 0, "button", 15);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](4, "button", 17);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](5, "Close");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()()();
  }
  if (rf & 2) {
    const ctx_r5 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", !ctx_r5.loginmodeEmail);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx_r5.loginmodeEmail);
  }
}
class LoginDialogComponent {
  constructor(data, lightningService) {
    this.data = data;
    this.lightningService = lightningService;
    //qrcodesrc = this.lightningService.getLnUrl();
    this.qrcodesrc = 'http://54.219.218.253/api/generate_qr/' + this.lightningService.getLnUrl();
    this.weblnurl = 'lightning:' + this.lightningService.getLnUrl();
    // Multi-stage dialog
    // Stage1 = lightninglogin
    this.signinLightning = true;
    this.loginmodebrowser = true;
    this.loginmodeQR = false;
    this.loginmodeEmail = false;
    // Stage 2 - email address entry
    this.signinEmailValidationStart = false;
    this.signinEmailValidation = false;
    this.emailaddress = '';
    // Stage 3 - Email validation
    this.signinEmailValidationCodeStart = false;
    this.emailaddressverificationcode = '';
  }
  ngOnInit() {
    // subscribe to the user in lightning service for changes 
    this.lightningService.showEmailPopUp.subscribe(value => {
      console.log('show email popup');
      this.signinEmailValidationStart = true;
      this.signinLightning = false;
    });
    // subscribe to the user in lightning service for changes
    this.lightningService.showEmailValidationPopUp.subscribe(value => {
      console.log('show Email Validation popup');
      this.signinEmailValidationCodeStart = true;
      this.signinEmailValidationStart = false;
    });
  }
  changeLoginMode(loginMode) {
    if (loginMode == "browser") {
      this.loginmodebrowser = true;
      this.loginmodeQR = false;
      this.loginmodeEmail = false;
    } else if (loginMode == "qrcode") {
      this.loginmodebrowser = false;
      this.loginmodeQR = true;
      this.loginmodeEmail = false;
    } else {
      this.loginmodebrowser = false;
      this.loginmodeQR = false;
      this.loginmodeEmail = true;
    }
  }
  submitEmail() {
    console.log(this.emailaddress);
    this.lightningService.startEmailValidation(this.emailaddress);
  }
  validateEmail() {
    console.log(this.emailaddress);
    console.log(this.emailaddressverificationcode);
    this.lightningService.validateEmail(this.emailaddress, this.emailaddressverificationcode);
  }
  submitEmailNoLightning() {
    console.log(this.emailaddress);
    this.lightningService.startEmailValidationNoLightning(this.emailaddress);
    // Turn off the mode selection buttons
    this.signinLightning = false;
  }
  validateEmailNoLightning() {
    console.log(this.emailaddress);
    console.log(this.emailaddressverificationcode);
    this.lightningService.validateEmailNoLightning(this.emailaddress, this.emailaddressverificationcode);
  }
}
LoginDialogComponent.ɵfac = function LoginDialogComponent_Factory(t) {
  return new (t || LoginDialogComponent)(_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdirectiveInject"](_angular_material_dialog__WEBPACK_IMPORTED_MODULE_2__.MAT_DIALOG_DATA), _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdirectiveInject"](_lightning_service__WEBPACK_IMPORTED_MODULE_0__.LightningService));
};
LoginDialogComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵdefineComponent"]({
  type: LoginDialogComponent,
  selectors: [["app-login-dialog"]],
  standalone: true,
  features: [_angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵStandaloneFeature"]],
  decls: 8,
  vars: 6,
  consts: [["mat-dialog-title", ""], ["mat-dialog-content", "", 4, "ngIf"], ["mat-dialog-actions", "", 4, "ngIf"], ["mat-dialog-content", ""], [4, "ngIf"], [1, "webln-button", "d-none", "btn", "btn-primary", "mx-auto"], ["href", "https://getalby.com"], ["href", "https://coincharge.io/en/lnurl-for-lightning-wallets/"], ["href", "", 1, "qr-link"], ["id", "qr_image", 1, "qr", 3, "src"], ["type", "email", "email", "", 3, "ngModel", "ngModelChange"], ["mat-raised-button", "", "color", "primary", 3, "click"], ["type", "text", 3, "ngModel", "ngModelChange"], ["mat-dialog-actions", ""], [1, "login-button-row"], ["mat-raised-button", "", "color", "primary", 3, "click", 4, "ngIf"], ["mat-raised-button", "", "color", "accent", 3, "click", 4, "ngIf"], ["mat-raised-button", "", "color", "warn", "mat-dialog-close", ""], ["mat-raised-button", "", "color", "accent", 3, "click"]],
  template: function LoginDialogComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "h1", 0);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Login to unlockd");
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](2, LoginDialogComponent_div_2_Template, 4, 3, "div", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](3, LoginDialogComponent_div_3_Template, 14, 2, "div", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](4, LoginDialogComponent_div_4_Template, 10, 2, "div", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](5, LoginDialogComponent_div_5_Template, 7, 3, "div", 2);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](6, LoginDialogComponent_div_6_Template, 6, 0, "div", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](7, LoginDialogComponent_div_7_Template, 6, 2, "div", 1);
    }
    if (rf & 2) {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](2);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx.signinLightning);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx.signinEmailValidationStart);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx.signinEmailValidationCodeStart);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx.signinLightning);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx.signinEmailValidationStart);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx.signinEmailValidationCodeStart);
    }
  },
  dependencies: [_angular_common__WEBPACK_IMPORTED_MODULE_3__.CommonModule, _angular_common__WEBPACK_IMPORTED_MODULE_3__.NgIf, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_2__.MatDialogModule, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_2__.MatDialogClose, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_2__.MatDialogTitle, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_2__.MatDialogContent, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_2__.MatDialogActions, _angular_material_button__WEBPACK_IMPORTED_MODULE_4__.MatButtonModule, _angular_material_button__WEBPACK_IMPORTED_MODULE_4__.MatButton, _angular_forms__WEBPACK_IMPORTED_MODULE_5__.FormsModule, _angular_forms__WEBPACK_IMPORTED_MODULE_5__.DefaultValueAccessor, _angular_forms__WEBPACK_IMPORTED_MODULE_5__.NgControlStatus, _angular_forms__WEBPACK_IMPORTED_MODULE_5__.EmailValidator, _angular_forms__WEBPACK_IMPORTED_MODULE_5__.NgModel, _angular_forms__WEBPACK_IMPORTED_MODULE_5__.ReactiveFormsModule],
  encapsulation: 2
});


/***/ }),

/***/ 4913:
/*!*********************!*\
  !*** ./src/main.ts ***!
  \*********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _angular_platform_browser__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/platform-browser */ 6480);
/* harmony import */ var _app_app_module__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./app/app.module */ 8629);


_angular_platform_browser__WEBPACK_IMPORTED_MODULE_1__.platformBrowser().bootstrapModule(_app_app_module__WEBPACK_IMPORTED_MODULE_0__.AppModule).catch(err => console.error(err));

/***/ })

},
/******/ __webpack_require__ => { // webpackRuntimeModules
/******/ var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
/******/ __webpack_require__.O(0, ["vendor"], () => (__webpack_exec__(4913)));
/******/ var __webpack_exports__ = __webpack_require__.O();
/******/ }
]);
//# sourceMappingURL=main.js.map