var controller = angular.module('uetopiaFrontEnd.controller.developer.game.offer.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.offer.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devGameOfferCreateCtl($scope, endpoints, $state, $stateParams) {

      var gameKeyId = parseInt($stateParams.gameKeyId);

      $scope.gameoffer = {};
      $scope.gameoffertags = [];
      $scope.gameKeyId = $stateParams.gameKeyId;
      $scope.gameoffer.gameKeyId = $stateParams.gameKeyId;


    	$scope.submitAdd = function(form) {
        if ($scope.gameoffertags.length == 0)
        {
          alert('at least one tag is required.');
        }
        else
        {
          if (!form.$invalid) {
            $scope.gameoffer.tags = $scope.gameoffertags;
        		endpoints.post('offers', 'create', $scope.gameoffer).then(function(resp) {
                  //chatService.append({textMessage: resp.response_message });
                	$state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
            	});
            }
        }

    	}
    }
]);
