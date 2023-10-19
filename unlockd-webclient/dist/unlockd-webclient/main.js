"use strict";
(self["webpackChunkunlockd_webclient"] = self["webpackChunkunlockd_webclient"] || []).push([["main"],{

/***/ 4702:
/*!************************************************************!*\
  !*** ./src/app/admin/user-detail/user-detail.component.ts ***!
  \************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   UserDetailComponent: () => (/* binding */ UserDetailComponent)
/* harmony export */ });
/* harmony import */ var C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ 1670);
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/forms */ 8849);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/core */ 1699);
/* harmony import */ var _lightning_service__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../lightning.service */ 707);
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/router */ 7947);
/* harmony import */ var _angular_material_button__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/material/button */ 895);
/* harmony import */ var _angular_material_checkbox__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @angular/material/checkbox */ 6658);
/* harmony import */ var _angular_material_form_field__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @angular/material/form-field */ 1333);
/* harmony import */ var _angular_material_input__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @angular/material/input */ 26);










class UserDetailComponent {
  constructor(lightningService, route, router) {
    var _this = this;
    this.lightningService = lightningService;
    this.route = route;
    this.router = router;
    this.userid = "";
    this.user = {};
    this.getUserData = /*#__PURE__*/(0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      if (localStorage.getItem("token") === null) {
        console.log('user data - no access token');
      } else {
        const response = yield fetch(_this.lightningService.apiUrl + '/admin/users/' + _this.userid, {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem("token")}`
          }
        });
        const result = yield response.json();
        console.log(result);
        console.log(result.user);
        if (result.status == "401") {
          _this.lightningService.requestLogin();
        }
        if (result.user) {
          console.log('found user');
          console.log(result.user['title']);
          console.log(result.user['description']);
          _this.developer.setValue(result.user['developer']);
          _this.user = result.user;
          _this.title.setValue(result.user['title']);
          _this.emailaddress.setValue(result.user['emailaddress']);
        }
      }
    });
    this.title = new _angular_forms__WEBPACK_IMPORTED_MODULE_2__.FormControl('');
    this.emailaddress = new _angular_forms__WEBPACK_IMPORTED_MODULE_2__.FormControl('');
    this.developer = new _angular_forms__WEBPACK_IMPORTED_MODULE_2__.FormControl('');
    this.updateUser = /*#__PURE__*/(0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      console.log('update user');
      console.log(localStorage.getItem("token"));
      //const location = window.location.hostname; // this works for live
      //const location = '13.56.127.211' // hardcoding for now
      const settings = {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
          '_id': _this.userid,
          'title': _this.title.value,
          'emailaddress': _this.emailaddress.value,
          'developer': _this.developer.value
        })
      };
      //try {
      const fetchResponse = yield fetch(_this.lightningService.apiUrl + '/admin/users/' + _this.userid + '/update', settings);
      console.log(fetchResponse);
      const data = yield fetchResponse.json();
      // we dont have to do anything special here.  redirect?
      _this.router.navigate(['admin-users']);
      console.log(data);
      return data;
      //} catch (e) {
      //    return e;
      //} 
    });

    this.deleteUser = /*#__PURE__*/(0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      console.log('delete user');
      console.log(localStorage.getItem("token"));
      //const location = window.location.hostname; // this works for live
      //const location = '13.56.127.211' // hardcoding for now
      const settings = {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
          '_id': _this.userid
        })
      };
      //try {
      const fetchResponse = yield fetch(_this.lightningService.apiUrl + '/admin/users/' + _this.userid + '/delete', settings);
      console.log(fetchResponse);
      const data = yield fetchResponse.json();
      // we dont have to do anything special here.  redirect?
      _this.router.navigate(['admin-users']);
      console.log(data);
      return data;
      //} catch (e) {
      //    return e;
      //} 
    });
  }
  // load the role into the form 
  ngOnInit() {
    console.log('user detail init');
    this.route.paramMap.subscribe(params => {
      console.log('user data params changed');
      this.userid = params.get('userid') || "";
      //this.role = this.productService.getProduct(this.id);
      this.getUserData();
    });
  }
}
UserDetailComponent.ɵfac = function UserDetailComponent_Factory(t) {
  return new (t || UserDetailComponent)(_angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵdirectiveInject"](_lightning_service__WEBPACK_IMPORTED_MODULE_1__.LightningService), _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵdirectiveInject"](_angular_router__WEBPACK_IMPORTED_MODULE_4__.ActivatedRoute), _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵdirectiveInject"](_angular_router__WEBPACK_IMPORTED_MODULE_4__.Router));
};
UserDetailComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵdefineComponent"]({
  type: UserDetailComponent,
  selectors: [["app-user-detail"]],
  decls: 17,
  vars: 3,
  consts: [["roleUpdateeForm", "ngForm"], [1, "example-full-width"], ["for", "title"], ["matInput", "", "id", "title", "type", "text", 3, "formControl"], ["for", "emailaddress"], ["matInput", "", "id", "emailaddress", "type", "text", 3, "formControl"], [3, "formControl"], ["mat-raised-button", "", "color", "primary", "type", "button", 3, "click"], ["mat-raised-button", "", "color", "warn", "type", "button", 3, "click"]],
  template: function UserDetailComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](0, "form", null, 0)(2, "mat-form-field", 1)(3, "mat-label", 2);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtext"](4, "Name ");
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelement"](5, "input", 3);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](6, "mat-form-field", 1)(7, "mat-label", 4);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtext"](8, "email address ");
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelement"](9, "input", 5);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](10, "p")(11, "mat-checkbox", 6);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtext"](12, "developer");
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](13, "button", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵlistener"]("click", function UserDetailComponent_Template_button_click_13_listener() {
        return ctx.updateUser();
      });
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtext"](14, "Update");
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementStart"](15, "button", 8);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵlistener"]("click", function UserDetailComponent_Template_button_click_15_listener() {
        return ctx.deleteUser();
      });
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵtext"](16, "Delete");
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵelementEnd"]();
    }
    if (rf & 2) {
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"](5);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("formControl", ctx.title);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"](4);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("formControl", ctx.emailaddress);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵadvance"](2);
      _angular_core__WEBPACK_IMPORTED_MODULE_3__["ɵɵproperty"]("formControl", ctx.developer);
    }
  },
  dependencies: [_angular_material_button__WEBPACK_IMPORTED_MODULE_5__.MatButton, _angular_material_checkbox__WEBPACK_IMPORTED_MODULE_6__.MatCheckbox, _angular_forms__WEBPACK_IMPORTED_MODULE_2__["ɵNgNoValidate"], _angular_forms__WEBPACK_IMPORTED_MODULE_2__.DefaultValueAccessor, _angular_forms__WEBPACK_IMPORTED_MODULE_2__.NgControlStatus, _angular_forms__WEBPACK_IMPORTED_MODULE_2__.NgControlStatusGroup, _angular_forms__WEBPACK_IMPORTED_MODULE_2__.NgForm, _angular_forms__WEBPACK_IMPORTED_MODULE_2__.FormControlDirective, _angular_material_form_field__WEBPACK_IMPORTED_MODULE_7__.MatFormField, _angular_material_form_field__WEBPACK_IMPORTED_MODULE_7__.MatLabel, _angular_material_input__WEBPACK_IMPORTED_MODULE_8__.MatInput],
  styles: ["/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsInNvdXJjZVJvb3QiOiIifQ== */"]
});


/***/ }),

/***/ 9909:
/*!************************************************!*\
  !*** ./src/app/admin/users/users.component.ts ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   UsersComponent: () => (/* binding */ UsersComponent)
/* harmony export */ });
/* harmony import */ var C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ 1670);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ 1699);
/* harmony import */ var _lightning_service__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../lightning.service */ 707);
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/common */ 6575);
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/router */ 7947);





function UsersComponent_tr_7_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "tr")(1, "td")(2, "a", 1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()();
  }
  if (rf & 2) {
    const site_user_r1 = ctx.$implicit;
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵpropertyInterpolate1"]("routerLink", "/admin/users/", site_user_r1["_id"], "");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate1"](" ", site_user_r1["title"], " ");
  }
}
class UsersComponent {
  constructor(lightningService) {
    var _this = this;
    this.lightningService = lightningService;
    this.user_list = [];
    this.getUserData = /*#__PURE__*/(0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      const response = yield fetch(_this.lightningService.apiUrl + '/users/', {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem("token")}`
        }
      });
      const result = yield response.json();
      console.log(result);
      _this.user_list = result;
    });
  }
  ngOnInit() {
    console.log('admin users init');
    //this.title.setValue(this.lightningService.user['title']);
    this.getUserData();
  }
}
UsersComponent.ɵfac = function UsersComponent_Factory(t) {
  return new (t || UsersComponent)(_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdirectiveInject"](_lightning_service__WEBPACK_IMPORTED_MODULE_1__.LightningService));
};
UsersComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵdefineComponent"]({
  type: UsersComponent,
  selectors: [["app-users"]],
  decls: 8,
  vars: 1,
  consts: [[4, "ngFor", "ngForOf"], [3, "routerLink"]],
  template: function UsersComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](1, "users works!");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](2, "table")(3, "thead")(4, "th");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](5, "Name");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](6, "tbody");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](7, UsersComponent_tr_7_Template, 4, 2, "tr", 0);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    }
    if (rf & 2) {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](7);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngForOf", ctx.user_list);
    }
  },
  dependencies: [_angular_common__WEBPACK_IMPORTED_MODULE_3__.NgForOf, _angular_router__WEBPACK_IMPORTED_MODULE_4__.RouterLink],
  styles: ["/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsInNvdXJjZVJvb3QiOiIifQ== */"]
});


/***/ }),

/***/ 3966:
/*!***************************************!*\
  !*** ./src/app/app-routing.module.ts ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   AppRoutingModule: () => (/* binding */ AppRoutingModule)
/* harmony export */ });
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @angular/router */ 7947);
/* harmony import */ var _homepage_homepage_component__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./homepage/homepage.component */ 6905);
/* harmony import */ var _costs_costs_component__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./costs/costs.component */ 4208);
/* harmony import */ var _faq_faq_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./faq/faq.component */ 8970);
/* harmony import */ var _profile_profile_component__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./profile/profile.component */ 5229);
/* harmony import */ var _transactions_transactions_component__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./transactions/transactions.component */ 3186);
/* harmony import */ var _admin_users_users_component__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./admin/users/users.component */ 9909);
/* harmony import */ var _admin_user_detail_user_detail_component__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./admin/user-detail/user-detail.component */ 4702);
/* harmony import */ var _developer_games_games_component__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./developer/games/games.component */ 7820);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @angular/core */ 1699);











