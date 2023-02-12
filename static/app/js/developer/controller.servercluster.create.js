var controller = angular.module('uetopiaFrontEnd.controller.developer.servercluster.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.servercluster.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devServerClusterCreateCtl($scope, endpoints, $state, $stateParams) {
      var gameKeyId = $stateParams.gameKeyId;
      //$scope.userService = userService;
    	$scope.submitAdd = function() {
        $scope.servercluster.gameKeyId = gameKeyId;
        endpoints.post('servers', 'serverClusterCreate', $scope.servercluster).then(function(resp) {
            	$state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
              //chatService.append({textMessage: resp.response_message });
        	});
    	}
    }
]);
