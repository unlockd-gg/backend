var profilecontroller = angular.module('uetopiaFrontEnd.controller.416.agreement', []);

profilecontroller.controller('uetopiaFrontEnd.controller.416.agreement', ['$scope', '$rootScope', '$state','endpoints',
    function ProfileCtrl($scope, $rootScope, $state, endpoints) {

      $scope.showAgreement = true;
      $scope.showRegion = false;

      $scope.agreedToTerms = false;
      $scope.selectedRegion = "us-central1";

      console.log('agreement controller');


      $scope.agreeToTerms = function() {
        $scope.agreedToTerms = true;
        $scope.showAgreement = false;
        $scope.showRegion = true;
      }

            $scope.submit = function(form) {
              if (!form.$invalid) {
                endpoints.post('users', 'usersUpdate', {
                                                  'agreed_with_terms': true,
                                                'region': $scope.selectedRegion}).then(function(resp) {
                      console.log(resp);
                      $rootScope.show_terms = false;
                      $state.go('home');

                  });
              }
            };

          }
      ]);
