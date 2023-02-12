var faqcontroller = angular.module('uetopiaFrontEnd.controller.faq', []);

faqcontroller.controller('uetopiaFrontEnd.controller.faq', ['$scope', '$rootScope', '$state','endpoints',
    function FaqCtrl($scope, $rootScope, $state, endpoints) {

            $scope.ten_minute_game_server_cost_cred = 0.0075 / $rootScope.CREDValue.$value;
          }
      ]);
