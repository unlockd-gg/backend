var controller = angular.module('uetopiaFrontEnd.controller.developer.game.voucher.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.voucher.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devGameVoucherCreateCtl($scope, endpoints, $state, $stateParams) {

      var gameKeyId = parseInt($stateParams.gameKeyId);
      var offerKeyId = parseInt($stateParams.offerKeyId);

      $scope.showapikey = false;
      $scope.apikey = "";

      $scope.gamevoucher = {};
      $scope.gameKeyId = $stateParams.gameKeyId;
      $scope.gamevoucher.gameKeyId = $stateParams.gameKeyId;
      $scope.gamevoucher.offerKeyId = $stateParams.offerKeyId;


    	$scope.submitAdd = function(form) {
          if (!form.$invalid) {
        		endpoints.post('vouchers', 'create', $scope.gamevoucher).then(function(resp) {
                  //chatService.append({textMessage: resp.response_message });
                	//$state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
                  $scope.apikey = resp.apiKey;
                  $scope.showapikey = true;
            	});
            }

    	}
    }
]);
