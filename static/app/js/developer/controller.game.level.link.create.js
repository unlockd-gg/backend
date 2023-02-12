var controller = angular.module('uetopiaFrontEnd.controller.developer.game.level.link.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.level.link.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devGameLevelCreateCtl($scope, endpoints, $state, $stateParams) {

      var gameLevelKeyId = parseInt($stateParams.gameLevelKeyId);

    	$scope.submitAdd = function() {
        $scope.gamelevellink.gameLevelKeyId = gameLevelKeyId;
    		endpoints.post('games', 'gameLevelLinkCreate', $scope.gamelevellink).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
              $state.go('developergameleveldetail', {gameKeyId: $stateParams.gameKeyId, key_id: $stateParams.gameLevelKeyId });
        	});
    	}
    }
]);