const routes = [{
  path: '',
  component: _homepage_homepage_component__WEBPACK_IMPORTED_MODULE_0__.HomepageComponent
}, {
  path: 'profile',
  component: _profile_profile_component__WEBPACK_IMPORTED_MODULE_3__.ProfileComponent
}, {
  path: 'costs',
  component: _costs_costs_component__WEBPACK_IMPORTED_MODULE_1__.CostsComponent
}, {
  path: 'faq',
  component: _faq_faq_component__WEBPACK_IMPORTED_MODULE_2__.FaqComponent
}, {
  path: 'transactions',
  component: _transactions_transactions_component__WEBPACK_IMPORTED_MODULE_4__.TransactionsComponent
}, {
  path: 'admin/users',
  component: _admin_users_users_component__WEBPACK_IMPORTED_MODULE_5__.UsersComponent
}, {
  path: 'admin/users/:userid',
  component: _admin_user_detail_user_detail_component__WEBPACK_IMPORTED_MODULE_6__.UserDetailComponent
}, {
  path: 'developer/games',
  component: _developer_games_games_component__WEBPACK_IMPORTED_MODULE_7__.GamesComponent
}];
class AppRoutingModule {}
AppRoutingModule.ɵfac = function AppRoutingModule_Factory(t) {
  return new (t || AppRoutingModule)();
};
AppRoutingModule.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_8__["ɵɵdefineNgModule"]({
  type: AppRoutingModule
});
AppRoutingModule.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_8__["ɵɵdefineInjector"]({
  imports: [_angular_router__WEBPACK_IMPORTED_MODULE_9__.RouterModule.forRoot(routes), _angular_router__WEBPACK_IMPORTED_MODULE_9__.RouterModule]
});

(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_8__["ɵɵsetNgModuleScope"](AppRoutingModule, {
    imports: [_angular_router__WEBPACK_IMPORTED_MODULE_9__.RouterModule],
    exports: [_angular_router__WEBPACK_IMPORTED_MODULE_9__.RouterModule]
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
/* harmony import */ var _app_login_dialog_login_dialog_component__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../app/login-dialog/login-dialog.component */ 5892);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/core */ 1699);
/* harmony import */ var _app_lightning_service__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../app/lightning.service */ 707);
/* harmony import */ var _angular_material_dialog__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/material/dialog */ 7401);
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/router */ 7947);
/* harmony import */ var _angular_common__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/common */ 6575);
/* harmony import */ var _angular_material_button__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @angular/material/button */ 895);
/* harmony import */ var _angular_material_icon__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @angular/material/icon */ 6515);
/* harmony import */ var _angular_material_menu__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @angular/material/menu */ 8128);









