var controller = angular.module('uetopiaFrontEnd.controller.developer.game.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.create', ['$scope', 'endpoints', '$state',
    function devGameCreateCtl($scope, endpoints, $state) {

    	$scope.submitAdd = function() {
    		endpoints.post('games', 'create', $scope.game).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
            	$state.go('developerhome');
        	});
    	}
    }
]);
