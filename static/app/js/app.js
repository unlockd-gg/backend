var app = angular.module('uetopiaFrontEnd', [
    'ui.router',
    'ngResource',
    'uetopiaFrontEnd.router',
    'uetopiaFrontEnd.controller',
    'firebase',
    'ngMaterial',
    'angularMoment',
]);

app.constant('AppSettings', {ver: '1.2.2',
                            defaultApiVersion: 'v1',
                            apiUrl: 'https://ue4topia.appspot.com/_ah/api',
                            //apiUrl: 'https://apitest-dot-ue4topia.appspot.com/_ah/api',
                            //apiUrl: 'https://debugging-dot-ue4topia.appspot.com/_ah/api',
                            //apiUrl: 'https://api-dot-ue4topia.appspot.com/_ah/api',
                            //apiUrl: '//localhost:8080/_ah/api',
                            projectName: 'ue4topia'});

app.factory("Auth", ["$firebaseAuth",
  function($firebaseAuth) {
    return $firebaseAuth();
  }
]);

app.run(['$state', '$rootScope', '$window', 'endpoints','$http', '$firebaseArray', '$firebaseObject','$location','moment',
    function($state, $rootScope, $window, endpoints, $http, $firebaseArray, $firebaseObject, $location, moment) {

        //$rootScope.auth = auth;
        //$rootScope.session = session;
        $rootScope.user = null;
        $rootScope.userAccount = null;
        $rootScope.alerts = {};
        $rootScope.friends = {};
        $rootScope.userAccount_loaded = false;
        $rootScope.show_terms = true;
        $rootScope.show_friends = false;

        $rootScope.currentNavItem = 'home';

        $rootScope.loggedOutHeaderSmall = true;

        $rootScope.viewLoginButtons = false;
        $rootScope.toggleViewLoginButtons = function () {
          $rootScope.viewLoginButtons = !$rootScope.viewLoginButtons;
        }

        $rootScope.CREDValue = 0.0;

        // This is passed into the backend to authenticate the user.
        var userIdToken = null;

        // We are getting duplicate user registrations sometimes because of the way firebase spams refreshes on the page.
        // Trying to isolate so only one request happens at a time.
        var checkAuthenticationInProgress = false;

        $http.defaults.headers.common['X-UETOPIA-Auth'] = null;

        var CLIENT = 'x.apps.googleusercontent.com'; // replace with your key
        var BASE;
        if($window.location.hostname == 'localhost') {
            BASE = '//localhost:8080/_ah/api';
        } else {
            BASE = 'https://ue4topia.appspot.com/_ah/api';
        }

        firebase.auth().onAuthStateChanged(function(user) {
          console.log('app.js - onAuthStateChanged')
          if (user) {
            console.log('onAuthStateChanged - user found')
            user.getToken().then(function(idToken) {
              userIdToken = idToken;
              $http.defaults.headers.common['X-UETOPIA-Auth'] = 'Bearer ' + userIdToken;
              checkEndpointsAuthentication();

              $rootScope.user = user;

              var ref = firebase.database().ref().child('users').child($rootScope.user.uid);
              $rootScope.userAccount = $firebaseObject(ref);

              $rootScope.userAccount.$loaded(
                function(data) {
                  console.log('userAccount loaded')
                  $rootScope.userAccount_loaded = true;
                  if ($rootScope.userAccount.agreed_with_terms) {
                    $rootScope.show_terms = false;
                  } else {
                    console.log('show terms');
                  }
                }
              )

              var user_online_ref = firebase.database().ref().child('users').child($rootScope.user.uid).child('online');
              user_online_ref.onDisconnect().set(false);

              //var user_presence_ref = firebase.database().ref().child('presence').child($rootScope.user.uid).child('online');
              //user_presence_ref.onDisconnect().set(false);


              var ref = firebase.database().ref().child('users').child($rootScope.user.uid).child('alerts');
              $rootScope.alerts = $firebaseArray(ref);

              var ref = firebase.database().ref().child('users').child($rootScope.user.uid).child('friends');
              $rootScope.friends = $firebaseArray(ref);

            })
          } else {
            $http.defaults.headers.common['X-UETOPIA-Auth'] = null;
          }
        });


        // [START configureFirebaseLoginWidget]
        // Firebase log-in widget
        configureFirebaseLoginWidget = function() {
          var uiConfig = {
            'signInSuccessUrl': '/',
            callbacks: {
                signInSuccess: function(currentUser, credential, redirectUrl) {
                    console.log('sign in success');
                    console.log(currentUser);
                    // alert(currentUser)
                    currentUser.getToken().then(function(idToken) {
                      console.log('got token');
                      userIdToken = idToken;
                      $http.defaults.headers.common['X-UETOPIA-Auth'] = 'Bearer ' + userIdToken;
                      endpoints.post('users', 'clientSignIn', {})
                          .then(function(response) {
                              // DONE!
                              console.log(response);
                              $window.location.reload();
                              if (response.refresh_token) {
                                console.log('Firebase Unauth - REFRESHING');
                                console.log(firebase.auth());
                              }
                          }, function() {
                            console.log('error');
                          });
                        })
                    return false;
                },
                uiShown: function () {
                    console.log("uiShow");
                }
            },
            'signInOptions': [
              // Leave the lines as is for the providers you want to offer your users.
              firebase.auth.GoogleAuthProvider.PROVIDER_ID,
              //firebase.auth.FacebookAuthProvider.PROVIDER_ID,
              //firebase.auth.TwitterAuthProvider.PROVIDER_ID,
              firebase.auth.GithubAuthProvider.PROVIDER_ID,
              //firebase.auth.EmailAuthProvider.PROVIDER_ID
            ],
            // Terms of service url
            'tosUrl': '<your-tos-url>',
          };

          var ui = new firebaseui.auth.AuthUI(firebase.auth());
          ui.start('#firebaseui-auth-container', uiConfig);
        }
        // [END configureFirebaseLoginWidget]

        checkEndpointsAuthentication = function() {
          if (userIdToken) {
              endpoints.post('users', 'clientConnect', {})
                  .then(function(response) {
                      // DONE!
                      console.log(response);
                      if (response.refresh_token) {
                        console.log('Firebase Unauth - REFRESHING');
                        console.log(firebase.auth());
                      }
                      //setTimeout(resetCheckAuthenticationInProgress(), 2000);
                  }, function() {
                    // ERROR!
                    console.log('error');
                    //setTimeout(resetCheckAuthenticationInProgress(), 2000);
                  });
          } else {
            console.log('no userIdToken found - skipping');
          }
        };

        // TODO new function which can execute after a delay which will reset the state of checkAuthenticationInProgress
        // I think it is being reset too quickly in some cases.

        resetCheckAuthenticationInProgress = function() {
          checkAuthenticationInProgress = false;
        }

        // This is for the setting of the title.
        // we need this for our token authorization scheme

        $rootScope.$on("$stateChangeError", function(event, toState, toParams, fromState, fromParams, error) {
          console.log("$stateChangeError");
          console.log(error);
          if (error === "AUTH_REQUIRED") {
            console.log("AUTH_REQUIRED");
            // pass in some params to the login $state, with the requested
            // state within the <code>toWhere</code> value
            $state.go('home', { toWhere: toState });
          }
        });

        $rootScope.title = "Home";

        $rootScope.$on('$stateChangeSuccess', function (event, current, previous) {
            console.log('stateChangeSuccess');
            console.log(current);
            $rootScope.title = current.title;
            if ($rootScope.userAccount_loaded) {
              if ($rootScope.show_terms) {
                if (current.name != 'Home' && current.name != 'Agreement' ) {
                  console.log('not home and not agreement - redirecting to terms');
                  $state.go('agreement');
                }
              }
            }
        });


        $rootScope.removeAlert= function(alert) {
          console.log('removeAlert');
          $rootScope.alerts.$remove(alert);
        };



        $rootScope.logout = function() {
            //auth.$unauth();
            firebase.auth().signOut().then(function() {
              // Sign-out successful.
              console.log('Sign-out successful.');
              $rootScope.user = null;
            }, function(error) {
              // An error happened.
              console.log('An error happened.');
            });
        };

        // analytics
        $rootScope.$on('$routeChangeSuccess', $window.ga('send', 'pageview', { page: $location.url() }) );

        $rootScope.closeFriends = function () {
          // Component lookup should always be available since we are not using `ng-if`
          $mdSidenav('right').close()
            .then(function () {
              $log.debug("close RIGHT is done");
            });
        };

        $rootScope.toggleFriends = function () {
          console.log('toggling friends');
          $rootScope.show_friends = !$rootScope.show_friends;
        };

        var credref = firebase.database().ref().child('currency').child('CRED').child('value_to_usd');
        $rootScope.CREDValue = $firebaseObject(credref);


        configureFirebaseLoginWidget();
    }
]);
