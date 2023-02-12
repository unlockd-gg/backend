var controller = angular.module('uetopiaFrontEnd.controller.group.ad.detail', []);

controller.controller('uetopiaFrontEnd.controller.group.ad.detail', ['$scope', 'endpoints', '$state','$mdDialog','$stateParams',
    function groupRoleDetailCtl($scope, endpoints, $state, $mdDialog, $stateParams) {

      $scope.ad = {};
      $scope.loaded = false;


      console.log($stateParams.key_id);
      endpoints.post('ads', 'adGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.ad = resp;
            $scope.loaded = true;

        });


    }
]);