function AppComponent_span_18_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](1, "Welcome, ");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](2, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const ctx_r1 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](3);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtextInterpolate1"](" ", ctx_r1.userTitle, " ");
  }
}
function AppComponent_span_19_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "span")(1, "span")(2, "button", 10)(3, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](4, "admin_panel_settings");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](5, "mat-menu", null, 11)(7, "button", 12)(8, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](9, "cast for education");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](10, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](11, "Games");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](12, "button", 13)(13, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](14, "group");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](15, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](16, "Users");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](17, "button", 14)(18, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](19, "event_list");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](20, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](21, "Blog");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()()();
  }
  if (rf & 2) {
    const _r6 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵreference"](6);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("matMenuTriggerFor", _r6);
  }
}
function AppComponent_span_20_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "span")(1, "span")(2, "button", 10)(3, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](4, "developer_mode");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](5, "mat-menu", null, 15)(7, "button", 12)(8, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](9, "gamepad");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](10, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](11, "Games");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](12, "button", 13)(13, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](14, "group");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](15, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](16, "Users");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](17, "button", 14)(18, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](19, "event_list");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](20, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](21, "Blog");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()()()();
  }
  if (rf & 2) {
    const _r7 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵreference"](6);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("matMenuTriggerFor", _r7);
  }
}
function AppComponent_span_21_button_25_Template(rf, ctx) {
  if (rf & 1) {
    const _r11 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "button", 21);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function AppComponent_span_21_button_25_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r11);
      const ctx_r10 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r10.logout());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](1, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](2, "logout");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](3, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](4, "logout");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
  }
}
function AppComponent_span_21_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "span")(1, "button", 10)(2, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](3, "more_vert");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](4, "mat-menu", null, 16)(6, "button", 17)(7, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](8, "person");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](9, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](10, "profile");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](11, "button", 18)(12, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](13, "list");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](14, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](15, "transactions");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](16, "button", 19)(17, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](18, "checklist");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](19, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](20, "badges");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](21, "button", 19);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](22, "mat-icon");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](23, "span");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](24, "redeem voucher");
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](25, AppComponent_span_21_button_25_Template, 5, 0, "button", 20);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
  }
  if (rf & 2) {
    const _r8 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵreference"](5);
    const ctx_r4 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("matMenuTriggerFor", _r8);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](24);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx_r4.logoutButtonVisible);
  }
}
function AppComponent_button_22_Template(rf, ctx) {
  if (rf & 1) {
    const _r13 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "button", 22);
    _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵlistener"]("click", function AppComponent_button_22_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵrestoreView"](_r13);
      const ctx_r12 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵresetView"](ctx_r12.loginChallenge());
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
    this.user = this.lightningService.user;
    this.admin = false;
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
    if (localStorage.getItem("admin") === null) {
      console.log('admin not found in localstorage');
    } else {
      var admin_str = localStorage.getItem("admin") || "";
      if (admin_str == 'true') {
        this.admin = true;
      } else {
        this.admin = false;
      }
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
    // subscribe to the user in lightning service for changes 
    this.lightningService.sub_user.subscribe(value => {
      console.log('lightning service user changed');
      console.log(this.lightningService.user);
      //console.log(this.lightningService.role);
      this.user = this.lightningService.user;
      this.userTitle = this.lightningService.user.title;
      //this.role = this.lightningService.role;
      //console.log(this.role.view_admin_interface.valueOf());
    });
    // subscribe to UI changes
    this.lightningService.showCloseDialog.subscribe(value => {
      console.log('show close dialog');
      this.closeDialog();
      this.loginButtonVisible = false;
      this.logoutButtonVisible = true;
    });
    this.dialog.afterAllClosed.subscribe(data => {
      console.log("data returned from mat-dialog-close is ", data);
      this.lightningService.signinActive = false;
    });
  }
  loginChallenge() {
    console.log('App Component Login pressed');
    this.lightningService.loginChallenge().subscribe(authchall => {
      this.authchall = authchall;
      this.qrcodesrc = 'https://unlockd.gg/api/generate_qr/' + authchall.lnurl;
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
  decls: 25,
  vars: 6,
  consts: [["role", "banner", 1, "toolbar"], ["mat-button", "", "routerLink", "/"], ["mat-button", "", 3, "matMenuTriggerFor"], ["infomenu", "matMenu"], ["mat-menu-item", "", "routerLink", "costs"], ["mat-menu-item", "", "routerLink", "faq"], [1, "spacer"], [4, "ngIf"], ["mat-raised-button", "", 3, "click", 4, "ngIf"], ["role", "main", 1, "content"], ["mat-icon-button", "", "aria-label", "Example icon-button with a menu", 3, "matMenuTriggerFor"], ["adminmenu", "matMenu"], ["mat-menu-item", "", "routerLink", "admin-courses"], ["mat-menu-item", "", "routerLink", "admin/users"], ["mat-menu-item", "", "routerLink", "admin-roles"], ["developermenu", "matMenu"], ["menu", "matMenu"], ["mat-menu-item", "", "routerLink", "profile"], ["mat-menu-item", "", "routerLink", "transactions"], ["mat-menu-item", "", "routerLink", "badges"], ["mat-menu-item", "", 3, "click", 4, "ngIf"], ["mat-menu-item", "", 3, "click"], ["mat-raised-button", "", 3, "click"]],
  template: function AppComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](0, "div", 0)(1, "button", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](2, "unlockd");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](3, "button", 2);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](4, "info");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](5, "mat-menu", null, 3)(7, "button", 4)(8, "mat-icon");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](9, "currency_bitcoin");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](10, "span");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](11, "Service Costs");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](12, "button", 5)(13, "mat-icon");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](14, "quiz");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](15, "span");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtext"](16, "Frequently Asked Questions");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](17, "div", 6);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](18, AppComponent_span_18_Template, 4, 1, "span", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](19, AppComponent_span_19_Template, 22, 1, "span", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](20, AppComponent_span_20_Template, 22, 1, "span", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](21, AppComponent_span_21_Template, 26, 2, "span", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵtemplate"](22, AppComponent_button_22_Template, 2, 0, "button", 8);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementStart"](23, "div", 9);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelement"](24, "router-outlet");
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵelementEnd"]();
    }
    if (rf & 2) {
      const _r0 = _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵreference"](6);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](3);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("matMenuTriggerFor", _r0);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](15);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.logoutButtonVisible);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.lightningService.user.admin);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.lightningService.user.developer);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.logoutButtonVisible);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵproperty"]("ngIf", ctx.loginButtonVisible);
    }
  },
  dependencies: [_angular_common__WEBPACK_IMPORTED_MODULE_5__.NgIf, _angular_router__WEBPACK_IMPORTED_MODULE_4__.RouterOutlet, _angular_router__WEBPACK_IMPORTED_MODULE_4__.RouterLink, _angular_material_button__WEBPACK_IMPORTED_MODULE_6__.MatButton, _angular_material_button__WEBPACK_IMPORTED_MODULE_6__.MatIconButton, _angular_material_icon__WEBPACK_IMPORTED_MODULE_7__.MatIcon, _angular_material_menu__WEBPACK_IMPORTED_MODULE_8__.MatMenu, _angular_material_menu__WEBPACK_IMPORTED_MODULE_8__.MatMenuItem, _angular_material_menu__WEBPACK_IMPORTED_MODULE_8__.MatMenuTrigger],
  styles: ["/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsInNvdXJjZVJvb3QiOiIifQ== */", "[_nghost-%COMP%] {\n    font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, Helvetica, Arial, sans-serif, \"Apple Color Emoji\", \"Segoe UI Emoji\", \"Segoe UI Symbol\";\n    font-size: 14px;\n    color: #333;\n    box-sizing: border-box;\n    -webkit-font-smoothing: antialiased;\n    -moz-osx-font-smoothing: grayscale;\n  }\n\n  h1[_ngcontent-%COMP%], h2[_ngcontent-%COMP%], h3[_ngcontent-%COMP%], h4[_ngcontent-%COMP%], h5[_ngcontent-%COMP%], h6[_ngcontent-%COMP%] {\n    margin: 8px 0;\n  }\n\n  p[_ngcontent-%COMP%] {\n    margin: 0;\n  }\n\n  .spacer[_ngcontent-%COMP%] {\n    flex: 1;\n  }\n\n  .toolbar[_ngcontent-%COMP%] {\n    position: absolute;\n    top: 0;\n    left: 0;\n    right: 0;\n    height: 60px;\n    display: flex;\n    align-items: center;\n    background-color: #1976d2;\n    color: white;\n    font-weight: 600;\n  }\n\n  .toolbar[_ngcontent-%COMP%]   img[_ngcontent-%COMP%] {\n    margin: 0 16px;\n  }\n\n  .toolbar[_ngcontent-%COMP%]   #twitter-logo[_ngcontent-%COMP%] {\n    height: 40px;\n    margin: 0 8px;\n  }\n\n  .toolbar[_ngcontent-%COMP%]   #youtube-logo[_ngcontent-%COMP%] {\n    height: 40px;\n    margin: 0 16px;\n  }\n\n  .toolbar[_ngcontent-%COMP%]   #twitter-logo[_ngcontent-%COMP%]:hover, .toolbar[_ngcontent-%COMP%]   #youtube-logo[_ngcontent-%COMP%]:hover {\n    opacity: 0.8;\n  }\n\n  .content[_ngcontent-%COMP%] {\n    display: flex;\n    margin: 82px auto 32px;\n    padding: 0 16px;\n    max-width: 960px;\n    flex-direction: column;\n    align-items: center;\n  }\n\n  svg.material-icons[_ngcontent-%COMP%] {\n    height: 24px;\n    width: auto;\n  }\n\n  svg.material-icons[_ngcontent-%COMP%]:not(:last-child) {\n    margin-right: 8px;\n  }\n\n  .card[_ngcontent-%COMP%]   svg.material-icons[_ngcontent-%COMP%]   path[_ngcontent-%COMP%] {\n    fill: #888;\n  }\n\n  .card-container[_ngcontent-%COMP%] {\n    display: flex;\n    flex-wrap: wrap;\n    justify-content: center;\n    margin-top: 16px;\n  }\n\n  .card[_ngcontent-%COMP%] {\n    all: unset;\n    border-radius: 4px;\n    border: 1px solid #eee;\n    background-color: #fafafa;\n    height: 40px;\n    width: 200px;\n    margin: 0 8px 16px;\n    padding: 16px;\n    display: flex;\n    flex-direction: row;\n    justify-content: center;\n    align-items: center;\n    transition: all 0.2s ease-in-out;\n    line-height: 24px;\n  }\n\n  .card-container[_ngcontent-%COMP%]   .card[_ngcontent-%COMP%]:not(:last-child) {\n    margin-right: 0;\n  }\n\n  .card.card-small[_ngcontent-%COMP%] {\n    height: 16px;\n    width: 168px;\n  }\n\n  .card-container[_ngcontent-%COMP%]   .card[_ngcontent-%COMP%]:not(.highlight-card) {\n    cursor: pointer;\n  }\n\n  .card-container[_ngcontent-%COMP%]   .card[_ngcontent-%COMP%]:not(.highlight-card):hover {\n    transform: translateY(-3px);\n    box-shadow: 0 4px 17px rgba(0, 0, 0, 0.35);\n  }\n\n  .card-container[_ngcontent-%COMP%]   .card[_ngcontent-%COMP%]:not(.highlight-card):hover   .material-icons[_ngcontent-%COMP%]   path[_ngcontent-%COMP%] {\n    fill: rgb(105, 103, 103);\n  }\n\n  .card.highlight-card[_ngcontent-%COMP%] {\n    background-color: #1976d2;\n    color: white;\n    font-weight: 600;\n    border: none;\n    width: auto;\n    min-width: 30%;\n    position: relative;\n  }\n\n  .card.card.highlight-card[_ngcontent-%COMP%]   span[_ngcontent-%COMP%] {\n    margin-left: 60px;\n  }\n\n  svg#rocket[_ngcontent-%COMP%] {\n    width: 80px;\n    position: absolute;\n    left: -10px;\n    top: -24px;\n  }\n\n  svg#rocket-smoke[_ngcontent-%COMP%] {\n    height: calc(100vh - 95px);\n    position: absolute;\n    top: 10px;\n    right: 180px;\n    z-index: -10;\n  }\n\n  a[_ngcontent-%COMP%], a[_ngcontent-%COMP%]:visited, a[_ngcontent-%COMP%]:hover {\n    color: #1976d2;\n    text-decoration: none;\n  }\n\n  a[_ngcontent-%COMP%]:hover {\n    color: #125699;\n  }\n\n  .terminal[_ngcontent-%COMP%] {\n    position: relative;\n    width: 80%;\n    max-width: 600px;\n    border-radius: 6px;\n    padding-top: 45px;\n    margin-top: 8px;\n    overflow: hidden;\n    background-color: rgb(15, 15, 16);\n  }\n\n  .terminal[_ngcontent-%COMP%]::before {\n    content: \"\\2022 \\2022 \\2022\";\n    position: absolute;\n    top: 0;\n    left: 0;\n    height: 4px;\n    background: rgb(58, 58, 58);\n    color: #c2c3c4;\n    width: 100%;\n    font-size: 2rem;\n    line-height: 0;\n    padding: 14px 0;\n    text-indent: 4px;\n  }\n\n  .terminal[_ngcontent-%COMP%]   pre[_ngcontent-%COMP%] {\n    font-family: SFMono-Regular,Consolas,Liberation Mono,Menlo,monospace;\n    color: white;\n    padding: 0 1rem 1rem;\n    margin: 0;\n  }\n\n  .circle-link[_ngcontent-%COMP%] {\n    height: 40px;\n    width: 40px;\n    border-radius: 40px;\n    margin: 8px;\n    background-color: white;\n    border: 1px solid #eeeeee;\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    cursor: pointer;\n    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);\n    transition: 1s ease-out;\n  }\n\n  .circle-link[_ngcontent-%COMP%]:hover {\n    transform: translateY(-0.25rem);\n    box-shadow: 0px 3px 15px rgba(0, 0, 0, 0.2);\n  }\n\n  footer[_ngcontent-%COMP%] {\n    margin-top: 8px;\n    display: flex;\n    align-items: center;\n    line-height: 20px;\n  }\n\n  footer[_ngcontent-%COMP%]   a[_ngcontent-%COMP%] {\n    display: flex;\n    align-items: center;\n  }\n\n  .github-star-badge[_ngcontent-%COMP%] {\n    color: #24292e;\n    display: flex;\n    align-items: center;\n    font-size: 12px;\n    padding: 3px 10px;\n    border: 1px solid rgba(27,31,35,.2);\n    border-radius: 3px;\n    background-image: linear-gradient(-180deg,#fafbfc,#eff3f6 90%);\n    margin-left: 4px;\n    font-weight: 600;\n  }\n\n  .github-star-badge[_ngcontent-%COMP%]:hover {\n    background-image: linear-gradient(-180deg,#f0f3f6,#e6ebf1 90%);\n    border-color: rgba(27,31,35,.35);\n    background-position: -.5em;\n  }\n\n  .github-star-badge[_ngcontent-%COMP%]   .material-icons[_ngcontent-%COMP%] {\n    height: 16px;\n    width: 16px;\n    margin-right: 4px;\n  }\n\n  svg#clouds[_ngcontent-%COMP%] {\n    position: fixed;\n    bottom: -160px;\n    left: -230px;\n    z-index: -10;\n    width: 1920px;\n  }\n\n  \n\n  @media screen and (max-width: 767px) {\n    .card-container[_ngcontent-%COMP%]    > *[_ngcontent-%COMP%]:not(.circle-link), .terminal[_ngcontent-%COMP%] {\n      width: 100%;\n    }\n\n    .card[_ngcontent-%COMP%]:not(.highlight-card) {\n      height: 16px;\n      margin: 8px 0;\n    }\n\n    .card.highlight-card[_ngcontent-%COMP%]   span[_ngcontent-%COMP%] {\n      margin-left: 72px;\n    }\n\n    svg#rocket-smoke[_ngcontent-%COMP%] {\n      right: 120px;\n      transform: rotate(-5deg);\n    }\n  }\n\n  @media screen and (max-width: 575px) {\n    svg#rocket-smoke[_ngcontent-%COMP%] {\n      display: none;\n      visibility: hidden;\n    }\n  }"]
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
/* harmony import */ var _angular_platform_browser__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! @angular/platform-browser */ 6480);
/* harmony import */ var _angular_common_http__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! @angular/common/http */ 4860);
/* harmony import */ var _app_routing_module__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./app-routing.module */ 3966);
/* harmony import */ var _app_component__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./app.component */ 6401);
/* harmony import */ var _angular_platform_browser_animations__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! @angular/platform-browser/animations */ 4987);
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_23__ = __webpack_require__(/*! @angular/forms */ 8849);
/* harmony import */ var _angular_material_input__WEBPACK_IMPORTED_MODULE_26__ = __webpack_require__(/*! @angular/material/input */ 26);
/* harmony import */ var _angular_material_select__WEBPACK_IMPORTED_MODULE_25__ = __webpack_require__(/*! @angular/material/select */ 6355);
/* harmony import */ var _angular_material_form_field__WEBPACK_IMPORTED_MODULE_24__ = __webpack_require__(/*! @angular/material/form-field */ 1333);
/* harmony import */ var _angular_material_dialog__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! @angular/material/dialog */ 7401);
/* harmony import */ var _angular_material_button__WEBPACK_IMPORTED_MODULE_16__ = __webpack_require__(/*! @angular/material/button */ 895);
/* harmony import */ var _angular_material_icon__WEBPACK_IMPORTED_MODULE_17__ = __webpack_require__(/*! @angular/material/icon */ 6515);
/* harmony import */ var _angular_material_menu__WEBPACK_IMPORTED_MODULE_18__ = __webpack_require__(/*! @angular/material/menu */ 8128);
/* harmony import */ var _angular_material_datepicker__WEBPACK_IMPORTED_MODULE_20__ = __webpack_require__(/*! @angular/material/datepicker */ 2226);
/* harmony import */ var _angular_material_core__WEBPACK_IMPORTED_MODULE_19__ = __webpack_require__(/*! @angular/material/core */ 5309);
/* harmony import */ var _angular_material_checkbox__WEBPACK_IMPORTED_MODULE_21__ = __webpack_require__(/*! @angular/material/checkbox */ 6658);
/* harmony import */ var _angular_material_list__WEBPACK_IMPORTED_MODULE_22__ = __webpack_require__(/*! @angular/material/list */ 3228);
/* harmony import */ var _angular_material_grid_list__WEBPACK_IMPORTED_MODULE_27__ = __webpack_require__(/*! @angular/material/grid-list */ 647);
/* harmony import */ var _profile_profile_component__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./profile/profile.component */ 5229);
/* harmony import */ var _generic_response_dialog_generic_response_dialog_component__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./generic-response-dialog/generic-response-dialog.component */ 1642);
/* harmony import */ var _homepage_homepage_component__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./homepage/homepage.component */ 6905);
/* harmony import */ var _transactions_transactions_component__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./transactions/transactions.component */ 3186);
/* harmony import */ var _admin_users_users_component__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./admin/users/users.component */ 9909);
/* harmony import */ var _admin_user_detail_user_detail_component__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./admin/user-detail/user-detail.component */ 4702);
/* harmony import */ var _developer_games_games_component__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./developer/games/games.component */ 7820);
/* harmony import */ var _costs_costs_component__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./costs/costs.component */ 4208);
/* harmony import */ var _faq_faq_component__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./faq/faq.component */ 8970);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! @angular/core */ 1699);




























