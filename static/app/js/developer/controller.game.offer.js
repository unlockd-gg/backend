var controller = angular.module('uetopiaFrontEnd.controller.developer.game.offer', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.offer', ['$scope','$state','$stateParams','endpoints',
    function DevGameOfferCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_game_offer = false;
      $scope.gameoffertags = [];

      $scope.vouchers =  [];
      $scope.loaded_game_vouchers = false;

      $scope.gameKeyId = $stateParams.gameKeyId;
      $scope.offerKeyId = $stateParams.offerKeyId;

      console.log($stateParams.key_id);

      endpoints.post('offers', 'offerGet', {'key_id': $stateParams.offerKeyId}).then(function(resp) {
          console.log(resp);
            $scope.gameoffer = resp;
            $scope.loaded_game_offer = true;
            $scope.gameoffertags = resp.tags;

            // also get the vouchers associated with this offer.
            endpoints.post('vouchers', 'voucherCollectionGetPage', {'gameKeyId': $stateParams.gameKeyId, 'offerKeyId': $stateParams.offerKeyId}).then(function(resp) {
                console.log(resp);
                    if (resp.vouchers ){
                      $scope.vouchers = resp.vouchers;
                      $scope.loaded_game_vouchers = true;
                    } else {
                      $scope.vouchers =  [];
                      $scope.loaded_game_vouchers = true;
                    }
                  });

        });

        $scope.submit = function(form, gameoffer) {
          if ($scope.gameoffertags.length == 0)
          {
            alert('at least one tag is required.');
          }
          else
          {
            if (!form.$invalid) {
              $scope.gameoffer.tags = $scope.gameoffertags;
              $scope.gameoffer.key_id = $stateParams.offerKeyId;
              endpoints.post('offers', 'update', $scope.gameoffer
                                                          ).then(function(resp) {
                  console.log(resp.response_message);
                    $scope.gameoffer = resp;
                    //chatService.append({textMessage: resp.response_message });
                    //form.$setPristine();
                    console.log(resp);
                    $state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
                });
            }
          }
        };

    }
])
