var controller = angular.module('uetopiaFrontEnd.controller.admin.users', []);

controller.controller('uetopiaFrontEnd.controller.admin.users', ['$scope', 'endpoints', '$state',
    function adminUsersCtl($scope, endpoints, $state) {

      console.log('adminUsersCtl');

      $scope.users = [];

      endpoints.post('users', 'userCollectionGet')
            .then(function(response) {
                // DONE!
                console.log(response);
                if (response.response_message === "Firebase Unauth.") {
                  console.log('Firebase Unauth');

                  //auth.refreshtoken();
                } else {
                  $scope.users = response.users;
                }
                //$state.go('home');
            }, function() {
              // ERROR!
              console.log('error');
            });



    }
]);
