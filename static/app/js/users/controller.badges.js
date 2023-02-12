var controller = angular.module('uetopiaFrontEnd.controller.user.badges', []);

controller.controller('uetopiaFrontEnd.controller.user.badges', ['$scope','$state','$stateParams','endpoints',
    function DevGameCtrl($scope, $state, $stateParams, endpoints) {

      $scope.badges = [];

      $scope.loaded_badges = false;

      endpoints.post('badges', 'badgeCollectionGetPage').then(function(resp) {
          console.log(resp);
              if (resp.badges ){
                $scope.badges = resp.badges;
                $scope.loaded_badges = true;
              } else {
                $scope.badges =  [];
                $scope.loaded_badges = true;
              }
            });

    }
])
