var controller = angular.module('uetopiaFrontEnd.controller.developer.game.mode.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.mode.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devGameModeCreateCtl($scope, endpoints, $state, $stateParams) {

      var gameKeyId = parseInt($stateParams.gameKeyId);

      $scope.gamemodetags = [];

    	$scope.submitAdd = function() {
        $scope.gamemode.key_id = gameKeyId;
        $scope.gamemode.requireBadgeTags = $scope.gamemodetags;
    		endpoints.post('games', 'gameModeCreate', $scope.gamemode).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
            	$state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
        	});
    	}
    }
]);
