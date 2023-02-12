var controller = angular.module('uetopiaFrontEnd.controller.developer.gameLevelLink', []);

controller.controller('uetopiaFrontEnd.controller.developer.gameLevelLink', ['$scope','$state','$stateParams','endpoints',
    function DevGameCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_game_level_link = false;

      console.log($stateParams.key_id);
      endpoints.post('games', 'gameLevelLinkGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.gamelevellink = resp;
            $scope.loaded_game_level_link = true;
        });

        $scope.submit = function(form, gamelevellink) {
          if (!form.$invalid) {
            $scope.gamelevellink.key_id = $stateParams.key_id;
            endpoints.post('games', 'gameLevelLinkUpdate', $scope.gamelevellink
                                                        ).then(function(resp) {
                console.log(resp.response_message);
                  $scope.gamelevellink = resp;
                  //chatService.append({textMessage: resp.response_message });
                  //form.$setPristine();
                  console.log(resp);
                  $state.go('developergameleveldetail', {gameKeyId: $stateParams.gameKeyId, key_id: $stateParams.gameLevelKeyId });
              });
          }
        };

        $scope.remove = function(gamelevellink) {
          endpoints.post('games', 'gameLevelLinkDelete',{'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                  $scope.gamelevellink = resp;
                  //chatService.append({textMessage: resp.response_message });
                  $state.go('developergameleveldetail', {gameKeyId: $stateParams.gameKeyId, key_id: $stateParams.gameLevelKeyId });
              });



          //return promise;
        };
    }
])
