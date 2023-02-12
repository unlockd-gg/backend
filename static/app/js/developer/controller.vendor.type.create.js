var controller = angular.module('uetopiaFrontEnd.controller.developer.vendor.type.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.vendor.type.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devSVendorTypeCreateCtl($scope, endpoints, $state, $stateParams) {

      var gameKeyId = $stateParams.gameKeyId;

    	$scope.submitAdd = function() {
        $scope.vendortype.gameKeyId = gameKeyId;

        endpoints.post('vendors', 'typeCreate', $scope.vendortype).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
            	$state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
        	});
    	}
    }
]);
