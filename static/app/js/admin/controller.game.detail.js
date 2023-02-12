var controller = angular.module('uetopiaFrontEnd.controller.admin.game', []);

controller.controller('uetopiaFrontEnd.controller.admin.game', ['$scope','$state','$stateParams','endpoints',
    function GameCtrl($scope, $state, $stateParams, endpoints) {

      $scope.servers = [];
      $scope.gameplayer = [];
      $scope.editGame = false;

      $scope.toggleGameEdit = function() {
        $scope.editGame = !$scope.editGame;
    };


    endpoints.post('servers', 'serversCollectionGetPage', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
        console.log(resp.response_message);
          $scope.servers = resp.servers;
      });

      endpoints.post('games', 'gameModesCollectionGetPage', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.game_modes ){
                $scope.game_modes = resp.game_modes;
              } else {
                $scope.game_modes =  [];
              }
            });

      endpoints.post('games', 'gameLevelsCollectionDeveloperGetPage', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.game_levels ){
                $scope.game_levels = resp.game_levels;
              } else {
                $scope.game_levels =  [];
              }
            });


      console.log($stateParams.key_id);
      endpoints.post('games', 'get', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.game = resp;
        });

        $scope.submit = function(form, game) {
          if (!form.$invalid) {
            game.key_id = $stateParams.key_id;
            game.adminRequest = true;
            endpoints.post('games', 'update', game).then(function(resp) {
                console.log(resp.response_message);
                  $scope.game = resp;
                  //chatService.append({textMessage: resp.response_message });
                  form.$setPristine();
                  console.log(resp);
                  $state.go('home');
              });
          }
        };

        $scope.remove = function(server) {
          endpoints.post('games', 'delete',{'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                  //$scope.gamemode = resp;
                  //chatService.append({textMessage: resp.response_message });
                  $state.go('home');
              });



          //return promise;
        };

    }
])
