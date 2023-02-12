var controller = angular.module('uetopiaFrontEnd.controller.416.token.expose', []);

controller.controller('uetopiaFrontEnd.controller.416.token.expose', ['$scope','$state', '$stateParams', 'endpoints','$rootScope','$interval', '$timeout', '$window', '$location',
    function clientList($scope, $state, $stateParams, endpoints, $rootScope, $interval, $timeout, $window, $location) {

      var token_retieved = false;

      console.log('token login state');

      $scope.message = "Logging you in. ";

      // Get the URL param "state" - we need to send it back in the redirect.
      // Only do it if it's not already set
      if (!$rootScope.UEState)
      {
        var qs = $location.search();
        console.log(qs.state);
        $rootScope.UEState = qs.state;
      }


      // first check but don't redirect right away.
      if($rootScope.user){
        //console.log('user is logged in');
        if (token_retieved == false) {


          //TODO get the gameKeyId so we can display the customized login screen

          // get the login token from the backend

          endpoints.post('users', 'exposeToken', {}).then(function(resp) {
                console.log(resp);
                if (resp.agreed_with_terms)
                {
                  console.log('agreed with terms')
                  $rootScope.title = resp.custom_title;
                  token_retieved = true;
                  $scope.message = "Good to go.  Have fun!";
                  $window.location.href = "/4.16/t_login_complete_R?state=" + $rootScope.UEState+ "&access_token=" + resp.access_token;
                }
                else {
                  console.log('not agreed with terms')
                  // TODO forward to special terms page
                  $state.go('agreement');
                }
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
                  if (resp.agreed_with_terms)
                  {
                    console.log('agreed with terms')
                    $rootScope.title = resp.custom_title;
                    token_retieved = true;
                    $scope.message = "Good to go.  Have fun!";
                    $window.location.href = "/4.16/t_login_complete_R?state=" + $rootScope.UEState + "&access_token=" + resp.access_token;
                  }
                  else {
                    console.log('not agreed with terms')
                    // TODO forward to special terms page
                    $state.go('agreement');
                  }
              });
          }
      	}
      }

      $interval( this.getTokenInterval, 7000);
      //$timeout( this.getTokenInterval, 13000);

    }
])
