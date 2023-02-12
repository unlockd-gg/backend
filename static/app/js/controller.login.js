var controller = angular.module('uetopiaFrontEnd.controller.login', []);

controller.controller('uetopiaFrontEnd.controller.login', ['$scope','$state', 'auth', '$stateParams', 'fbUserProfile', '$interval','currentAuth', '$timeout',
    function clientList($scope, $state, auth, $stateParams, fbUserProfile, $interval, currentAuth, $timeout) {

      var initialRedirectRequired = true;
      var promise;
      $scope.loginClicked = false;

      $scope.checkForCompleteAndRedirect = function() {
        if(auth.isLoggedIn()){
          console.log('user is logged in');

            if ($stateParams.toWhere != null) {
              $interval.cancel(promise);
              $state.go($stateParams.toWhere.name);
            } else {
              $interval.cancel(promise);
              $state.go('home');
            }





            //$state.go('home');


      	}
      }
      promise = $interval( $scope.checkForCompleteAndRedirect, 2000);



      $scope.doLogin = function() {

          // login with Google
          $scope.loginClicked = true;
            auth.logIn()
          //    console.log("Firebase: Signed in as:", firebaseUser.user.uid);
          //    console.log('test');
          //    accessToken = firebaseUser.credential.accessToken;
          //    idToken = firebaseUser.credential.idToken;


          //    ifLogin();
          //  }).catch(function(error) {
          //    console.log("Authentication failed:", error);
          //  });
        };



    }
])
