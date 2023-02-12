var controller = angular.module('uetopiaFrontEnd.controller.developer.gameMode', []);

controller.controller('uetopiaFrontEnd.controller.developer.gameMode', ['$scope','$state','$stateParams','endpoints',
    function DevGameCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_game_mode = false;
      $scope.loaded_ads = false;
      $scope.ads = [];
      $scope.gamemodetags = [];

      console.log($stateParams.key_id);
      endpoints.post('games', 'gameModeGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.gamemode = resp;
            if (resp.requireBadgeTags)
            {
              console.log('found tags');
              $scope.gamemodetags = resp.requireBadgeTags;
            }
            else
            {
              console.log('did not find tags');
              $scope.gamemodetags = [];
            }

            $scope.loaded_game_mode = true;
        });


        // Get the ads for this game
        endpoints.post('ads', 'adsCollectionGetPage', {'gameModeKeyId': $stateParams.key_id}).then(function(resp) {
            console.log(resp.response_message);
              $scope.ads = resp.ads;
              $scope.loaded_ads = true;
          });

        $scope.submit = function(form, gamemode) {
          if (!form.$invalid) {
            $scope.gamemode.key_id = $stateParams.key_id;
            $scope.gamemode.requireBadgeTags = $scope.gamemodetags;
            endpoints.post('games', 'gameModeUpdate', $scope.gamemode
                                                        ).then(function(resp) {
                console.log(resp.response_message);
                  $scope.gamemode = resp;
                  //chatService.append({textMessage: resp.response_message });
                  //form.$setPristine();
                  console.log(resp);
                  $state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
              });
          }
        };

        $scope.remove = function(server) {
          endpoints.post('games', 'gameModeDelete',{'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                  $scope.gamemode = resp;
                  //chatService.append({textMessage: resp.response_message });
                  $state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
              });



          //return promise;
        };
    }
])
