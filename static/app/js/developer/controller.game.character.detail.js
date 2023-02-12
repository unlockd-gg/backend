var controller = angular.module('uetopiaFrontEnd.controller.developer.game.character.detail', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.character.detail', ['$scope','$state','$stateParams','endpoints','$mdDialog',
    function DevGameCtrl($scope, $state, $stateParams, endpoints, $mdDialog) {

      $scope.game_character= {};
      $scope.snapshots = [];
      $scope.gameKeyId = $stateParams.gameKeyId;
      $scope.gamePlayerKeyId = $stateParams.gamePlayerKeyId;
      $scope.gameCharacterKeyId = $stateParams.gameCharacterKeyId;

      $scope.loaded_game_character = false;
      $scope.loaded_game = false;
      $scope.loaded_game_character_snapshots = false;

      $scope.loaded_snapshots = false;
      $scope.snapshots = [];

      $scope.viewSnapshots = false;
      $scope.toggleViewSnapshots= function () {
        $scope.viewSnapshots = !$scope.viewSnapshots ;
      }

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

      $scope.viewCharacterCustom = false;
      $scope.toggleViewCharacterCustom = function () {
        $scope.viewCharacterCustom = !$scope.viewCharacterCustom ;
      }

      console.log($stateParams.gameCharacterKeyId);

      endpoints.post('characters', 'get', {'gameCharacterKeyId': $stateParams.gameCharacterKeyId, 'developerRequest': true  }).then(function(resp) {
          console.log(resp);
                $scope.game_character = resp;
                $scope.loaded_game_character = true;

                // Also check for snapshots
                endpoints.post('games', 'gamePlayerSnapshotCollectionGetPage', {'characterKeyId': $stateParams.gameCharacterKeyId, 'gameKeyId': $scope.gameKeyId }).then(function(resp) {
                    console.log(resp);
                          $scope.snapshots = resp.snapshots;
                          $scope.loaded_snapshots = true;

                      }); // end get snapshots


            }); // end get character



            $scope.submit = function(form, game_character) {
              if (!form.$invalid) {
                $scope.game_character.key_id = $stateParams.gameCharacterKeyId;

                endpoints.post('characters', 'update', $scope.game_character).then(function(resp) {
                    console.log(resp.response_message);
                      form.$setPristine();
                      console.log(resp);
                      //chatService.append({textMessage: resp.response_message });
                      $state.go('developerhome');
                  });
              }
            };


    }
])
