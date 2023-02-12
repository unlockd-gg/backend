var controller = angular.module('uetopiaFrontEnd.controller.developer.game.level.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.level.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devGameLevelCreateCtl($scope, endpoints, $state, $stateParams) {

      var gameKeyId = parseInt($stateParams.gameKeyId);

    	$scope.submitAdd = function() {
        $scope.gamelevel.key_id = gameKeyId;
    		endpoints.post('games', 'gameLevelCreate', $scope.gamelevel).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
              $state.go('developergamedetail', {key_id: gameKeyId });
        	});
    	}
    }
]);
