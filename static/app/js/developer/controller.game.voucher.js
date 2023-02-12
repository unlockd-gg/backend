var controller = angular.module('uetopiaFrontEnd.controller.developer.game.voucher', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.voucher', ['$scope','$state','$stateParams','endpoints',
    function DevGameOfferCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_game_voucher = false;

      $scope.gameKeyId = $stateParams.gameKeyId;
      $scope.offerKeyId = $stateParams.offerKeyId;
      $scope.voucherKeyId = $stateParams.voucherKeyId;

      console.log($stateParams.key_id);

      endpoints.post('vouchers', 'voucherGet', {'key_id': $stateParams.voucherKeyId}).then(function(resp) {
          console.log(resp);
            $scope.gamevoucher = resp;
            $scope.loaded_game_voucher = true;
        });


    }
])
