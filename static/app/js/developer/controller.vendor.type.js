var controller = angular.module('uetopiaFrontEnd.controller.developer.vendor.type', []);

controller.controller('uetopiaFrontEnd.controller.developer.vendor.type', ['$scope','$state','$stateParams','endpoints',
    function DevVendorTypeCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_vendor_type= false;

      console.log($stateParams.key_id);
      endpoints.post('vendors', 'typeGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.vendortype = resp;
            $scope.loaded_vendor_type = true;
        });

        $scope.submit = function(form, gamelevellink) {
          if (!form.$invalid) {
            $scope.vendortype.key_id = $stateParams.key_id;
            endpoints.post('vendors', 'typeUpdate', $scope.vendortype
                                                        ).then(function(resp) {
                console.log(resp.response_message);
                  $scope.vendortype = resp;
                  //chatService.append({textMessage: resp.response_message });
                  //form.$setPristine();
                  console.log(resp);
                  $state.go('developergamedetail', {key_id: $stateParams.gameKeyId});
              });
          }
        };

        $scope.remove = function(gamelevellink) {
          endpoints.post('vendors', 'typeDelete',{'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                  $scope.vendortype = resp;
                  //chatService.append({textMessage: resp.response_message });
                  $state.go('developergamedetail', {key_id: $stateParams.gameKeyId});
              });



          //return promise;
        };
    }
])
