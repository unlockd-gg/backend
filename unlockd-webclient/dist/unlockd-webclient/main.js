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
/* harmony import */ var _angular_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @angular/core */ 1699);
/* harmony import */ var _angular_router__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @angular/router */ 7947);


class AppComponent {
  constructor() {
    this.title = 'unlockd-webclient';
  }
}
AppComponent.ɵfac = function AppComponent_Factory(t) {
  return new (t || AppComponent)();
};
AppComponent.ɵcmp = /*@__PURE__*/_angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵdefineComponent"]({
  type: AppComponent,
  selectors: [["app-root"]],
  decls: 180,
  vars: 0,
  consts: [["role", "banner", 1, "toolbar"], ["width", "40", "alt", "Angular Logo", "src", "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTAgMjUwIj4KICAgIDxwYXRoIGZpbGw9IiNERDAwMzEiIGQ9Ik0xMjUgMzBMMzEuOSA2My4ybDE0LjIgMTIzLjFMMTI1IDIzMGw3OC45LTQzLjcgMTQuMi0xMjMuMXoiIC8+CiAgICA8cGF0aCBmaWxsPSIjQzMwMDJGIiBkPSJNMTI1IDMwdjIyLjItLjFWMjMwbDc4LjktNDMuNyAxNC4yLTEyMy4xTDEyNSAzMHoiIC8+CiAgICA8cGF0aCAgZmlsbD0iI0ZGRkZGRiIgZD0iTTEyNSA1Mi4xTDY2LjggMTgyLjZoMjEuN2wxMS43LTI5LjJoNDkuNGwxMS43IDI5LjJIMTgzTDEyNSA1Mi4xem0xNyA4My4zaC0zNGwxNy00MC45IDE3IDQwLjl6IiAvPgogIDwvc3ZnPg=="], [1, "spacer"], ["aria-label", "Angular on twitter", "target", "_blank", "rel", "noopener", "href", "https://twitter.com/angular", "title", "Twitter"], ["id", "twitter-logo", "height", "24", "data-name", "Logo", "xmlns", "http://www.w3.org/2000/svg", "viewBox", "0 0 400 400"], ["width", "400", "height", "400", "fill", "none"], ["d", "M153.62,301.59c94.34,0,145.94-78.16,145.94-145.94,0-2.22,0-4.43-.15-6.63A104.36,104.36,0,0,0,325,122.47a102.38,102.38,0,0,1-29.46,8.07,51.47,51.47,0,0,0,22.55-28.37,102.79,102.79,0,0,1-32.57,12.45,51.34,51.34,0,0,0-87.41,46.78A145.62,145.62,0,0,1,92.4,107.81a51.33,51.33,0,0,0,15.88,68.47A50.91,50.91,0,0,1,85,169.86c0,.21,0,.43,0,.65a51.31,51.31,0,0,0,41.15,50.28,51.21,51.21,0,0,1-23.16.88,51.35,51.35,0,0,0,47.92,35.62,102.92,102.92,0,0,1-63.7,22A104.41,104.41,0,0,1,75,278.55a145.21,145.21,0,0,0,78.62,23", "fill", "#fff"], ["aria-label", "Angular on YouTube", "target", "_blank", "rel", "noopener", "href", "https://youtube.com/angular", "title", "YouTube"], ["id", "youtube-logo", "height", "24", "width", "24", "data-name", "Logo", "xmlns", "http://www.w3.org/2000/svg", "viewBox", "0 0 24 24", "fill", "#fff"], ["d", "M0 0h24v24H0V0z", "fill", "none"], ["d", "M21.58 7.19c-.23-.86-.91-1.54-1.77-1.77C18.25 5 12 5 12 5s-6.25 0-7.81.42c-.86.23-1.54.91-1.77 1.77C2 8.75 2 12 2 12s0 3.25.42 4.81c.23.86.91 1.54 1.77 1.77C5.75 19 12 19 12 19s6.25 0 7.81-.42c.86-.23 1.54-.91 1.77-1.77C22 15.25 22 12 22 12s0-3.25-.42-4.81zM10 15V9l5.2 3-5.2 3z"], ["role", "main", 1, "content"], ["id", "container"], ["id", "recent"], [1, "tag"], [1, "fourcolcontent", "post"], ["href", "#"], ["id", "comments", 1, "fourcolside"], [1, "clear"], [1, "divider"], ["id", "older"], [1, "fourcolside", "post"], ["href", "https://discord.gg/QXQkq4dhdx"], ["id", "navigate"], [1, "fourcolside"], ["href", "https://github.com/unlockd-gg/ExampleGame"], ["href", "https://github.com/unlockd-gg/online-subsystem"], ["href", "https://github.com/unlockd-gg/metagame"], ["href", "https://github.com/unlockd-gg/backend"], ["href", "https://github.com/unlockd-gg/UnrealEngine"], ["href", "https://github.com/unlockd-gg/socketIO-server"], ["href", "https://github.com/unlockd-gg/launcher"], ["href", "/img/btc_donations.png"], ["href", "https://getalby.com/element.png"], ["href", "https://uetopia.com"], ["href", "https://github.com/uetopia/"], [1, "fourcolsidesmall"], ["href", "http://www.gregponchak.com"], ["id", "header"], ["id", "headerinner"], ["id", "title", 1, "fourcolside"], ["id", "description", 1, "fourcolside"], ["id", "navigation", 1, "fourcolside"], ["href", "https://github.com/unlockd-gg/"]],
  template: function AppComponent_Template(rf, ctx) {
    if (rf & 1) {
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](0, "div", 0);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](1, "img", 1);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](2, "span");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](3, "Welcome");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](4, "div", 2);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](5, "a", 3);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵnamespaceSVG"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](6, "svg", 4);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](7, "rect", 5)(8, "path", 6);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵnamespaceHTML"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](9, "a", 7);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵnamespaceSVG"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](10, "svg", 8);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](11, "path", 9)(12, "path", 10);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵnamespaceHTML"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](13, "div", 11)(14, "div", 12)(15, "div", 13)(16, "div", 14);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](17, "Now");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](18, "div", 15)(19, "h3")(20, "a", 16);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](21, "uetopia is unlockd");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](22, " We are moving beyond only supporting Unreal Engine, and aim to support all multiplayer game engines. Godot, Unity, and Lumberyard devs - LFG! We are also making some changes to support our ethics and mission. Open source, decentralization, and bitcoin. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](23, "div", 17)(24, "h5")(25, "a", 16);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](26, "21");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](27, "div", 18);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](28, "div", 19);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](29, "div", 20)(30, "div", 14);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](31, "Mission");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](32, "div", 21)(33, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](34, "Bitcoin Only");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](35, " We are exclusively focused on bitcoin. No site token, no shi*coins. It's btc and lightning ftw. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](36, "div", 21)(37, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](38, "Support developers");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](39, " Indie and small studios need backend game solutions. Providing complete open source access allows devs and studios to run a customized backend. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](40, "div", 21)(41, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](42, "Promote decentralization");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](43, " Multiplayer games still require high performance, realtime, dedicated servers. Especially in the case of competitive games, or games with an economy, these servers need to be under control of the game developer. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](44, "div", 21)(45, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](46, "Encourage self custody");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](47, " We remind users to withdraw sats from the site at the end of a gaming session. We will provide help and instructions on how to do this. Lightning makes deposit and withdraw quick and easy. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](48, "div", 18);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](49, "div", 19);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](50, "div", 20)(51, "div", 14);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](52, "TASKS");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](53, "div", 21)(54, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](55, "Convert backend to python 3 runtime");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](56, " Python 2.7 is no longer supported, and we need to convert. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](57, "div", 21)(58, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](59, "Convert metagame to python 3 runtime");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](60, " Python 2.7 is no longer supported, and we need to convert. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](61, "div", 21)(62, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](63, "Convert examplegame to use pub/priv key auth");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](64, " Remove firebase auth and replace with lnurl login. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](65, "div", 21)(66, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](67, "Integrate lightning deposit/withdraw");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](68, " Remove braintree payments, and replace with lightning. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](69, "div", 21)(70, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](71, "Remove uetopia references throughout");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](72, " uetopia is mentioned throughout the codebase, and we need to replace it. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](73, "div", 21)(74, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](75, "Sunsetting uetopia");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](76, " The uetopia website and legacy functionality will be retained until January 2024. Users and games should run a backend instance or find an alternative before this time. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](77, "div", 21)(78, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](79, "Community Discord");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](80, "a", 22);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](81, "Discord Server");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](82, " up and running. Stop by and chat about games. ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](83, "div", 18);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](84, "div", 19);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](85, "div", 23)(86, "div", 14);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](87, "Navigate");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](88, "div", 24)(89, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](90, "Repositories");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](91, "ul")(92, "li")(93, "a", 25);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](94, "Example Game");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](95, "li")(96, "a", 26);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](97, "Unreal Engine Plugin");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](98, "li")(99, "a", 27);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](100, "Metagame");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](101, "li")(102, "a", 28);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](103, "Backend");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](104, "li")(105, "a", 29);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](106, "Unreal Engine");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](107, "li")(108, "a", 30);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](109, "SocketIO Server");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](110, "li")(111, "a", 31);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](112, "Launcher");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](113, "div", 24)(114, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](115, "Social");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](116, "ul")(117, "li")(118, "a", 22);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](119, "Discord");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](120, "li")(121, "a", 16);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](122, "Twitter");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](123, "li")(124, "a", 16);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](125, "Blog");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](126, "div", 24)(127, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](128, "Support");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](129, "ul")(130, "li")(131, "a", 32);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](132, "bitcoin donations");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](133, "li")(134, "a", 33);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](135, "lightning donations");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](136, "div", 24)(137, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](138, "uetopia/legacy");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](139, "ul")(140, "li")(141, "a", 34);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](142, "Backend");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](143, "li")(144, "a", 35);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](145, "Repositories");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](146, "div", 18);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](147, "div", 18)(148, "div", 19);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](149, "div", 24);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](150, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](151, "div", 24);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](152, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](153, "div", 24);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](154, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](155, "div", 36);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](156, "This page designed and coded by ");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](157, "a", 37);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](158, "Greg Ponchak");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](159, ".");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](160, "div", 38)(161, "div", 39)(162, "div", 40)(163, "h1")(164, "a", 16);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](165, "unlockd.gg");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](166, "div", 41)(167, "h3");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](168, "Open Game Backend");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](169, "div", 24);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](170, "\u00A0");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](171, "div", 42)(172, "a", 16);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](173, "Home");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](174, "a", 43);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](175, "Contribute");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementStart"](176, "a", 22);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵtext"](177, "Discuss");
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](178, "div", 18);
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelementEnd"]()()();
      _angular_core__WEBPACK_IMPORTED_MODULE_0__["ɵɵelement"](179, "router-outlet");
    }
  },
  dependencies: [_angular_router__WEBPACK_IMPORTED_MODULE_1__.RouterOutlet],
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
/* harmony import */ var _app_routing_module__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./app-routing.module */ 3966);
/* harmony import */ var _app_component__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./app.component */ 6401);
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
  imports: [_angular_platform_browser__WEBPACK_IMPORTED_MODULE_3__.BrowserModule, _app_routing_module__WEBPACK_IMPORTED_MODULE_0__.AppRoutingModule]
});

(function () {
  (typeof ngJitMode === "undefined" || ngJitMode) && _angular_core__WEBPACK_IMPORTED_MODULE_2__["ɵɵsetNgModuleScope"](AppModule, {
    declarations: [_app_component__WEBPACK_IMPORTED_MODULE_1__.AppComponent],
    imports: [_angular_platform_browser__WEBPACK_IMPORTED_MODULE_3__.BrowserModule, _app_routing_module__WEBPACK_IMPORTED_MODULE_0__.AppRoutingModule]
  });
})();

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