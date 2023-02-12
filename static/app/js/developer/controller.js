var controller = angular.module('uetopiaFrontEnd.controller.developer', []);

controller.controller('uetopiaFrontEnd.controller.developer', ['$scope', 'endpoints',
    function developerCtl($scope, endpoints) {

      $scope.loaded = false;

      $scope.games = [];

      $scope.viewDocumentation = false;
      $scope.toggleViewDocumentation = function () {
        $scope.viewDocumentation = !$scope.viewDocumentation;
      }

      endpoints.post('games', 'gamesCollectionDeveloperGetPage', {}).then(function(resp) {
              if (resp.games ){
                $scope.games = resp.games;
                $scope.loaded = true;
              } else {
                $scope.games =  [];
                $scope.loaded = true;
              }
            });

    }
]);
