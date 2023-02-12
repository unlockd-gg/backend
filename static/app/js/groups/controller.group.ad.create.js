var controller = angular.module('uetopiaFrontEnd.controller.group.ad.create', []);

controller.controller('uetopiaFrontEnd.controller.group.ad.create', ['$scope', 'endpoints', '$state','$mdDialog','$stateParams',
    function groupAdCreateCtl($scope, endpoints, $state, $mdDialog, $stateParams) {

      $scope.ad = {};
      $scope.game_modes =  [];
      $scope.loaded_game_modes = false;
      //$scope.ad.gameKeyId = $stateParams.gameKeyId;
      $scope.selectedIndex = null;
      $scope.selectedGameMode = null;
      $scope.game = null;
      $scope.highBid = null;

      // the group game is here:  $stateParams.groupGameKeyId
      // NOTE this is not a gameKey.  It is a groupGameKey

      // Load the game from endpoints
      endpoints.post('games', 'get', {'groupGameKeyId': $stateParams.groupGameKeyId}).then(function(resp) {
          console.log(resp);
              $scope.game = resp;
              // Load the gameModes from endpoints for this game
              endpoints.post('games', 'gameModesCollectionGetPage', {'gameKeyId': resp.key_id}).then(function(resp) {
                  console.log(resp);
                      if (resp.game_modes ){
                        $scope.game_modes = resp.game_modes;
                        $scope.loaded_game_modes = true;
                      } else {
                        $scope.game_modes =  [];
                        $scope.loaded_game_modes = true;
                      }
                    });


            });



      //Handle the user selection
      $scope.selectGameMode = function () {
        if ($scope.selectedIndex !== undefined) {
          console.log("You have selected: Item " + $scope.selectedIndex);
          $scope.selectedGameMode = $scope.game_modes[$scope.selectedIndex];

          // get the high bid from endpoints
          endpoints.post('ads', 'adGetHighBid', {'key_id': $scope.selectedGameMode.key_id}).then(function(resp) {
              console.log(resp);
                  if (resp.bid_per_impression ){
                    $scope.highBid = resp.bid_per_impression;
                  } else {
                    $scope.highBid = $scope.selectedGameMode.ads_minimum_bid_per_impression;
                  }
                });


          return $scope.selectedItem;
          //return "You have selected: Item " + $scope.selectedItem;
        } else {
          //
          console.log("Please select an item");
          return "Please select an item";
        }
      };



      // Save updates

    	$scope.submitAdd = function() {
        console.log($scope.selectedGameMode.key_id);
        $scope.ad.groupKeyId = $stateParams.key_id;
        $scope.ad.gameModeKeyId = $scope.selectedGameMode.key_id;
        $scope.ad.groupGameKeyId =  $stateParams.groupGameKeyId;
    		endpoints.post('ads', 'create', $scope.ad).then(function(resp) {
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
