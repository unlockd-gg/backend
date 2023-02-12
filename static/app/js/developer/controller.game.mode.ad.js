var controller = angular.module('uetopiaFrontEnd.controller.developer.gameModeAd', []);

controller.controller('uetopiaFrontEnd.controller.developer.gameModeAd', ['$scope','$state','$stateParams','endpoints',
    function DevGameCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_game_mode_ad = false;

      $scope.viewRejectForm = false;
      $scope.toggleViewRejectForm = function () {
        $scope.viewRejectForm = !$scope.viewRejectForm;
      }

      console.log($stateParams.key_id);
      endpoints.post('ads', 'adGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.ad = resp;
            $scope.loaded_game_mode_ad = true;
        });


        $scope.approve = function(form) {
          if (!form.$invalid) {
            $scope.ad.key_id = $stateParams.key_id;
            $scope.ad.approved = true;
            endpoints.post('ads', 'adsAuthorize', $scope.ad
                                                        ).then(function(resp) {
                console.log(resp.response_message);
                  //$scope.gamemode = resp;
                  //chatService.append({textMessage: resp.response_message });
                  //form.$setPristine();
                  console.log(resp);
                  $state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
              });
          }
        };

        $scope.reject = function(form) {
          $scope.ad.key_id = $stateParams.key_id;
          $scope.ad.rejected = true;
          endpoints.post('ads', 'adsAuthorize', $scope.ad).then(function(resp) {
                console.log(resp.response_message);
                  //$scope.gamemode = resp;
                  //chatService.append({textMessage: resp.response_message });
                  $state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
              });



          //return promise;
        };
    }
])
