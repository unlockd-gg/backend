var controller = angular.module('uetopiaFrontEnd.controller.token.expose', []);

controller.controller('uetopiaFrontEnd.controller.token.expose', ['$scope','$state', '$stateParams', 'endpoints','$rootScope','$interval', '$timeout', '$window',
    function clientList($scope, $state, $stateParams, endpoints, $rootScope, $interval, $timeout, $window) {

      var token_retieved = false;

      console.log('token login state');

      //TODO setup interval to check

      $scope.message = "Logging you in.";

      // first check but don't redirect right away.
      if($rootScope.user){
        //console.log('user is logged in');
        if (token_retieved == false) {
          // get the login token from the backend
          endpoints.post('users', 'exposeToken', {}).then(function(resp) {
                console.log(resp);
                $rootScope.title = resp.custom_title;
                token_retieved = true;
                $scope.message = "Good to go.  Have fun!";
                $window.location = "/token_login#/?access_token=" + resp.access_token;
            });
        }
      }



      this.getTokenInterval = function() {
        if($rootScope.user){
          //console.log('user is logged in');
          if (token_retieved == false) {
            // get the login token from the backend
            endpoints.post('users', 'exposeToken', {}).then(function(resp) {
                  console.log(resp);
                  $rootScope.title = resp.custom_title;
                  token_retieved = true;
                  $scope.message = "Good to go.  Have fun!";
                  $window.location = "/token_login#/redirect/access_token/" + resp.access_token;
              });
          }
      	}
      }

      $timeout( this.getTokenInterval, 7000);
      $timeout( this.getTokenInterval, 13000);

    }
])