class AppModule {}
AppModule.ɵfac = function AppModule_Factory(t) {
  return new (t || AppModule)();
};
AppModule.ɵmod = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_11__["ɵɵdefineNgModule"]({
  type: AppModule,
  bootstrap: [_app_component__WEBPACK_IMPORTED_MODULE_1__.AppComponent]
});
AppModule.ɵinj = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_11__["ɵɵdefineInjector"]({
  imports: [_angular_platform_browser__WEBPACK_IMPORTED_MODULE_12__.BrowserModule, _app_routing_module__WEBPACK_IMPORTED_MODULE_0__.AppRoutingModule, _angular_common_http__WEBPACK_IMPORTED_MODULE_13__.HttpClientModule, _angular_platform_browser_animations__WEBPACK_IMPORTED_MODULE_14__.BrowserAnimationsModule, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_15__.MatDialogModule, _angular_material_button__WEBPACK_IMPORTED_MODULE_16__.MatButtonModule, _angular_material_icon__WEBPACK_IMPORTED_MODULE_17__.MatIconModule, _angular_material_menu__WEBPACK_IMPORTED_MODULE_18__.MatMenuModule, _angular_material_core__WEBPACK_IMPORTED_MODULE_19__.MatNativeDateModule, _angular_material_datepicker__WEBPACK_IMPORTED_MODULE_20__.MatDatepickerModule, _angular_material_checkbox__WEBPACK_IMPORTED_MODULE_21__.MatCheckboxModule, _angular_material_list__WEBPACK_IMPORTED_MODULE_22__.MatListModule, _angular_forms__WEBPACK_IMPORTED_MODULE_23__.FormsModule, _angular_forms__WEBPACK_IMPORTED_MODULE_23__.ReactiveFormsModule, _angular_material_form_field__WEBPACK_IMPORTED_MODULE_24__.MatFormFieldModule, _angular_material_select__WEBPACK_IMPORTED_MODULE_25__.MatSelectModule, _angular_material_input__WEBPACK_IMPORTED_MODULE_26__.MatInputModule, _angular_material_grid_list__WEBPACK_IMPORTED_MODULE_27__.MatGridListModule]
});

(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_11__["ɵɵsetNgModuleScope"](AppModule, {
    declarations: [_app_component__WEBPACK_IMPORTED_MODULE_1__.AppComponent, _profile_profile_component__WEBPACK_IMPORTED_MODULE_2__.ProfileComponent, _generic_response_dialog_generic_response_dialog_component__WEBPACK_IMPORTED_MODULE_3__.GenericResponseDialogComponent, _homepage_homepage_component__WEBPACK_IMPORTED_MODULE_4__.HomepageComponent, _transactions_transactions_component__WEBPACK_IMPORTED_MODULE_5__.TransactionsComponent, _admin_users_users_component__WEBPACK_IMPORTED_MODULE_6__.UsersComponent, _admin_user_detail_user_detail_component__WEBPACK_IMPORTED_MODULE_7__.UserDetailComponent, _developer_games_games_component__WEBPACK_IMPORTED_MODULE_8__.GamesComponent, _costs_costs_component__WEBPACK_IMPORTED_MODULE_9__.CostsComponent, _faq_faq_component__WEBPACK_IMPORTED_MODULE_10__.FaqComponent],
    imports: [_angular_platform_browser__WEBPACK_IMPORTED_MODULE_12__.BrowserModule, _app_routing_module__WEBPACK_IMPORTED_MODULE_0__.AppRoutingModule, _angular_common_http__WEBPACK_IMPORTED_MODULE_13__.HttpClientModule, _angular_platform_browser_animations__WEBPACK_IMPORTED_MODULE_14__.BrowserAnimationsModule, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_15__.MatDialogModule, _angular_material_button__WEBPACK_IMPORTED_MODULE_16__.MatButtonModule, _angular_material_icon__WEBPACK_IMPORTED_MODULE_17__.MatIconModule, _angular_material_menu__WEBPACK_IMPORTED_MODULE_18__.MatMenuModule, _angular_material_core__WEBPACK_IMPORTED_MODULE_19__.MatNativeDateModule, _angular_material_datepicker__WEBPACK_IMPORTED_MODULE_20__.MatDatepickerModule, _angular_material_checkbox__WEBPACK_IMPORTED_MODULE_21__.MatCheckboxModule, _angular_material_list__WEBPACK_IMPORTED_MODULE_22__.MatListModule, _angular_forms__WEBPACK_IMPORTED_MODULE_23__.FormsModule, _angular_forms__WEBPACK_IMPORTED_MODULE_23__.ReactiveFormsModule, _angular_material_form_field__WEBPACK_IMPORTED_MODULE_24__.MatFormFieldModule, _angular_material_select__WEBPACK_IMPORTED_MODULE_25__.MatSelectModule, _angular_material_input__WEBPACK_IMPORTED_MODULE_26__.MatInputModule, _angular_material_grid_list__WEBPACK_IMPORTED_MODULE_27__.MatGridListModule]
  });
})();

/***/ }),

/***/ 4208:
/*!******************************************!*\
  !*** ./src/app/costs/costs.component.ts ***!
  \******************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   CostsComponent: () => (/* binding */ CostsComponent)
/* harmony export */ });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ 1699);

class CostsComponent {}
CostsComponent.ɵfac = function CostsComponent_Factory(t) {
  return new (t || CostsComponent)();
};
CostsComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdefineComponent"]({
  type: CostsComponent,
  selectors: [["app-costs"]],
  decls: 16,
  vars: 0,
  template: function CostsComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](0, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](1, "unlockd.gg is an open source project. This website is a live demo, and contains functionality that can be used by game developers, and players.");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](2, "h1");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](3, "You are a game developer");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](4, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](5, "As a game developer, you can deploy your own version of this website (backend) and configure it however you like. You make your own decisions about fee structure and costs of operation.");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](6, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](7, "This website uses a 5% fee on game income to help cover our backend expenses. (if you don't agree with this, you can run your own)");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](8, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](9, "You can configure your game to charge players for various things, and this is totally up to you. You pay 5% on any income through these sources.");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](10, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](11, "You pay for dedicated server hosting uptime through the game wallet if used. unlockd does not mark this up, and the game is only charged for what is used. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](12, "h1");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](13, "You are a player");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](14, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](15, "Deposits and withdrawals, (will be) done over lightning, and there are no additional fees associated with this. You can deposit via lightning, play a few matches, then withdraw. You pay 5% to unlockd for any game transactions. Buying a skin for example, 5% of that transaction is a fee, which is collected by unlockd, and the other 95% goes to the game. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
    }
  },
  styles: ["/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsInNvdXJjZVJvb3QiOiIifQ== */"]
});


/***/ }),

/***/ 7820:
/*!****************************************************!*\
  !*** ./src/app/developer/games/games.component.ts ***!
  \****************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   GamesComponent: () => (/* binding */ GamesComponent)
/* harmony export */ });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ 1699);

class GamesComponent {}
GamesComponent.ɵfac = function GamesComponent_Factory(t) {
  return new (t || GamesComponent)();
};
GamesComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdefineComponent"]({
  type: GamesComponent,
  selectors: [["app-games"]],
  decls: 2,
  vars: 0,
  template: function GamesComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](0, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](1, "developer games works!");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
    }
  },
  styles: ["/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsInNvdXJjZVJvb3QiOiIifQ== */"]
});


/***/ }),

/***/ 8970:
/*!**************************************!*\
  !*** ./src/app/faq/faq.component.ts ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   FaqComponent: () => (/* binding */ FaqComponent)
/* harmony export */ });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ 1699);

class FaqComponent {}
FaqComponent.ɵfac = function FaqComponent_Factory(t) {
  return new (t || FaqComponent)();
};
FaqComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdefineComponent"]({
  type: FaqComponent,
  selectors: [["app-faq"]],
  decls: 11,
  vars: 0,
  consts: [["href", "https://discord.gg/QXQkq4dhdx"]],
  template: function FaqComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](0, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](1, "unlockd provides backend services for multiplayer and competitive video games.");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](2, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](3, "Things like, matchmaker, server management, player rankings, etc. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](4, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](5, "The code is now 100% open source which promotes decentralization and levels the playing field against the massively centralized dominant players in the space.");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](6, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](7, "This faq is under development. Why not stop by our ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](8, "a", 0);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](9, "discord server");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](10, " and ask some great questions that we can include?");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
    }
  },
  styles: ["/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsInNvdXJjZVJvb3QiOiIifQ== */"]
});


/***/ }),

/***/ 1642:
/*!******************************************************************************!*\
  !*** ./src/app/generic-response-dialog/generic-response-dialog.component.ts ***!
  \******************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   GenericResponseDialogComponent: () => (/* binding */ GenericResponseDialogComponent)
/* harmony export */ });
/* harmony import */ var _angular_material_dialog__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/material/dialog */ 7401);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ 1699);
/* harmony import */ var _angular_material_button__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @angular/material/button */ 895);




class GenericResponseDialogComponent {
  constructor(dialogRef, data) {
    this.dialogRef = dialogRef;
    this.data = data;
  }
  onCancel() {
    this.dialogRef.close();
  }
}
GenericResponseDialogComponent.ɵfac = function GenericResponseDialogComponent_Factory(t) {
  return new (t || GenericResponseDialogComponent)(_angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdirectiveInject"](_angular_material_dialog__WEBPACK_IMPORTED_MODULE_1__.MatDialogRef), _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdirectiveInject"](_angular_material_dialog__WEBPACK_IMPORTED_MODULE_1__.MAT_DIALOG_DATA));
};
GenericResponseDialogComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdefineComponent"]({
  type: GenericResponseDialogComponent,
  selectors: [["app-generic-response-dialog"]],
  decls: 7,
  vars: 2,
  consts: [["mat-dialog-title", ""], ["mat-dialog-content", ""], ["mat-dialog-actions", ""], ["mat-button", "", 3, "click"]],
  template: function GenericResponseDialogComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](0, "h1", 0);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](2, "div", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](3);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](4, "div", 2)(5, "button", 3);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵlistener"]("click", function GenericResponseDialogComponent_Template_button_click_5_listener() {
        return ctx.onCancel();
      });
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](6, "OK");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()();
    }
    if (rf & 2) {
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵadvance"](1);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtextInterpolate"](ctx.data.response_title);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵadvance"](2);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtextInterpolate1"](" ", ctx.data.response_message, " ");
    }
  },
  dependencies: [_angular_material_dialog__WEBPACK_IMPORTED_MODULE_1__.MatDialogTitle, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_1__.MatDialogContent, _angular_material_dialog__WEBPACK_IMPORTED_MODULE_1__.MatDialogActions, _angular_material_button__WEBPACK_IMPORTED_MODULE_2__.MatButton],
  styles: ["/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsInNvdXJjZVJvb3QiOiIifQ== */"]
});


/***/ }),

/***/ 6905:
/*!************************************************!*\
  !*** ./src/app/homepage/homepage.component.ts ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   HomepageComponent: () => (/* binding */ HomepageComponent)
/* harmony export */ });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ 1699);

