var controller = angular.module('uetopiaFrontEnd.controller.developer.game.players', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.players', ['$scope','$state','$stateParams','endpoints','$mdDialog',
    function DevGameCtrl($scope, $state, $stateParams, endpoints, $mdDialog) {

      $scope.players = [];
      $scope.gameKeyId = $stateParams.gameKeyId;

      $scope.loaded_game_players = false;

      endpoints.post('games', 'gamePlayerCollectionGetPage', {'gameKeyId': $stateParams.gameKeyId}).then(function(resp) {
          console.log(resp);
              if (resp.game_players ){
                $scope.players = resp.game_players;
                $scope.loaded_game_players = true;
              } else {
                $scope.servplayerserclusters =  [];
                $scope.loaded_game_players = true;
              }
            });

    }
])
