var controller = angular.module('uetopiaFrontEnd.controller.developer.game.offers', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.offers', ['$scope','$state','$stateParams','endpoints','$mdDialog',
    function DevGameCtrl($scope, $state, $stateParams, endpoints, $mdDialog) {

      $scope.offers = [];
      $scope.gameKeyId = $stateParams.gameKeyId;

      $scope.loaded_game_offers = false;

      endpoints.post('offers', 'offerCollectionGetPage', {'gameKeyId': $stateParams.gameKeyId}).then(function(resp) {
          console.log(resp);
              if (resp.offers ){
                $scope.offers = resp.offers;
                $scope.loaded_game_offers = true;
              } else {
                $scope.offers =  [];
                $scope.loaded_game_offers = true;
              }
            });

    }
])