class HomepageComponent {}
HomepageComponent.ɵfac = function HomepageComponent_Factory(t) {
  return new (t || HomepageComponent)();
};
HomepageComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdefineComponent"]({
  type: HomepageComponent,
  selectors: [["app-homepage"]],
  decls: 145,
  vars: 0,
  consts: [["id", "container"], ["id", "recent"], [1, "tag"], [1, "fourcolcontent", "post"], ["href", "#"], ["id", "comments", 1, "fourcolside"], [1, "clear"], [1, "divider"], ["id", "older"], [1, "fourcolside", "post"], ["href", "https://discord.gg/QXQkq4dhdx"], ["id", "navigate"], [1, "fourcolside"], ["href", "https://github.com/unlockd-gg/ExampleGame"], ["href", "https://github.com/unlockd-gg/online-subsystem"], ["href", "https://github.com/unlockd-gg/metagame"], ["href", "https://github.com/unlockd-gg/backend"], ["href", "https://github.com/unlockd-gg/UnrealEngine"], ["href", "https://github.com/unlockd-gg/socketIO-server"], ["href", "https://github.com/unlockd-gg/launcher"], ["href", "https://twitter.com/ed_unlockd"], ["href", "/img/btc_donations.png"], ["href", "https://getalby.com/element.png"], ["href", "https://uetopia.com"], ["href", "https://github.com/uetopia/"], [1, "fourcolsidesmall"], ["href", "http://www.gregponchak.com"]],
  template: function HomepageComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](0, "div", 0)(1, "div", 1)(2, "div", 2);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](3, "Now");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](4, "div", 3)(5, "h3")(6, "a", 4);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](7, "gaming unlockd");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](8, " Open source, decentralized, bitcoin powered tools for modern multiplayer and competitive games.");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](9, "br");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](10, " Run your own multiplayer game backend, and customize it however you want. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](11, "div", 5)(12, "h5")(13, "a", 4);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](14, "21");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](15, "div", 6);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](16, "div", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](17, "div", 8)(18, "div", 2);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](19, "Mission");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](20, "div", 9)(21, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](22, "Bitcoin Only");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](23, " We are exclusively focused on bitcoin. No site token, no shi*coins. BTC and lightning ftw. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](24, "div", 9)(25, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](26, "Support developers");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](27, " Indie and small studios need backend game solutions. Providing complete open source access allows devs and studios to run a customized backend. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](28, "div", 9)(29, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](30, "Promote decentralization");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](31, " Multiplayer games still require high performance, realtime, dedicated servers. Especially in the case of competitive games, or games with an economy, these servers need to be under control of the game developer. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](32, "div", 9)(33, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](34, "Encourage self custody");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](35, " We remind users to withdraw sats from the site at the end of a gaming session. We will provide help and instructions on how to do this. Lightning makes deposit and withdraw quick and easy. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](36, "div", 6);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](37, "div", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](38, "div", 8)(39, "div", 2);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](40, "TASKS");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](41, "div", 9)(42, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](43, "Convert backend to python 3 runtime");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](44, " Python 2.7 is no longer supported, and we need to convert. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](45, "div", 9)(46, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](47, "Convert metagame to python 3 runtime");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](48, " Python 2.7 is no longer supported, and we need to convert. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](49, "div", 9)(50, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](51, "Convert examplegame to use pub/priv key auth");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](52, " Remove firebase auth and replace with lnurl login. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](53, "div", 9)(54, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](55, "Integrate lightning deposit/withdraw");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](56, " Remove braintree payments, and replace with lightning. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](57, "div", 9)(58, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](59, "Remove uetopia references throughout");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](60, " uetopia is mentioned throughout the codebase, and we need to replace it. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](61, "div", 9)(62, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](63, "Sunsetting uetopia");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](64, " The uetopia website and legacy functionality will be retained until January 2024. Users and games should run a backend instance or find an alternative before this time. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](65, "div", 9)(66, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](67, "Community Discord");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](68, "a", 10);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](69, "Discord Server");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](70, " up and running. Stop by and chat about games. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](71, "div", 6);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](72, "div", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](73, "div", 11)(74, "div", 2);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](75, "Navigate");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](76, "div", 12)(77, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](78, "Repositories");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](79, "ul")(80, "li")(81, "a", 13);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](82, "Example Game");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](83, "li")(84, "a", 14);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](85, "Unreal Engine Plugin");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](86, "li")(87, "a", 15);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](88, "Metagame");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](89, "li")(90, "a", 16);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](91, "Backend");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](92, "li")(93, "a", 17);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](94, "Unreal Engine");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](95, "li")(96, "a", 18);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](97, "SocketIO Server");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](98, "li")(99, "a", 19);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](100, "Launcher");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](101, "div", 12)(102, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](103, "Social");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](104, "ul")(105, "li")(106, "a", 10);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](107, "Discord");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](108, "li")(109, "a", 20);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](110, "Twitter");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](111, "div", 12)(112, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](113, "Support");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](114, "ul")(115, "li")(116, "a", 21);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](117, "bitcoin donations");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](118, "li")(119, "a", 22);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](120, "lightning donations");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](121, "div", 12)(122, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](123, "uetopia/legacy");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](124, "ul")(125, "li")(126, "a", 23);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](127, "Backend");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](128, "li")(129, "a", 24);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](130, "Repositories");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](131, "div", 6);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](132, "div", 6)(133, "div", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](134, "div", 12);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](135, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](136, "div", 12);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](137, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](138, "div", 12);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](139, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](140, "div", 25);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](141, "This page designed and coded by ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](142, "a", 26);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](143, "Greg Ponchak");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](144, ".");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
    }
  },
  styles: ["*[_ngcontent-%COMP%]\n{\n\tlist-style:none;\n\ttext-decoration:none;\n\tborder:0;\n\tfont-weight:400;\n\tmargin:0;\n\tpadding:0;\n}\n\nbody[_ngcontent-%COMP%]\n{\n\tbackground:#fff;\n\tfont-family:helvetica, arial, sans-serif;\n\tcolor:#333;\n\tline-height:18px;\n\tfont-size:11px;\n}\n\na[_ngcontent-%COMP%]\n{\n\tcolor:#BE04F4;\n\ttext-decoration:none;\n}\n\na[_ngcontent-%COMP%]:hover\n{\n\ttext-decoration:none;\n}\n\nb[_ngcontent-%COMP%]\n{\n\tfont-weight:700;\n}\n\nblockquote[_ngcontent-%COMP%]\n{\n\tcolor:#aaa;\n\tpadding:10px;\n}\n\nh1[_ngcontent-%COMP%], h1[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\ttext-decoration:none;\n\tline-height:30px;\n\tfont-size:30px;\n\tcolor:#333;\n}\n\nh2[_ngcontent-%COMP%], h2[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\ttext-decoration:none;\n\tline-height:26px;\n\tfont-size:26px;\n\tcolor:#333;\n}\n\nh3[_ngcontent-%COMP%], h3[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\ttext-decoration:none;\n\tline-height:22px;\n\tfont-size:22px;\n\tcolor:#333;\n}\n\nh4[_ngcontent-%COMP%], h4[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\ttext-decoration:none;\n\tline-height:18px;\n\tfont-size:18px;\n\tcolor:#333;\n}\n\nh5[_ngcontent-%COMP%], h5[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\ttext-decoration:none;\n\tline-height:14px;\n\tfont-size:14px;\n\tcolor:#333;\n}\n\np[_ngcontent-%COMP%]\n{\n\tmargin-bottom:10px;\n}\n\nsmall[_ngcontent-%COMP%]\n{\n\tfont-size:10px;\n}\n\n.clear[_ngcontent-%COMP%]\n{\n\tclear:both;\n}\n\n#container[_ngcontent-%COMP%]\n{\n\twidth:960px;\n\tmargin:110px auto;\n}\n\n.fourcolcontent[_ngcontent-%COMP%]\n{\n\tfloat:left;\n\twidth:710px;\n\tpadding-right:10px;\n\tposition:relative;\n}\n\n.fourcolside[_ngcontent-%COMP%]\n{\n\tfloat:left;\n\twidth:230px;\n\tpadding-right:10px;\n\tposition:relative;\n}\n\n.fourcolsidesmall[_ngcontent-%COMP%]\n{\n\tfont-size:7px;\n\tfloat:left;\n\twidth:230px;\n\tpadding-right:10px;\n\tposition:relative;\n}\n\n.divider[_ngcontent-%COMP%]\n{\n\theight:7px;\n\twidth:100%;\n\tbackground:#333;\n\tmargin:30px 0;\n}\n\n.tag[_ngcontent-%COMP%]\n{\n\ttext-align:right;\n\tright:965px;\n\tposition:absolute;\n\tbackground:#BE04F4;\n\tcolor:#fff;\n\ttext-transform:uppercase;\n\tpadding:2px;\n}\n\n#header[_ngcontent-%COMP%]\n{\n\theight:55px;\n\tbackground:#fff;\n\tleft:0;\n\tposition:fixed !important;\n\tposition:absolute;\n\tright:0;\n\ttop:0;\n}\n\n#headerinner[_ngcontent-%COMP%]\n{\n\tmargin:0 auto;\n\twidth:960px;\n}\n\n#header[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]\n{\n\toverflow:hidden;\n}\n\n#title[_ngcontent-%COMP%]   h1[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tcolor:#333;\n\tfont-size:21px;\n\tline-height:80px;\n\tfont-weight:700;\n}\n\n#description[_ngcontent-%COMP%]   h3[_ngcontent-%COMP%]\n{\n\tcolor:#333;\n\tfont-size:16px;\n\tline-height:80px;\n}\n\n#navigation[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tline-height:80px;\n\tpadding:0 10px;\n}\n\n#recent[_ngcontent-%COMP%]   .post[_ngcontent-%COMP%]   h3[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tfont-size:36px;\n\tline-height:36px;\n\tcolor:#333;\n\tpadding-bottom:10px;\n\tfont-weight:700;\n}\n\n#recent[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]   h5[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tfont-size:72px;\n\ttext-align:center;\n\tline-height:72px;\n\tpadding-top:36px;\n\tdisplay:block;\n\tfont-weight:700;\n}\n\n#comments[_ngcontent-%COMP%]\n{\n\ttext-align:center;\n}\n\n#recent[_ngcontent-%COMP%], #older[_ngcontent-%COMP%], #navigate[_ngcontent-%COMP%]\n{\n\tposition:relative;\n}\n\n#older[_ngcontent-%COMP%]   .post[_ngcontent-%COMP%]\n{\n\tcolor:#aaa;\n\tmax-height:144px;\n\toverflow:hidden;\n\tborder-bottom:7px solid #fff;\n\tmargin-bottom:3px;\n}\n\n#older[_ngcontent-%COMP%]   .post[_ngcontent-%COMP%]:hover\n{\n\tborder-bottom:7px solid #BE04F4;\n\tcolor:#888;\n}\n\n#older[_ngcontent-%COMP%]   .post[_ngcontent-%COMP%]:hover   h3[_ngcontent-%COMP%]\n{\n\tcolor:#333;\n}\n\n#older[_ngcontent-%COMP%]   .more[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tfont-size:60px;\n\tline-height:60px;\n\ttext-transform:uppercase;\n\tcolor:#aaa;\n\tbackground:#ddd;\n\tmargin-top:10px;\n\tdisplay:block;\n\ttext-align:center;\n\tpadding:10px;\n}\n\n#older[_ngcontent-%COMP%]   .more[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]:hover\n{\n\tcolor:#999;\n\tbackground:#ccc;\n}\n\n#navigate[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]   ul[_ngcontent-%COMP%]   li[_ngcontent-%COMP%]\n{\n\tdisplay:inline;\n}\n\n#navigate[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]   ul[_ngcontent-%COMP%]   li[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]\n{\n\tdisplay:block;\n\tcolor:#aaa;\n\tpadding:2px;\n}\n\n#navigate[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]   ul[_ngcontent-%COMP%]   li[_ngcontent-%COMP%]   a[_ngcontent-%COMP%]:hover\n{\n\tcolor:#ff00c0;\n}\n\n#older[_ngcontent-%COMP%]   .post[_ngcontent-%COMP%]   h3[_ngcontent-%COMP%], #navigate[_ngcontent-%COMP%]   .fourcolside[_ngcontent-%COMP%]   h3[_ngcontent-%COMP%]\n{\n\tfont-size:18px;\n\tline-height:18px;\n\tcolor:#999;\n}\n\n\n/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8uL3NyYy9hcHAvaG9tZXBhZ2UvaG9tZXBhZ2UuY29tcG9uZW50LmNzcyJdLCJuYW1lcyI6W10sIm1hcHBpbmdzIjoiQUFBQTs7Q0FFQyxlQUFlO0NBQ2Ysb0JBQW9CO0NBQ3BCLFFBQVE7Q0FDUixlQUFlO0NBQ2YsUUFBUTtDQUNSLFNBQVM7QUFDVjs7QUFFQTs7Q0FFQyxlQUFlO0NBQ2Ysd0NBQXdDO0NBQ3hDLFVBQVU7Q0FDVixnQkFBZ0I7Q0FDaEIsY0FBYztBQUNmOztBQUVBOztDQUVDLGFBQWE7Q0FDYixvQkFBb0I7QUFDckI7O0FBRUE7O0NBRUMsb0JBQW9CO0FBQ3JCOztBQUVBOztDQUVDLGVBQWU7QUFDaEI7O0FBRUE7O0NBRUMsVUFBVTtDQUNWLFlBQVk7QUFDYjs7QUFFQTs7Q0FFQyxvQkFBb0I7Q0FDcEIsZ0JBQWdCO0NBQ2hCLGNBQWM7Q0FDZCxVQUFVO0FBQ1g7O0FBRUE7O0NBRUMsb0JBQW9CO0NBQ3BCLGdCQUFnQjtDQUNoQixjQUFjO0NBQ2QsVUFBVTtBQUNYOztBQUVBOztDQUVDLG9CQUFvQjtDQUNwQixnQkFBZ0I7Q0FDaEIsY0FBYztDQUNkLFVBQVU7QUFDWDs7QUFFQTs7Q0FFQyxvQkFBb0I7Q0FDcEIsZ0JBQWdCO0NBQ2hCLGNBQWM7Q0FDZCxVQUFVO0FBQ1g7O0FBRUE7O0NBRUMsb0JBQW9CO0NBQ3BCLGdCQUFnQjtDQUNoQixjQUFjO0NBQ2QsVUFBVTtBQUNYOztBQUVBOztDQUVDLGtCQUFrQjtBQUNuQjs7QUFFQTs7Q0FFQyxjQUFjO0FBQ2Y7O0FBRUE7O0NBRUMsVUFBVTtBQUNYOztBQUVBOztDQUVDLFdBQVc7Q0FDWCxpQkFBaUI7QUFDbEI7O0FBRUE7O0NBRUMsVUFBVTtDQUNWLFdBQVc7Q0FDWCxrQkFBa0I7Q0FDbEIsaUJBQWlCO0FBQ2xCOztBQUVBOztDQUVDLFVBQVU7Q0FDVixXQUFXO0NBQ1gsa0JBQWtCO0NBQ2xCLGlCQUFpQjtBQUNsQjs7QUFFQTs7Q0FFQyxhQUFhO0NBQ2IsVUFBVTtDQUNWLFdBQVc7Q0FDWCxrQkFBa0I7Q0FDbEIsaUJBQWlCO0FBQ2xCOztBQUVBOztDQUVDLFVBQVU7Q0FDVixVQUFVO0NBQ1YsZUFBZTtDQUNmLGFBQWE7QUFDZDs7QUFFQTs7Q0FFQyxnQkFBZ0I7Q0FDaEIsV0FBVztDQUNYLGlCQUFpQjtDQUNqQixrQkFBa0I7Q0FDbEIsVUFBVTtDQUNWLHdCQUF3QjtDQUN4QixXQUFXO0FBQ1o7O0FBRUE7O0NBRUMsV0FBVztDQUNYLGVBQWU7Q0FDZixNQUFNO0NBQ04seUJBQXlCO0NBQ3pCLGlCQUFpQjtDQUNqQixPQUFPO0NBQ1AsS0FBSztBQUNOOztBQUVBOztDQUVDLGFBQWE7Q0FDYixXQUFXO0FBQ1o7O0FBRUE7O0NBRUMsZUFBZTtBQUNoQjs7QUFFQTs7Q0FFQyxVQUFVO0NBQ1YsY0FBYztDQUNkLGdCQUFnQjtDQUNoQixlQUFlO0FBQ2hCOztBQUVBOztDQUVDLFVBQVU7Q0FDVixjQUFjO0NBQ2QsZ0JBQWdCO0FBQ2pCOztBQUVBOztDQUVDLGdCQUFnQjtDQUNoQixjQUFjO0FBQ2Y7O0FBRUE7O0NBRUMsY0FBYztDQUNkLGdCQUFnQjtDQUNoQixVQUFVO0NBQ1YsbUJBQW1CO0NBQ25CLGVBQWU7QUFDaEI7O0FBRUE7O0NBRUMsY0FBYztDQUNkLGlCQUFpQjtDQUNqQixnQkFBZ0I7Q0FDaEIsZ0JBQWdCO0NBQ2hCLGFBQWE7Q0FDYixlQUFlO0FBQ2hCOztBQUVBOztDQUVDLGlCQUFpQjtBQUNsQjs7QUFFQTs7Q0FFQyxpQkFBaUI7QUFDbEI7O0FBRUE7O0NBRUMsVUFBVTtDQUNWLGdCQUFnQjtDQUNoQixlQUFlO0NBQ2YsNEJBQTRCO0NBQzVCLGlCQUFpQjtBQUNsQjs7QUFFQTs7Q0FFQywrQkFBK0I7Q0FDL0IsVUFBVTtBQUNYOztBQUVBOztDQUVDLFVBQVU7QUFDWDs7QUFFQTs7Q0FFQyxjQUFjO0NBQ2QsZ0JBQWdCO0NBQ2hCLHdCQUF3QjtDQUN4QixVQUFVO0NBQ1YsZUFBZTtDQUNmLGVBQWU7Q0FDZixhQUFhO0NBQ2IsaUJBQWlCO0NBQ2pCLFlBQVk7QUFDYjs7QUFFQTs7Q0FFQyxVQUFVO0NBQ1YsZUFBZTtBQUNoQjs7QUFFQTs7Q0FFQyxjQUFjO0FBQ2Y7O0FBRUE7O0NBRUMsYUFBYTtDQUNiLFVBQVU7Q0FDVixXQUFXO0FBQ1o7O0FBRUE7O0NBRUMsYUFBYTtBQUNkOztBQUVBOztDQUVDLGNBQWM7Q0FDZCxnQkFBZ0I7Q0FDaEIsVUFBVTtBQUNYIiwic291cmNlc0NvbnRlbnQiOlsiKlxyXG57XHJcblx0bGlzdC1zdHlsZTpub25lO1xyXG5cdHRleHQtZGVjb3JhdGlvbjpub25lO1xyXG5cdGJvcmRlcjowO1xyXG5cdGZvbnQtd2VpZ2h0OjQwMDtcclxuXHRtYXJnaW46MDtcclxuXHRwYWRkaW5nOjA7XHJcbn1cclxuXHJcbmJvZHlcclxue1xyXG5cdGJhY2tncm91bmQ6I2ZmZjtcclxuXHRmb250LWZhbWlseTpoZWx2ZXRpY2EsIGFyaWFsLCBzYW5zLXNlcmlmO1xyXG5cdGNvbG9yOiMzMzM7XHJcblx0bGluZS1oZWlnaHQ6MThweDtcclxuXHRmb250LXNpemU6MTFweDtcclxufVxyXG5cclxuYVxyXG57XHJcblx0Y29sb3I6I0JFMDRGNDtcclxuXHR0ZXh0LWRlY29yYXRpb246bm9uZTtcclxufVxyXG5cclxuYTpob3ZlclxyXG57XHJcblx0dGV4dC1kZWNvcmF0aW9uOm5vbmU7XHJcbn1cclxuXHJcbmJcclxue1xyXG5cdGZvbnQtd2VpZ2h0OjcwMDtcclxufVxyXG5cclxuYmxvY2txdW90ZVxyXG57XHJcblx0Y29sb3I6I2FhYTtcclxuXHRwYWRkaW5nOjEwcHg7XHJcbn1cclxuXHJcbmgxLGgxIGFcclxue1xyXG5cdHRleHQtZGVjb3JhdGlvbjpub25lO1xyXG5cdGxpbmUtaGVpZ2h0OjMwcHg7XHJcblx0Zm9udC1zaXplOjMwcHg7XHJcblx0Y29sb3I6IzMzMztcclxufVxyXG5cclxuaDIsaDIgYVxyXG57XHJcblx0dGV4dC1kZWNvcmF0aW9uOm5vbmU7XHJcblx0bGluZS1oZWlnaHQ6MjZweDtcclxuXHRmb250LXNpemU6MjZweDtcclxuXHRjb2xvcjojMzMzO1xyXG59XHJcblxyXG5oMyxoMyBhXHJcbntcclxuXHR0ZXh0LWRlY29yYXRpb246bm9uZTtcclxuXHRsaW5lLWhlaWdodDoyMnB4O1xyXG5cdGZvbnQtc2l6ZToyMnB4O1xyXG5cdGNvbG9yOiMzMzM7XHJcbn1cclxuXHJcbmg0LGg0IGFcclxue1xyXG5cdHRleHQtZGVjb3JhdGlvbjpub25lO1xyXG5cdGxpbmUtaGVpZ2h0OjE4cHg7XHJcblx0Zm9udC1zaXplOjE4cHg7XHJcblx0Y29sb3I6IzMzMztcclxufVxyXG5cclxuaDUsaDUgYVxyXG57XHJcblx0dGV4dC1kZWNvcmF0aW9uOm5vbmU7XHJcblx0bGluZS1oZWlnaHQ6MTRweDtcclxuXHRmb250LXNpemU6MTRweDtcclxuXHRjb2xvcjojMzMzO1xyXG59XHJcblxyXG5wXHJcbntcclxuXHRtYXJnaW4tYm90dG9tOjEwcHg7XHJcbn1cclxuXHJcbnNtYWxsXHJcbntcclxuXHRmb250LXNpemU6MTBweDtcclxufVxyXG5cclxuLmNsZWFyXHJcbntcclxuXHRjbGVhcjpib3RoO1xyXG59XHJcblxyXG4jY29udGFpbmVyXHJcbntcclxuXHR3aWR0aDo5NjBweDtcclxuXHRtYXJnaW46MTEwcHggYXV0bztcclxufVxyXG5cclxuLmZvdXJjb2xjb250ZW50XHJcbntcclxuXHRmbG9hdDpsZWZ0O1xyXG5cdHdpZHRoOjcxMHB4O1xyXG5cdHBhZGRpbmctcmlnaHQ6MTBweDtcclxuXHRwb3NpdGlvbjpyZWxhdGl2ZTtcclxufVxyXG5cclxuLmZvdXJjb2xzaWRlXHJcbntcclxuXHRmbG9hdDpsZWZ0O1xyXG5cdHdpZHRoOjIzMHB4O1xyXG5cdHBhZGRpbmctcmlnaHQ6MTBweDtcclxuXHRwb3NpdGlvbjpyZWxhdGl2ZTtcclxufVxyXG5cclxuLmZvdXJjb2xzaWRlc21hbGxcclxue1xyXG5cdGZvbnQtc2l6ZTo3cHg7XHJcblx0ZmxvYXQ6bGVmdDtcclxuXHR3aWR0aDoyMzBweDtcclxuXHRwYWRkaW5nLXJpZ2h0OjEwcHg7XHJcblx0cG9zaXRpb246cmVsYXRpdmU7XHJcbn1cclxuXHJcbi5kaXZpZGVyXHJcbntcclxuXHRoZWlnaHQ6N3B4O1xyXG5cdHdpZHRoOjEwMCU7XHJcblx0YmFja2dyb3VuZDojMzMzO1xyXG5cdG1hcmdpbjozMHB4IDA7XHJcbn1cclxuXHJcbi50YWdcclxue1xyXG5cdHRleHQtYWxpZ246cmlnaHQ7XHJcblx0cmlnaHQ6OTY1cHg7XHJcblx0cG9zaXRpb246YWJzb2x1dGU7XHJcblx0YmFja2dyb3VuZDojQkUwNEY0O1xyXG5cdGNvbG9yOiNmZmY7XHJcblx0dGV4dC10cmFuc2Zvcm06dXBwZXJjYXNlO1xyXG5cdHBhZGRpbmc6MnB4O1xyXG59XHJcblxyXG4jaGVhZGVyXHJcbntcclxuXHRoZWlnaHQ6NTVweDtcclxuXHRiYWNrZ3JvdW5kOiNmZmY7XHJcblx0bGVmdDowO1xyXG5cdHBvc2l0aW9uOmZpeGVkICFpbXBvcnRhbnQ7XHJcblx0cG9zaXRpb246YWJzb2x1dGU7XHJcblx0cmlnaHQ6MDtcclxuXHR0b3A6MDtcclxufVxyXG5cclxuI2hlYWRlcmlubmVyXHJcbntcclxuXHRtYXJnaW46MCBhdXRvO1xyXG5cdHdpZHRoOjk2MHB4O1xyXG59XHJcblxyXG4jaGVhZGVyIC5mb3VyY29sc2lkZVxyXG57XHJcblx0b3ZlcmZsb3c6aGlkZGVuO1xyXG59XHJcblxyXG4jdGl0bGUgaDEgYVxyXG57XHJcblx0Y29sb3I6IzMzMztcclxuXHRmb250LXNpemU6MjFweDtcclxuXHRsaW5lLWhlaWdodDo4MHB4O1xyXG5cdGZvbnQtd2VpZ2h0OjcwMDtcclxufVxyXG5cclxuI2Rlc2NyaXB0aW9uIGgzXHJcbntcclxuXHRjb2xvcjojMzMzO1xyXG5cdGZvbnQtc2l6ZToxNnB4O1xyXG5cdGxpbmUtaGVpZ2h0OjgwcHg7XHJcbn1cclxuXHJcbiNuYXZpZ2F0aW9uIGFcclxue1xyXG5cdGxpbmUtaGVpZ2h0OjgwcHg7XHJcblx0cGFkZGluZzowIDEwcHg7XHJcbn1cclxuXHJcbiNyZWNlbnQgLnBvc3QgaDMgYVxyXG57XHJcblx0Zm9udC1zaXplOjM2cHg7XHJcblx0bGluZS1oZWlnaHQ6MzZweDtcclxuXHRjb2xvcjojMzMzO1xyXG5cdHBhZGRpbmctYm90dG9tOjEwcHg7XHJcblx0Zm9udC13ZWlnaHQ6NzAwO1xyXG59XHJcblxyXG4jcmVjZW50IC5mb3VyY29sc2lkZSBoNSBhXHJcbntcclxuXHRmb250LXNpemU6NzJweDtcclxuXHR0ZXh0LWFsaWduOmNlbnRlcjtcclxuXHRsaW5lLWhlaWdodDo3MnB4O1xyXG5cdHBhZGRpbmctdG9wOjM2cHg7XHJcblx0ZGlzcGxheTpibG9jaztcclxuXHRmb250LXdlaWdodDo3MDA7XHJcbn1cclxuXHJcbiNjb21tZW50c1xyXG57XHJcblx0dGV4dC1hbGlnbjpjZW50ZXI7XHJcbn1cclxuXHJcbiNyZWNlbnQsI29sZGVyLCNuYXZpZ2F0ZVxyXG57XHJcblx0cG9zaXRpb246cmVsYXRpdmU7XHJcbn1cclxuXHJcbiNvbGRlciAucG9zdFxyXG57XHJcblx0Y29sb3I6I2FhYTtcclxuXHRtYXgtaGVpZ2h0OjE0NHB4O1xyXG5cdG92ZXJmbG93OmhpZGRlbjtcclxuXHRib3JkZXItYm90dG9tOjdweCBzb2xpZCAjZmZmO1xyXG5cdG1hcmdpbi1ib3R0b206M3B4O1xyXG59XHJcblxyXG4jb2xkZXIgLnBvc3Q6aG92ZXJcclxue1xyXG5cdGJvcmRlci1ib3R0b206N3B4IHNvbGlkICNCRTA0RjQ7XHJcblx0Y29sb3I6Izg4ODtcclxufVxyXG5cclxuI29sZGVyIC5wb3N0OmhvdmVyIGgzXHJcbntcclxuXHRjb2xvcjojMzMzO1xyXG59XHJcblxyXG4jb2xkZXIgLm1vcmUgYVxyXG57XHJcblx0Zm9udC1zaXplOjYwcHg7XHJcblx0bGluZS1oZWlnaHQ6NjBweDtcclxuXHR0ZXh0LXRyYW5zZm9ybTp1cHBlcmNhc2U7XHJcblx0Y29sb3I6I2FhYTtcclxuXHRiYWNrZ3JvdW5kOiNkZGQ7XHJcblx0bWFyZ2luLXRvcDoxMHB4O1xyXG5cdGRpc3BsYXk6YmxvY2s7XHJcblx0dGV4dC1hbGlnbjpjZW50ZXI7XHJcblx0cGFkZGluZzoxMHB4O1xyXG59XHJcblxyXG4jb2xkZXIgLm1vcmUgYTpob3ZlclxyXG57XHJcblx0Y29sb3I6Izk5OTtcclxuXHRiYWNrZ3JvdW5kOiNjY2M7XHJcbn1cclxuXHJcbiNuYXZpZ2F0ZSAuZm91cmNvbHNpZGUgdWwgbGlcclxue1xyXG5cdGRpc3BsYXk6aW5saW5lO1xyXG59XHJcblxyXG4jbmF2aWdhdGUgLmZvdXJjb2xzaWRlIHVsIGxpIGFcclxue1xyXG5cdGRpc3BsYXk6YmxvY2s7XHJcblx0Y29sb3I6I2FhYTtcclxuXHRwYWRkaW5nOjJweDtcclxufVxyXG5cclxuI25hdmlnYXRlIC5mb3VyY29sc2lkZSB1bCBsaSBhOmhvdmVyXHJcbntcclxuXHRjb2xvcjojZmYwMGMwO1xyXG59XHJcblxyXG4jb2xkZXIgLnBvc3QgaDMsI25hdmlnYXRlIC5mb3VyY29sc2lkZSBoM1xyXG57XHJcblx0Zm9udC1zaXplOjE4cHg7XHJcblx0bGluZS1oZWlnaHQ6MThweDtcclxuXHRjb2xvcjojOTk5O1xyXG59XHJcblxyXG4iXSwic291cmNlUm9vdCI6IiJ9 */"]
});


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
    this.apiUrl = 'https://unlockd.gg/api'; // URL to web api - in quotes - no trailing slash:  'http://54.176.48.9'
    this.lappUrl = 'https://unlockd.gg/lapp'; // URL to lightning  api - in quotes - no trailing slash:  'http://54.176.48.9'
    this.authChallengeResponse = '';
    this.qrCode = '';
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
      emailvalidated: false,
      admin: false,
      developer: false
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
          _this.update_user(result.user['title'], result.user['address'], result.user['admin']);
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
    const auth_url = `${this.lappUrl}/do-login`;
    return this.http.get(auth_url).pipe((0,rxjs_operators__WEBPACK_IMPORTED_MODULE_2__.tap)(
    // Log the result or error
    {
      //next: (data) => this.log(data['lnurl']), // this works
      //next: (data) => this.authChallengeResponse = data['lnurl'], // this too
      next: data => this.registerACR(data['lnurl'], data['qrCode']),
      error: error => this.log('error')
    }));
  }
  registerACR(aCR, qrCode) {
    console.log('register ACR');
    console.log(aCR);
    this.authChallengeResponse = aCR;
    this.signinActive = true;
    this.qrCode = qrCode;
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
  update_user(title, address, admin) {
    console.log('lightning service update user');
    this.user['title'] = title;
    this.user['admin'] = admin;
    this.sub_user.next(true);
  }
  doLogout() {
    this.user['admin'] = false;
    this.user['developer'] = false;
  }
  requestLogin() {
    this.login_user.next(true);
    this.user = {
      id: 0,
      title: 'Service Test User',
      emailvalidated: false,
      admin: false,
      developer: false
    };
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

/***/ 5892:
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
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("src", ctx_r7.qrCode, _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵsanitizeUrl"]);
  }
}
function LoginDialogComponent_div_2_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 3);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](1, LoginDialogComponent_div_2_div_1_Template, 13, 1, "div", 4);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](2, LoginDialogComponent_div_2_div_2_Template, 10, 1, "div", 4);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
  if (rf & 2) {
    const ctx_r0 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx_r0.loginmodebrowser);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", ctx_r0.loginmodeQR);
  }
}
function LoginDialogComponent_div_3_Template(rf, ctx) {
  if (rf & 1) {
    const _r9 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 3)(1, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](2, "You are logged in with lightning. ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](3, "h1", 0);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](4, "Optional: Validate email");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](5, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](6, "Connect your lightning login with an email address for additional features. Account recovery, gamer handle, group membership, developer tools, and more.");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](7, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](8, "We will never sell your email address, or give it away to anyone.");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](9, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](10, " Email address: ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](11, "input", 10);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("ngModelChange", function LoginDialogComponent_div_3_Template_input_ngModelChange_11_listener($event) {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r9);
      const ctx_r8 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r8.emailaddress = $event);
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
    const _r11 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 3)(1, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](2, "Please check your email for the 6 digit security code ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](3, "h1", 0);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](4, "Optional: Validate email");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](5, "p");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](6, " VerificationCode: ");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](7, "input", 11);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("ngModelChange", function LoginDialogComponent_div_4_Template_input_ngModelChange_7_listener($event) {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r11);
      const ctx_r10 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r10.emailaddressverificationcode = $event);
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
    const _r15 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "button", 17);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_5_button_2_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r15);
      const ctx_r14 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r14.changeLoginMode("browser"));
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Login with browser");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
}
function LoginDialogComponent_div_5_button_3_Template(rf, ctx) {
  if (rf & 1) {
    const _r17 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "button", 18);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_5_button_3_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r17);
      const ctx_r16 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r16.changeLoginMode("qrcode"));
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Login with QR code");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
}
function LoginDialogComponent_div_5_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 12)(1, "div", 13);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](2, LoginDialogComponent_div_5_button_2_Template, 2, 0, "button", 14);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](3, LoginDialogComponent_div_5_button_3_Template, 2, 0, "button", 15);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](4, "button", 16);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](5, "Close");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()()();
  }
  if (rf & 2) {
    const ctx_r3 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](2);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", !ctx_r3.loginmodebrowser);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵadvance"](1);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵproperty"]("ngIf", !ctx_r3.loginmodeQR);
  }
}
function LoginDialogComponent_div_6_Template(rf, ctx) {
  if (rf & 1) {
    const _r19 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 3)(1, "div", 13)(2, "button", 17);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_6_Template_button_click_2_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r19);
      const ctx_r18 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"]();
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r18.submitEmail());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](3, "Submit Email");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](4, "button", 16);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](5, "Close");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]()()();
  }
}
function LoginDialogComponent_div_7_button_2_Template(rf, ctx) {
  if (rf & 1) {
    const _r23 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "button", 17);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_7_button_2_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r23);
      const ctx_r22 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r22.validateEmail());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Verify Email");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
}
function LoginDialogComponent_div_7_button_3_Template(rf, ctx) {
  if (rf & 1) {
    const _r25 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵgetCurrentView"]();
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "button", 17);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵlistener"]("click", function LoginDialogComponent_div_7_button_3_Template_button_click_0_listener() {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵrestoreView"](_r25);
      const ctx_r24 = _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵnextContext"](2);
      return _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵresetView"](ctx_r24.validateEmailNoLightning());
    });
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Verify Email NL");
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
  }
}
function LoginDialogComponent_div_7_Template(rf, ctx) {
  if (rf & 1) {
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "div", 3)(1, "div", 13);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](2, LoginDialogComponent_div_7_button_2_Template, 2, 0, "button", 14);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](3, LoginDialogComponent_div_7_button_3_Template, 2, 0, "button", 14);
    _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](4, "button", 16);
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
    this.qrcodesrc = 'https://unlockd.gg/api/generate_qr/' + this.lightningService.getLnUrl();
    this.qrCode = this.lightningService.qrCode;
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
  consts: [["mat-dialog-title", ""], ["mat-dialog-content", "", 4, "ngIf"], ["mat-dialog-actions", "", 4, "ngIf"], ["mat-dialog-content", ""], [4, "ngIf"], [1, "webln-button", "d-none", "btn", "btn-primary", "mx-auto"], ["href", "https://getalby.com"], ["href", "https://coincharge.io/en/lnurl-for-lightning-wallets/"], ["href", "", 1, "qr-link"], ["id", "qr_image", 1, "qr", 3, "src"], ["type", "email", "email", "", 3, "ngModel", "ngModelChange"], ["type", "text", 3, "ngModel", "ngModelChange"], ["mat-dialog-actions", ""], [1, "login-button-row"], ["mat-raised-button", "", "color", "primary", 3, "click", 4, "ngIf"], ["mat-raised-button", "", "color", "accent", 3, "click", 4, "ngIf"], ["mat-raised-button", "", "color", "warn", "mat-dialog-close", ""], ["mat-raised-button", "", "color", "primary", 3, "click"], ["mat-raised-button", "", "color", "accent", 3, "click"]],
  template: function LoginDialogComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementStart"](0, "h1", 0);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtext"](1, "Login to unlockd");
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](2, LoginDialogComponent_div_2_Template, 3, 2, "div", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](3, LoginDialogComponent_div_3_Template, 14, 2, "div", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](4, LoginDialogComponent_div_4_Template, 10, 2, "div", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_1__["ɵɵtemplate"](5, LoginDialogComponent_div_5_Template, 6, 2, "div", 2);
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

/***/ 5229:
/*!**********************************************!*\
  !*** ./src/app/profile/profile.component.ts ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   ProfileComponent: () => (/* binding */ ProfileComponent)
