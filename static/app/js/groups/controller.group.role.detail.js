var controller = angular.module('uetopiaFrontEnd.controller.group.role.detail', []);

controller.controller('uetopiaFrontEnd.controller.group.role.detail', ['$scope', 'endpoints', '$state','$mdDialog','$stateParams',
    function groupRoleDetailCtl($scope, endpoints, $state, $mdDialog, $stateParams) {

      $scope.loaded = false;

      // load the initial data
      console.log($stateParams.key_id);
      console.log($stateParams.roleKeyId);

      // re-using the update form for add.  Check for "create"

      if ($stateParams.roleKeyId == 'create')
      {
        $scope.loaded = true;
        $scope.role = {};
      }
      else {
        endpoints.post('groups', 'groupRoleGet', {'key_id': $stateParams.roleKeyId, 'groupKeyId': $stateParams.key_id}).then(function(resp) {
            console.log(resp.response_message);
              $scope.role = resp;
              $scope.loaded = true;
          });
      }



      // Save updates


    	$scope.submitAdd = function() {

        // swtich 'create' to interger
        if ($stateParams.roleKeyId == 'create')
        {
          $scope.role.key_id = 1;
        }
        else
        {
          $scope.role.key_id = $stateParams.roleKeyId;
        }

        $scope.role.groupKeyId = $stateParams.key_id;
    		endpoints.post('groups', 'groupRoleUpdate', $scope.role).then(function(resp) {
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
