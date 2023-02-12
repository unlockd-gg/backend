var controller = angular.module('uetopiaFrontEnd.controller.admin.user.detail', []);

controller.controller('uetopiaFrontEnd.controller.admin.user.detail', ['$scope','$state','$stateParams','endpoints',
    function AdminUserCtrl($scope, $state, $stateParams, endpoints) {

      console.log($stateParams.key_id);
      endpoints.post('users', 'usersGet', {key_id: $stateParams.key_id}).then(function(resp) {
            console.log(resp.response_message);
            $scope.thisuser = resp;
        });



        $scope.submit = function(form, thisuser) {
          if (!form.$invalid) {
            //console.log($scope.selectedrole.key_id);
            endpoints.post('users', 'usersUpdate', {'key_id': $stateParams.key_id,
                                                  'title': thisuser.title,
                                                  'description': thisuser.description,
                                                  'googleUser': thisuser.googleUser,
                                                  'currencyBalance': thisuser.currencyBalance,
                                                  //'roleKeyId': user.roleKeyId,
                                                }).then(function(resp) {
                console.log(resp.response_message);

                  form.$setPristine();

                  //chatService.append({textMessage: resp.response_message });
                  $state.go('home');
              });
          }
        };

        $scope.remove = function(game) {
            endpoints.post('users', 'userDelete', {key_id: user.key_id}).then(function(resp) {
                console.log(resp.response_message);

                  //chatService.append({textMessage: resp.response_message });
                  $state.go('home');
              });



          //return promise;
        };
    }
])
