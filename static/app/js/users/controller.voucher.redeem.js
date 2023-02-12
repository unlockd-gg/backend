var controller = angular.module('uetopiaFrontEnd.controller.voucher.redeem', []);

controller.controller('uetopiaFrontEnd.controller.voucher.redeem', ['$scope','$state','$stateParams','endpoints','$mdDialog',
    function VoucherRedeemCtrl($scope, $state, $stateParams, endpoints, $mdDialog) {

      $scope.gameKeyId = $stateParams.gameKeyId;
      $scope.voucherKey = "";
      $scope.response_message = "";
      $scope.showVoucherKeyForm = true;
      $scope.showOfferDetails = false;
      $scope.autoRefresh = false;
      

      console.log($stateParams.key_id);

      $scope.submitAdd = function(form) {
          if (!form.$invalid) {
            $scope.showVoucherKeyForm = false;
        		endpoints.post('offers', 'offerGet', {'voucherKey': $scope.voucherKey } ).then(function(resp) {

                  if (resp.response_successful)
                  {
                    console.log('found offer');
                    $scope.offer = resp;
                    $scope.loaded_game_offer = true;
                    $scope.response_message = resp.response_message;
                    $scope.showOfferDetails = true;
                  }
                  else
                  {
                    console.log('did not find offer');
                    $scope.response_message = resp.response_message;

                    $mdDialog.show(
                      $mdDialog.alert()
                        .parent(angular.element(document.querySelector('#popupContainer')))
                        .clickOutsideToClose(true)
                        .title('There was a problem with the voucher')
                        .textContent('Sorry, this voucher is not valid.')
                        .ariaLabel('Invalid voucher')
                        .ok('Got it!')
                        //.targetEvent(ev)
                    );
                  }
            	});
            }
    	}

      $scope.showConfirm = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.confirm()
              .title('Claim this offer?')
              .textContent('By claiming the offer, you agree to any terms outlined in the details. ')
              .ariaLabel('Offer Claim')
              .targetEvent(ev)
              .ok('Yes.  CLAIM IT')
              .cancel('Nevermind');

              $mdDialog.show(confirm).then(function() {
                console.log('redeeming');
                endpoints.post('vouchers', 'redeem', {'apiKey': $scope.voucherKey, 'autoRefresh': $scope.autoRefresh } ).then(function(resp) {
                    if (resp.response_successful)
                    {
                      console.log('redeemed');
                      $state.go('home');
                    }
                    else
                    {
                      console.log('did not redeem');
                      $state.go('home');
                    }
                });


                  }, function() {
                    $state.go('home');


                  });
      };


    }
])
