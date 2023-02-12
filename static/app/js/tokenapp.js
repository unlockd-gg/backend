var app = angular.module('uetopiaFrontEnd', [
    'ui.router',
    'ngResource',
    'uetopiaFrontEnd.tokenapp.router',
    'uetopiaFrontEnd.tokenapp.controller',
    'firebase',
    'ngMaterial',

]);

app.constant('AppSettings', {ver: '1.2.2',
                            defaultApiVersion: 'v1',
                            apiUrl: 'https://ue4topia.appspot.com/_ah/api',
                            //apiUrl: '//localhost:8080/_ah/api',
                            projectName: 'ue4topia'});

app.factory("Auth", ["$firebaseAuth",
  function($firebaseAuth) {
    return $firebaseAuth();
  }
]);

app.run(['$state', '$rootScope', '$window', 'endpoints','$http', '$firebaseArray', '$firebaseObject',
    function($state, $rootScope, $window, endpoints, $http, $firebaseArray, $firebaseObject) {

        //$rootScope.auth = auth;
        //$rootScope.session = session;
        $rootScope.user = null;
        $rootScope.userAccount = null;

        // This is passed into the backend to authenticate the user.
        var userIdToken = null;
        // This is passed to the backend to allow token refreshes.
        var userRefreshToken = null;

        $http.defaults.headers.common['X-UETOPIA-Auth'] = null;

        var CLIENT = 'x.apps.googleusercontent.com'; // replace with your key
        var BASE;
        if($window.location.hostname == 'localhost') {
            BASE = '//localhost:8080/_ah/api';
        } else {
            BASE = 'https://ue4topia.appspot.com/_ah/api';
        }

        firebase.auth().onAuthStateChanged(function(user) {
          console.log('tokenapp.js - onAuthStateChanged');
          if (user) {
            console.log('onAuthStateChanged - user found');
            console.log(user);
            user.getToken().then(function(idToken) {
              userIdToken = idToken;
              userRefreshToken = user.refreshToken;
              $http.defaults.headers.common['X-UETOPIA-Auth'] = 'Bearer ' + userIdToken;


              $rootScope.user = user;

              checkEndpointsAuthentication();


              var ref = firebase.database().ref().child('users').child($rootScope.user.uid);
              $rootScope.userAccount = $firebaseObject(ref);

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
            endpoints.post('users', 'clientConnect', {refreshToken: $rootScope.user.refreshToken})
                .then(function(response) {
                    // DONE!
                    console.log(response);
                    if (response.refresh_token) {
                      console.log('Firebase Unauth - REFRESHING');
                      console.log(firebase.auth());

                    }
                }, function() {
                  // ERROR!
                  console.log('error');
                });
          } else {
            console.log('no userIdToken found - skipping');
          }

        };

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

        });



        configureFirebaseLoginWidget();
    }
]);
