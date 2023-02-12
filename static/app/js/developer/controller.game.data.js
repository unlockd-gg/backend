var controller = angular.module('uetopiaFrontEnd.controller.developer.gameData', []);

controller.controller('uetopiaFrontEnd.controller.developer.gameData', ['$scope','$state','$stateParams','endpoints',
    function DevGameCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_game_data = false;

      console.log($stateParams.key_id);
      endpoints.post('games', 'gameDataGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.gamedata = resp;
            $scope.loaded_game_data = true;
        });

        $scope.submit = function(form, gamemode) {
          if (!form.$invalid) {
            $scope.gamedata.key_id = $stateParams.key_id;
            endpoints.post('games', 'gameDataUpdate', $scope.gamedata
                                                        ).then(function(resp) {
                console.log(resp.response_message);
                  $scope.gamedata = resp;
                  //chatService.append({textMessage: resp.response_message });
                  //form.$setPristine();
                  console.log(resp);
                  $state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
              });
          }
        };

        $scope.remove = function(server) {
          endpoints.post('games', 'gameDataDelete',{'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                  $scope.gamedata= resp;
                  //chatService.append({textMessage: resp.response_message });
                  $state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
              });



          //return promise;
        };
    }
])
