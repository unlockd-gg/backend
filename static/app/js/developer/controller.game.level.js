var controller = angular.module('uetopiaFrontEnd.controller.developer.gameLevel', []);

controller.controller('uetopiaFrontEnd.controller.developer.gameLevel', ['$scope','$state','$stateParams','endpoints',
    function DevGameCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_game_level = false;
      $scope.loaded_game_level_links = false;

      console.log($stateParams.key_id);
      endpoints.post('games', 'gameLevelGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.gamelevel = resp;
            $scope.loaded_game_level = true;

            // there are some potentially hidden fields on the page.  Set the defaults if they don't exist.
            if (!$scope.gamelevel.shard_count_maximum)
            {
              $scope.gamelevel.shard_count_maximum = 1;
            }
            if (!$scope.gamelevel.sharded_player_capacity_maximum)
            {
              $scope.gamelevel.sharded_player_capacity_maximum = 1;
            }
            if (!$scope.gamelevel.sharded_player_capacity_threshold)
            {
              $scope.gamelevel.sharded_player_capacity_threshold = 1;
            }


        });

      $scope.returnLinkDefined = false;

      endpoints.post('games', 'gameLevelLinksCollectionDeveloperGetPage', {'gameLevelKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.game_level_links ){
                $scope.game_level_links = resp.game_level_links;
                for(var i= 0; i < $scope.game_level_links.length; i++){
                  if ($scope.game_level_links[i].isReturnLink) {
                    $scope.returnLinkDefined =true;
                  }
                }

              } else {
                $scope.game_level_links =  [];
              }
              $scope.loaded_game_level_links = true;
            });

        $scope.submit = function(form, gamelevel) {
          if (!form.$invalid) {
            $scope.gamelevel.key_id = $stateParams.key_id;
            endpoints.post('games', 'gameLevelUpdate', $scope.gamelevel
                                                        ).then(function(resp) {
                console.log(resp.response_message);
                  $scope.gamelevel = resp;
                  //chatService.append({textMessage: resp.response_message });
                  //form.$setPristine();
                  console.log(resp);
                  $state.go('developergamedetail', {key_id: $stateParams.key_id });
              });
          }
        };

        $scope.remove = function(gamelevel) {
          endpoints.post('games', 'gameLevelDelete',{'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                  $scope.gamelevel = resp;
                  //chatService.append({textMessage: resp.response_message });
                  $state.go('developergamedetail', {key_id: $stateParams.key_id });
              });



          //return promise;
        };
    }
])
