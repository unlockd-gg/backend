var controller = angular.module('uetopiaFrontEnd.controller.developer.documentation', []);

controller.controller('uetopiaFrontEnd.controller.developer.documentation', ['$scope', 'endpoints',
    function developerDocsCtl($scope, endpoints) {

      $scope.viewDeprecatedProjects = false;
      $scope.toggleViewDeprecatedProjects = function () {
        $scope.viewDeprecatedProjects = !$scope.viewDeprecatedProjects;
      }


    }
]);
