var controller = angular.module('uetopiaFrontEnd.controller.developer.game.player.detail', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.player.detail', ['$scope','$state','$stateParams','endpoints','$mdDialog',
    function DevGameCtrl($scope, $state, $stateParams, endpoints, $mdDialog) {

      $scope.game_player = {};
      $scope.characters = [];
      $scope.snapshots = [];
      $scope.gameKeyId = $stateParams.gameKeyId;
      $scope.gamePlayerKeyId = $stateParams.gamePlayerKeyId;

      $scope.show_characters = false;
      $scope.show_snapshots = false;

      $scope.loaded_game_player = false;
      $scope.loaded_game = false;
      $scope.loaded_game_characters = false;
      $scope.loaded_game_player_snapshots = false;

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



      // First get the game player.
      endpoints.post('games', 'gamePlayerGet', {'gamePlayerKeyId': $stateParams.gamePlayerKeyId, 'developer': true, 'key_id': $stateParams.gameKeyId}).then(function(resp) {
          console.log(resp);
                $scope.game_player =  resp;
                $scope.loaded_game_player = true;
                $scope.gamePlayerKeyId = resp.key_id;

                // get the game.  We need to know if characters are enabled
                console.log($stateParams.gameKeyId);
                endpoints.post('games', 'get', {'key_id': $stateParams.gameKeyId }).then(function(resp) {
                    console.log(resp);
                      $scope.game = resp;
                      $scope.loaded_game = true;

                      if ($scope.game.characters_enabled){
                        console.log('characters_enabled');
                        $scope.show_characters = true;

                        // Need the userkey for this one!
                        endpoints.post('characters', 'collectionGetPage', {'gameKeyId': $stateParams.gameKeyId, 'developerRequest': true, 'userKeyId':$scope.game_player.userKeyId }).then(function(resp) {
                            console.log(resp);
                                if (resp.characters ){
                                  $scope.characters = resp.characters;
                                  $scope.loaded_game_characters = true;
                                } else {
                                  $scope.characters =  [];
                                  $scope.loaded_game_characters = true;
                                }
                              }); // end get characters



                      } else {
                        console.log('characters NOT enabled');
                        $scope.show_snapshots = true;

                        endpoints.post('games', 'gamePlayerSnapshotCollectionGetPage', {'gamePlayerKeyId': $stateParams.gamePlayerKeyId, 'gameKeyId': $scope.gameKeyId}).then(function(resp) {
                            console.log(resp);
                                if (resp.snapshots ){
                                  $scope.snapshots = resp.snapshots;
                                  $scope.loaded_game_player_snapshots = true;
                                } else {
                                  $scope.snapshots =  [];
                                  $scope.loaded_game_player_snapshots = true;
                                }
                              }); // end get characters





                      } // end if characters enabled

                  }); // end get game

            });  // end get game player

            $scope.submit = function(form, game_player) {
              if (!form.$invalid) {
                $scope.game_player.key_id = $stateParams.gameKeyId;
                $scope.game_player.gamePlayerKeyId = $stateParams.gamePlayerKeyId;
                $scope.game_player.developer = true;
                endpoints.post('games', 'gamePlayerUpdate', $scope.game_player).then(function(resp) {
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
