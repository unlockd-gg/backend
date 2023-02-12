var controller = angular.module('uetopiaFrontEnd.controller.developer.game.consignment.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.consignment.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devGameConsignmentCreateCtl($scope, endpoints, $state, $stateParams) {

      var gameKeyId = parseInt($stateParams.gameKeyId);

      $scope.gameconsignment= {};

      $scope.gameKeyId = $stateParams.gameKeyId;



    	$scope.submitAdd = function(form) {
          if (!form.$invalid) {
            $scope.gameconsignment.gameKeyId = $stateParams.gameKeyId;
        		endpoints.post('consignments', 'create', $scope.gameconsignment).then(function(resp) {
                  //chatService.append({textMessage: resp.response_message });
                	$state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
            	});
            }


    	}
    }
]);
