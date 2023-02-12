var controller = angular.module('uetopiaFrontEnd.controller.developer.game.consignments', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.consignments', ['$scope','$state','$stateParams','endpoints','$mdDialog',
    function DevGameCtrl($scope, $state, $stateParams, endpoints, $mdDialog) {

      $scope.consignments = [];
      $scope.gameKeyId = $stateParams.gameKeyId;

      $scope.loaded_game_consignments = false;

      endpoints.post('consignments', 'collectionGetPage', {'gameKeyId': $stateParams.gameKeyId}).then(function(resp) {
          console.log(resp);
              if (resp.store_item_cons ){
                $scope.consignments = resp.store_item_cons;
                $scope.loaded_game_consignments = true;
              } else {
                $scope.consignments =  [];
                $scope.loaded_game_consignments = true;
              }
            });

    }
])
