var controller = angular.module('uetopiaFrontEnd.controller.user.badge.detail', []);

controller.controller('uetopiaFrontEnd.controller.user.badge.detail', ['$scope', 'endpoints', '$state', '$stateParams',
    function userBadgeCtl($scope, endpoints, $state, $stateParams) {

      $scope.badge = {};

      $scope.loaded_badge = false;

      endpoints.post('badges', 'badgeGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp);

                $scope.badge = resp;
                $scope.loaded_badge = true;

            });

    	$scope.submitAdd = function() {
    		endpoints.post('badges', 'update', $scope.badge).then(function(resp) {
                $state.go('userbadges');
        	});
    	}
    }
]);
