var profilecontroller = angular.module('uetopiaFrontEnd.controller.agreement', []);

profilecontroller.controller('uetopiaFrontEnd.controller.agreement', ['$scope', '$rootScope', '$state','endpoints', 
    function ProfileCtrl($scope, $rootScope, $state, endpoints) {


      //$scope.userService = fbUserProfile;
      //console.log('fbUserProfile.user');
      //console.log(fbUserProfile.get());
      $scope.thisuser = {'title': $rootScope.userAccount.title,
                          'description': $rootScope.userAccount.description,
                          'developer': $rootScope.userAccount.developer,
                          'personality': $rootScope.userAccount.personality,
                          'region': $rootScope.userAccount.region,
                          'selectedRegion': $rootScope.userAccount.region,
                          'profile_saved': $rootScope.userAccount.profile_saved,
                          'key_id': $rootScope.userAccount.key
                        }

            $scope.submit = function(form, thisuser) {
              if (!form.$invalid) {
                endpoints.post('users', 'usersUpdate', {
                                                  'agreed_with_terms': true}).then(function(resp) {
                      console.log(resp);
                      $rootScope.show_terms = false;
                      $state.go('profile');

                  });
              }
            };

          }
      ]);
