var controller = angular.module('uetopiaFrontEnd.controller.developer.server.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.server.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devServerCreateCtl($scope, endpoints, $state, $stateParams) {

      var gameKeyId = parseInt($stateParams.gameKeyId);
      var serverClusterKeyId = $stateParams.serverClusterKeyId;
      $scope.servertags = [];

      endpoints.post('games', 'gameLevelsCollectionDeveloperGetPage', {'gameKeyId': gameKeyId}).then(function(resp) {
          console.log(resp);
              if (resp.game_levels ){
                $scope.game_levels = resp.game_levels;
              } else {
                $scope.game_levels =  [];
              }
            });

    	$scope.submitAdd = function() {
        $scope.server.gameKeyId = gameKeyId;
        $scope.server.serverClusterKeyId = serverClusterKeyId;
        $scope.server.gameLevelKeyId = $scope.targetgamelevel;
        $scope.server.requireBadgeTags = $scope.servertags;
        endpoints.post('servers', 'create', $scope.server).then(function(resp) {
          //chatService.append({textMessage: resp.response_message });
            	$state.go('developerserverclusterdetail', {'gameKeyId':$stateParams.gameKeyId, 'key_id': $stateParams.serverClusterKeyId});
        	});
    	}
    }
]);
