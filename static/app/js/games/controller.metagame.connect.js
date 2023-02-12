var controller = angular.module('uetopiaFrontEnd.controller.game.metagame.connect', []);

controller.controller('uetopiaFrontEnd.controller.game.metagame.connect', ['$rootScope', '$scope','$state','$stateParams','endpoints',
    function GameCtrl($rootScope, $scope, $state, $stateParams, endpoints) {

      $scope.gameplayer = [];
      $scope.loaded = false;

    // look up from ENDPOINTS
    endpoints.post('games', 'metaGamePlayerConnect', {'key_id': $stateParams.key_id}).then(function(resp) {
        console.log(resp);
              $scope.gameplayer =  resp;
              $scope.loaded = true;
            });  // end get game player


    }
])
