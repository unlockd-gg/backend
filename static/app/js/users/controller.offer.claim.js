var controller = angular.module('uetopiaFrontEnd.controller.offer.claim', []);

controller.controller('uetopiaFrontEnd.controller.offer.claim', ['$scope','$state','$stateParams','endpoints','$mdDialog',
    function OfferClaimCtrl($scope, $state, $stateParams, endpoints, $mdDialog) {

      $scope.offerKeyId = $stateParams.offerKeyId;
      $scope.voucherKey = "";
      $scope.response_message = "";
      $scope.showOfferDetails = false;
      $scope.autoRefresh = false;

  		endpoints.post('offers', 'offerGet', {'key_id': $stateParams.offerKeyId } ).then(function(resp) {

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
                  .title('There was a problem with the offer')
                  .textContent('Sorry, this offer could not be found.')
                  .ariaLabel('Invalid offer')
                  .ok('Got it!')
                  //.targetEvent(ev)
              );
            }
      	});

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
                endpoints.post('offers', 'claim', {'key_id': $stateParams.offerKeyId, 'autoRefresh': $scope.autoRefresh } ).then(function(resp) {
                    if (resp.response_successful)
                    {
                      console.log('claimed');
                      $state.go('home');
                    }
                    else
                    {
                      console.log('did not claim');

                      $mdDialog.show(
                        $mdDialog.alert()
                          .parent(angular.element(document.querySelector('#popupContainer')))
                          .clickOutsideToClose(true)
                          .title('Offer was not claimed')
                          .textContent(resp.response_message)
                          .ariaLabel('Offer claim error')
                          .ok('Got it!')
                          .targetEvent(ev)
                      );


                      //$state.go('home');
                    }
                });


                  }, function() {
                    $state.go('home');


                  });
      };


    }
])
