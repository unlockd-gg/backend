var controller = angular.module('uetopiaFrontEnd.controller.admin.games', []);

controller.controller('uetopiaFrontEnd.controller.admin.games', ['$scope','endpoints',
    function adminGamesCtl($scope, endpoints) {

      $scope.games = [];

      endpoints.post('games', 'gamesCollectionGetPage', {}).then(function(resp) {
              if (resp.games ){
                $scope.games = resp.games;
              } else {
                $scope.games =  [];
              }
            });


    }
]);
