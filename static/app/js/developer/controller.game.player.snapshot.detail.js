var controller = angular.module('uetopiaFrontEnd.controller.developer.game.player.snapshot.detail', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.player.snapshot.detail', ['$scope','$state','$stateParams','endpoints','$mdDialog',
    function DevGameCtrl($scope, $state, $stateParams, endpoints, $mdDialog) {

      $scope.game_player_snapshot = {};

      $scope.loaded_game_player_snapshot = false;

      $scope.viewAbilities = false;
      $scope.toggleViewAbilities = function () {
        $scope.viewAbilities = !$scope.viewAbilities ;
      }

      $scope.viewEquipment = false;
      $scope.toggleViewEquipment = function () {
        $scope.viewEquipment = !$scope.viewEquipment ;
      }

      $scope.viewInterface = false;
      $scope.toggleViewInterface = function () {
        $scope.viewInterface = !$scope.viewInterface ;
      }

      $scope.viewInventory = false;
      $scope.toggleViewInventory = function () {
        $scope.viewInventory = !$scope.viewInventory ;
      }

      $scope.viewCrafting = false;
      $scope.toggleViewCrafting = function () {
        $scope.viewCrafting = !$scope.viewCrafting ;
      }

      $scope.viewRecipes = false;
      $scope.toggleViewRecipes = function () {
        $scope.viewRecipes = !$scope.viewRecipes ;
      }

      $scope.viewCharacter = false;
      $scope.toggleViewCharacter = function () {
        $scope.viewCharacter = !$scope.viewCharacter ;
      }


      // First get the game player.
      endpoints.post('games', 'gamePlayerSnapshotGet', {'key_id': $stateParams.gamePlayerSnapshotKeyId, 'developerRequest': true, 'gameKeyId': $stateParams.gameKeyId}).then(function(resp) {
          console.log(resp);
                $scope.game_player_snapshot =  resp;
                $scope.loaded_game_player_snapshot = true;

            });  // end get game player snapshot


    }
])
