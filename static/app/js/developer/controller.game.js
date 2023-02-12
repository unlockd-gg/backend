var controller = angular.module('uetopiaFrontEnd.controller.developer.game', []);

controller.controller('uetopiaFrontEnd.controller.developer.game', ['$scope','$state','$stateParams','endpoints','$mdDialog',
    function DevGameCtrl($scope, $state, $stateParams, endpoints, $mdDialog) {

      $scope.serverclusters = [];
      $scope.transactions = [];

      $scope.loaded_game = false;
      $scope.loaded_game_modes = false;
      $scope.loaded_game_levels = false;
      $scope.loaded_game_server_clusters = false;
      $scope.loaded_game_vendor_types = false;
      $scope.loaded_game_data = false;

      $scope.viewEditForm = false;
      $scope.toggleViewEditForm = function () {
        $scope.viewEditForm = !$scope.viewEditForm;
      }

      $scope.viewCredentials= false;
      $scope.toggleViewCredentials = function () {
        $scope.viewCredentials = !$scope.viewCredentials;
      }

      $scope.viewTransactions= false;
      $scope.toggleViewTransactions = function () {
        $scope.viewTransactions = !$scope.viewTransactions;
      }

      $scope.viewData = false;
      $scope.toggleViewData= function () {
        $scope.viewData = !$scope.viewData ;
      }

      $scope.viewVendorTypes = false;
      $scope.toggleViewVendorTypes = function () {
        $scope.viewVendorTypes = !$scope.viewVendorTypes ;
      }



      endpoints.post('servers', 'serverClusterCollectionGetPage', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.server_clusters ){
                $scope.serverclusters = resp.server_clusters;
                $scope.loaded_game_server_clusters = true;
              } else {
                $scope.serverclusters =  [];
                $scope.loaded_game_server_clusters = true;
              }
            });

      endpoints.post('games', 'gameModesCollectionGetPage', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.game_modes ){
                $scope.game_modes = resp.game_modes;
                $scope.loaded_game_modes = true;
              } else {
                $scope.game_modes =  [];
                $scope.loaded_game_modes = true;
              }
            });

      endpoints.post('games', 'gameLevelsCollectionDeveloperGetPage', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.game_levels ){
                $scope.game_levels = resp.game_levels;
                $scope.loaded_game_levels = true;
              } else {
                $scope.game_levels =  [];
                $scope.loaded_game_levels = true;
              }
            });

      endpoints.post('transactions', 'transactionCollectionGetPage', {'gameKeyId': $stateParams.key_id, 'transactionType': 'game'}).then(function(resp) {
          console.log(resp);
              if (resp.transactions ){
                $scope.transactions = resp.transactions;
              } else {
                $scope.transactions =  [];
              }
            });

      endpoints.post('vendors', 'typesCollectionGetPage', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.vendor_types ){
                $scope.vendor_types = resp.vendor_types;
                $scope.loaded_game_vendor_types = true;
              } else {
                $scope.vendor_types =  [];
                $scope.loaded_game_vendor_types = true;
              }
            });

      endpoints.post('games', 'gameDataCollectionDeveloperGetPage', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.game_data ){
                $scope.game_data = resp.game_data;
                $scope.loaded_game_data = true;
              } else {
                $scope.game_data =  [];
                $scope.loaded_game_data = true;
              }
            });

      console.log($stateParams.key_id);
      endpoints.post('games', 'get', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.game = resp;
            $scope.loaded_game = true;
        });

        $scope.submit = function(form, game) {
          if (!form.$invalid) {
            $scope.game.key_id = $stateParams.key_id;
            $scope.game.developerRequest = true;
            $scope.game.adminRequest = false;
            endpoints.post('games', 'update', $scope.game).then(function(resp) {
                console.log(resp.response_message);
                  $scope.game = resp;
                  form.$setPristine();
                  console.log(resp);
                  //chatService.append({textMessage: resp.response_message });
                  $state.go('developerhome');
              });
          }
        };

        $scope.remove = function(game) {
          endpoints.post('games', 'delete', {'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                //chatService.append({textMessage: resp.response_message });
                  $scope.game = resp;
                  $state.go('developerhome');
              });
          //return promise;
        };

        $scope.showClearMatchDialog = function(ev) {
          var confirm = $mdDialog.confirm()
            .title('Would you like to delete all of the matches and match related information?')
            .textContent('This is not undoable.')
            .ariaLabel('Lucky day')
            .targetEvent(ev)
            .ok('Yes.  Delete all matches.')
            .cancel('Nevermind');

          $mdDialog.show(confirm).then(function() {
            endpoints.post('games', 'gameClearMatches', {'key_id': $stateParams.key_id,
                                                  }).then(function(resp) {
                console.log(resp.response_message);

                  $mdDialog.show(
                    $mdDialog.alert()
                        .parent(angular.element(document.querySelector('#popupContainer')))
                        .clickOutsideToClose(true)
                        .title('Match Deletion Results')
                        .textContent(resp.response_message)
                        .ariaLabel('Alert Dialog Demo')
                        .ok('Got it!')
                        .targetEvent(ev)
                  );
                  console.log(resp);
              });

          }, function() {
            $scope.status = 'You cancel.';
          });
        };
    }
])
