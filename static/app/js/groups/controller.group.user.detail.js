var controller = angular.module('uetopiaFrontEnd.controller.group.user.detail', []);

controller.controller('uetopiaFrontEnd.controller.group.user.detail', ['$scope', 'endpoints', '$state','$mdDialog','$stateParams',
    function groupUserDetailCtl($scope, endpoints, $state, $mdDialog, $stateParams) {

      // load the initial data
      console.log($stateParams.key_id);
      endpoints.post('groups', 'groupMemberGet', {'key_id': $stateParams.userKeyId, 'groupKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.groupUser = resp;
        });

      // load the roles for the dropdown
      console.log('loading roles from endpoints');
      endpoints.post('groups', 'groupRoleCollectionGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.groupRoles = resp.roles;
        });


      $scope.showTipDialog = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.prompt()
          .title('How much CRED would you like to donate to this user?')
          .textContent('This non-refundable.  And the funds are coming out of the Group wallet.')
          .placeholder('10')
          .ariaLabel('Donate Amount')
          .initialValue('10')
          .targetEvent(ev)
          .ok('Donate')
          .cancel('Nevermind');

        $mdDialog.show(confirm).then(function(result) {
          endpoints.post('transactions', 'userTip', {'key_id': $stateParams.userKeyId,
                                                'amountInt': parseInt(result),
                                                'fromGroup': true,
                                                'fromGroupKeyId': $stateParams.key_id
                                                }).then(function(resp) {
              console.log(resp.response_message);

              if (resp.response_successful == false) {
                $mdDialog.show(
                  $mdDialog.alert()
                      .parent(angular.element(document.querySelector('#popupContainer')))
                      .clickOutsideToClose(true)
                      .title('Error')
                      .textContent(resp.response_message)
                      .ariaLabel('Alert Dialog Demo')
                      .ok('Got it!')
                      .targetEvent(ev)
                );
              }
                console.log(resp);
            });
        }, function() {
          $scope.status = 'You didn\'t donate.';
        });
      };

      // Save updates


    	$scope.submitAdd = function() {
        $scope.groupUser.key_id = $stateParams.userKeyId;
        $scope.groupUser.groupKeyId = $stateParams.key_id;
    		endpoints.post('groups', 'groupMemberupdate', $scope.groupUser).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
              if (resp.response_successful) {
                $state.go('groups');
              } else {
                $mdDialog.show(
                  $mdDialog.alert()
                    .parent(angular.element(document.querySelector('#popupContainer')))
                    .clickOutsideToClose(true)
                    .title('There was a problem')
                    .textContent(resp.response_message)
                    .ariaLabel('Alert Dialog Demo')
                    .ok('Got it!')
                    //.targetEvent(ev)
                );
              }


        	});
    	}

      $scope.submitRemove= function() {
        $scope.groupUser.key_id = $stateParams.userKeyId;
        $scope.groupUser.groupKeyId = $stateParams.key_id;
    		endpoints.post('groups', 'groupMemberRemove', $scope.groupUser).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
              if (resp.response_successful) {
                $state.go('groups');
              } else {
                $mdDialog.show(
                  $mdDialog.alert()
                    .parent(angular.element(document.querySelector('#popupContainer')))
                    .clickOutsideToClose(true)
                    .title('There was a problem')
                    .textContent(resp.response_message)
                    .ariaLabel('Alert Dialog Demo')
                    .ok('Got it!')
                    //.targetEvent(ev)
                );
              }


        	});
    	}
    }
]);
