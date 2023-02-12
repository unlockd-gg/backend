var controller = angular.module('uetopiaFrontEnd.controller.tournament.create', []);

controller.controller('uetopiaFrontEnd.controller.tournament.create', ['$scope', 'endpoints', '$state','$mdDialog', '$stateParams',
    function groupCreateCtl($scope, endpoints, $state, $mdDialog, $stateParams) {

      // get this user's group membership collection
      // We need to know which groups this user has the "create tournaments" permission
      endpoints.post('groups', 'groupMemberCollection', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.group_users ){
                $scope.group_users = resp.group_users;
              } else {
                $scope.group_users =  [];
              }
            });

      // get the game's modes.
      endpoints.post('games', 'gameModesCollectionGetPage', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.game_modes ){
                $scope.game_modes = resp.game_modes;
              } else {
                $scope.game_modes =  [];
              }
            });

    	$scope.submitAdd = function() {
        $scope.tournament.gameKeyId = $stateParams.key_id;
    		endpoints.post('tournaments', 'tournamentCreate', $scope.tournament).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
              if (resp.response_successful) {
                $state.go('home');
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
