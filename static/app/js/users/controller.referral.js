var controller = angular.module('uetopiaFrontEnd.controller.user.referral', []);

controller.controller('uetopiaFrontEnd.controller.user.referral', ['$scope', 'endpoints', '$state', '$stateParams', '$rootScope', '$timeout',
    function adminUserInviteCtl($scope, endpoints, $state, $stateParams, $rootScope, $timeout ) {

      // example url endpoints
      // http://localhost:8080/#/user/5066549580791808/referral

      //console.log($stateParams.key_id);
      console.log($stateParams.user_key_id);

      $scope.response = {'response_message': "Checking this referral.  Please wait."};

      acceptReferral = function() {

        endpoints.post('users', 'referral', {key_id: $stateParams.key_id})
              .then(function(response) {
                  // DONE!
                  console.log(response);
                  if (response.response_successful) {
                    $scope.response = response;
                    // add the referred use as a friend too
                    endpoints.post('user_relationships', 'create', {'key_id': $stateParams.key_id,
                                                                  'friend': true}).then(function(resp) {
                          $scope.relationship = resp;

                      });



                  } else {
                    //console.log('Firebase Unauth');
                    $scope.response = response;

                  }
              }, function() {
                // ERROR!
                console.log('error');
              });


      }

      $timeout( acceptReferral, 7000);

      // Do something if logged in
      if($rootScope.user){
        console.log('user is logged in')

      } else {
        console.log('user is NOT logged in')
        //$state.go('login');
        //$state.go("login", {"programKeyId": $stateParams.program_key_id, "authCode": $stateParams.authCode});
        $scope.response = {'response_message': "There was a problem with your authentication information.  Please login first then refresh this page."};
      }

    }
]);