/* harmony export */ });
/* harmony import */ var C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/asyncToGenerator.js */ 1670);
/* harmony import */ var _angular_forms__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @angular/forms */ 8849);
/* harmony import */ var _generic_response_dialog_generic_response_dialog_component__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../generic-response-dialog/generic-response-dialog.component */ 1642);
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @angular/core */ 1699);
/* harmony import */ var _lightning_service__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../lightning.service */ 707);
/* harmony import */ var _angular_material_dialog__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @angular/material/dialog */ 7401);
/* harmony import */ var _angular_material_button__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @angular/material/button */ 895);
/* harmony import */ var _angular_material_checkbox__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! @angular/material/checkbox */ 6658);
/* harmony import */ var _angular_material_form_field__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @angular/material/form-field */ 1333);
/* harmony import */ var _angular_material_input__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! @angular/material/input */ 26);











class ProfileComponent {
  constructor(lightningService, dialog) {
    var _this = this;
    this.lightningService = lightningService;
    this.dialog = dialog;
    this.profile_user_json = {};
    this.member = false;
    this.user = {
      id: 0,
      title: 'Profile User',
      emailvalidated: false,
      admin: false,
      developer: false
    };
    this.title = new _angular_forms__WEBPACK_IMPORTED_MODULE_3__.FormControl('');
    this.developer = new _angular_forms__WEBPACK_IMPORTED_MODULE_3__.FormControl('');
    this.getUserData = /*#__PURE__*/(0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      if (localStorage.getItem("token") === null) {
        console.log('profile - no access token');
      } else {
        const response = yield fetch(_this.lightningService.apiUrl + '/users/data', {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem("token")}`
          }
        });
        const result = yield response.json();
        console.log(result);
        console.log(result.user);
        console.log(result.status);
        if (result.status == "401") {
          _this.lightningService.requestLogin();
        }
        if (result.user) {
          console.log('found user');
          _this.user = result.user;
          _this.title.setValue(result.user['title']);
          _this.developer.setValue(result.user['developer']);
          //this.admin = result.user['admin'];
        }
      }
    });

    this.updateProfile = /*#__PURE__*/(0,C_Users_Ed_Documents_GitHub_backend_unlockd_webclient_node_modules_babel_runtime_helpers_esm_asyncToGenerator_js__WEBPACK_IMPORTED_MODULE_0__["default"])(function* () {
      console.log('update profile');
      console.log(localStorage.getItem("token"));
      //const location = window.location.hostname; // this works for live
      const location = '13.56.127.211'; // hardcoding for now
      const settings = {
        method: 'POST',
        headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem("token")}`
        },
        body: JSON.stringify({
          'title': _this.title.value,
          'developer': _this.developer.value
        })
      };
      //try {
      const fetchResponse = yield fetch(_this.lightningService.apiUrl + '/users/profile/update', settings);
      console.log(fetchResponse);
      const data = yield fetchResponse.json();
      // TODO - update localstorage with the new profile data
      //const result = await data.json();
      console.log(data);
      //localStorage.setItem('user', JSON.stringify(result.user));
      _this.dialog.open(_generic_response_dialog_generic_response_dialog_component__WEBPACK_IMPORTED_MODULE_1__.GenericResponseDialogComponent, {
        data: {
          response_message: data['response_message'],
          response_title: data['response_title']
        }
      });
      localStorage.setItem('usertitle', _this.title.value || "Lightning User!");
      // we want to do an update at some point, later.
      // doing this here, results in overwriting the actual form data
      _this.lightningService.getUserData();
      //this.profile_user_json = result.user;
      return data;
      //} catch (e) {
      //    return e;
      //} 
    });
  }

  ngOnInit() {
    console.log('profile init');
    //this.title.setValue(this.lightningService.user['title']);
    this.getUserData();
  }
}
ProfileComponent.ɵfac = function ProfileComponent_Factory(t) {
  return new (t || ProfileComponent)(_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdirectiveInject"](_lightning_service__WEBPACK_IMPORTED_MODULE_2__.LightningService), _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdirectiveInject"](_angular_material_dialog__WEBPACK_IMPORTED_MODULE_5__.MatDialog));
};
ProfileComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵdefineComponent"]({
  type: ProfileComponent,
  selectors: [["app-profile"]],
  decls: 14,
  vars: 2,
  consts: [[1, "ng-binding"], ["heroForm", "ngForm"], [1, "example-full-width"], ["for", "title"], ["matInput", "", "id", "title", "type", "text", 3, "formControl"], [3, "formControl"], ["mat-raised-button", "", "color", "primary", 3, "click"]],
  template: function ProfileComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](0, "h3", 0)(1, "b");
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtext"](2, "Update My Profile");
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](3, "form", null, 1)(5, "mat-form-field", 2)(6, "mat-label", 3);
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtext"](7, "Name ");
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelement"](8, "input", 4);
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](9, "p")(10, "mat-checkbox", 5);
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtext"](11, "developer");
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementStart"](12, "button", 6);
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵlistener"]("click", function ProfileComponent_Template_button_click_12_listener() {
        return ctx.updateProfile();
      });
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵtext"](13, "Update Profile");
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵelementEnd"]();
    }
    if (rf & 2) {
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"](8);
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("formControl", ctx.title);
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵadvance"](2);
      _angular_core__WEBPACK_IMPORTED_MODULE_4__["ɵɵproperty"]("formControl", ctx.developer);
    }
  },
  dependencies: [_angular_material_button__WEBPACK_IMPORTED_MODULE_6__.MatButton, _angular_material_checkbox__WEBPACK_IMPORTED_MODULE_7__.MatCheckbox, _angular_forms__WEBPACK_IMPORTED_MODULE_3__["ɵNgNoValidate"], _angular_forms__WEBPACK_IMPORTED_MODULE_3__.DefaultValueAccessor, _angular_forms__WEBPACK_IMPORTED_MODULE_3__.NgControlStatus, _angular_forms__WEBPACK_IMPORTED_MODULE_3__.NgControlStatusGroup, _angular_forms__WEBPACK_IMPORTED_MODULE_3__.NgForm, _angular_forms__WEBPACK_IMPORTED_MODULE_3__.FormControlDirective, _angular_material_form_field__WEBPACK_IMPORTED_MODULE_8__.MatFormField, _angular_material_form_field__WEBPACK_IMPORTED_MODULE_8__.MatLabel, _angular_material_input__WEBPACK_IMPORTED_MODULE_9__.MatInput],
  styles: ["/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsInNvdXJjZVJvb3QiOiIifQ== */"]
});


/***/ }),

/***/ 3186:
/*!********************************************************!*\
  !*** ./src/app/transactions/transactions.component.ts ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TransactionsComponent: () => (/* binding */ TransactionsComponent)
/* harmony export */ });
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ 1699);

class TransactionsComponent {}
TransactionsComponent.ɵfac = function TransactionsComponent_Factory(t) {
  return new (t || TransactionsComponent)();
};
TransactionsComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdefineComponent"]({
  type: TransactionsComponent,
  selectors: [["app-transactions"]],
  decls: 2,
  vars: 0,
  template: function TransactionsComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](0, "p");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](1, "transactions works!");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
    }
  },
  styles: ["/*# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJzb3VyY2VzIjpbXSwibmFtZXMiOltdLCJtYXBwaW5ncyI6IiIsInNvdXJjZVJvb3QiOiIifQ== */"]
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