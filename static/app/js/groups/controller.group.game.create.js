var controller = angular.module('uetopiaFrontEnd.controller.group.game.create', []);

controller.controller('uetopiaFrontEnd.controller.group.game.create', ['$scope', 'endpoints', '$state','$mdDialog','$stateParams',
    function groupGameDetailCtl($scope, endpoints, $state, $mdDialog, $stateParams) {

      $scope.groupGame = {};
      $scope.groupGame.gameKeyId = $stateParams.gameKeyId;

      // load the list of games
      console.log($stateParams.key_id);
      endpoints.post('games', 'gamesCollectionGetPage', {}).then(function(resp) {
          console.log(resp);
            $scope.allGames = resp.games;
        });


      // Save updates


    	$scope.submitAdd = function() {
        $scope.groupGame.groupKeyId = $stateParams.key_id;
    		endpoints.post('groups', 'groupGameCreate', $scope.groupGame).then(function(resp) {
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
