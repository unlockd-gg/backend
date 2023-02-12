var controller = angular.module('uetopiaFrontEnd.controller.server.player', []);

controller.controller('uetopiaFrontEnd.controller.server.player', ['$scope','$state','$stateParams','endpoints',
    function ServerPlayerCtrl($scope, $state, $stateParams, endpoints) {

      $scope.player = {};
      $scope.player.currencyHold = 0;

        endpoints.post('servers', 'serverPlayerGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp);

                $scope.player = resp;
                if (!$scope.player.currencyHold) {
                  $scope.player.currencyHold = 0;
                }

            });

        $scope.submit = function(form, player) {
          if (!form.$invalid) {
            endpoints.post('servers', 'serverPlayStart', {'key_id': $stateParams.key_id,
                                                  'currencyHold': player.currencyHold
                                                  }).then(function(resp) {
                console.log(resp.response_message);
                  //$scope.player = resp;
                  //form.$setPristine();
                  console.log(resp);
                  $state.go('serverdetail', {gameKeyId:$stateParams.gameKeyId, clusterKeyId: $scope.player.serverClusterKeyId, key_id: $stateParams.key_id});
              });
          }
        };

    }
])
