var controller = angular.module('uetopiaFrontEnd.controller.developer.game.data.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.data.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devGameDateCreateCtl($scope, endpoints, $state, $stateParams) {

      var gameKeyId = parseInt($stateParams.gameKeyId);

    	$scope.submitAdd = function() {
        $scope.gamedata.gameKeyId = gameKeyId;
    		endpoints.post('games', 'gameDataCreate', $scope.gamedata).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
            	$state.go('developergamedetail', {key_id: gameKeyId });
        	});
    	}
    }
]);
