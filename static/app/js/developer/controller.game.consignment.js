var controller = angular.module('uetopiaFrontEnd.controller.developer.game.consignment', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.consignment', ['$scope','$state','$stateParams','endpoints',
    function DevGameConsignmentCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_game_consignment = false;

      $scope.gameKeyId = $stateParams.gameKeyId;
      $scope.consignmentKeyId = $stateParams.consignmentKeyId;

      console.log($stateParams.key_id);

      endpoints.post('consignments', 'get', {'key_id': $stateParams.consignmentKeyId}).then(function(resp) {
          console.log(resp);
            $scope.gameconsignment = resp;
            $scope.loaded_game_consignment = true;
        });

        $scope.submit = function(form, gameoffer) {
            if (!form.$invalid) {
              $scope.gameconsignment.key_id = $stateParams.consignmentKeyId;
              endpoints.post('consignments', 'update', $scope.gameconsignment
                                                          ).then(function(resp) {
                  console.log(resp.response_message);
                    $scope.gameconsignment = resp;
                    //chatService.append({textMessage: resp.response_message });
                    //form.$setPristine();
                    console.log(resp);
                    $state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
                });
            }

        };

    }
])
