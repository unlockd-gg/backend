var profilecontroller = angular.module('uetopiaFrontEnd.controller.profile', []);

profilecontroller.controller('uetopiaFrontEnd.controller.profile', ['$scope', '$rootScope', '$state','endpoints','$mdDialog',
    function ProfileCtrl($scope, $rootScope, $state, endpoints, $mdDialog) {

      //$scope.userService = fbUserProfile;
      //console.log('fbUserProfile.user');
      //console.log(fbUserProfile.get());
      $scope.saveReminder = "";

      $scope.viewOptionalForm = false;
      $scope.toggleViewOptionalForm = function () {
        $scope.viewOptionalForm = !$scope.viewOptionalForm;
      }

      // strip non-alphanumeric characters

      // wait until user is loaded
      $rootScope.userAccount.$loaded().then(function() {

        var newtitle = $rootScope.userAccount.title;
        newtitle = newtitle.replace(/\W/g, '');
        newtitle = newtitle.substring(0,13);

        $scope.thisuser = {'title': newtitle,
                            'description': $rootScope.userAccount.description,
                            'developer': $rootScope.userAccount.developer,
                            'personality': $rootScope.userAccount.personality,
                            'region': $rootScope.userAccount.region,
                            'selectedRegion': $rootScope.userAccount.region,
                            'profile_saved': $rootScope.userAccount.profile_saved,
                            //'key_id': $rootScope.userAccount.key,
                            'gsp_advertisements' :$rootScope.userAccount.gsp_advertisements,
                              'gsp_totally_free' :$rootScope.userAccount.gsp_totally_free,
                              'gsp_free_to_play' :$rootScope.userAccount.gsp_free_to_play,
                              'gsp_subscription' :$rootScope.userAccount.gsp_subscription,
                              'gsp_sticker_price_purchase' :$rootScope.userAccount.gsp_sticker_price_purchase,
                              'twitch_streamer' :$rootScope.userAccount.twitch_streamer,
                              'twitch_channel_id' :$rootScope.userAccount.twitch_channel_id,
                              'groupTagKeyIdStr' :$rootScope.userAccount.groupTagKeyIdStr,
                              'opt_out_email_promotions' :$rootScope.userAccount.opt_out_email_promotions,
                              'opt_out_email_alerts' :$rootScope.userAccount.opt_out_email_alerts,
                              'defaultTeamTitle': $rootScope.userAccount.defaultTeamTitle,
                              'discord_webhook': $rootScope.userAccount.discord_webhook,
                              'discord_subscribe_errors': $rootScope.userAccount.discord_subscribe_errors,
                              'discord_subscribe_transactions': $rootScope.userAccount.discord_subscribe_transactions,
                              'discord_subscribe_consignments': $rootScope.userAccount.discord_subscribe_consignments,
                          }
          });

        endpoints.post('groups', 'groupMemberCollection', {}).then(function(resp) {
            console.log(resp);
                if (resp.group_users ){
                  $scope.group_users = resp.group_users;
                } else {
                  $scope.group_users =  [];
                }
              });

            $scope.submit = function(form, thisuser) {
              if (!form.$invalid) {
                if ($scope.thisuser.groupTagKeyIdStr) {
                  groupTagKeyIdStr = $scope.thisuser.groupTagKeyIdStr.toString()
                } else {
                  groupTagKeyIdStr = null;
                }
                endpoints.post('users', 'usersUpdate', {'title': $scope.thisuser.title,
                                                      'description': $scope.thisuser.description,
                                                      'developer': $scope.thisuser.developer,
                                                      'personality': $scope.thisuser.selectedPersonality,
                                                    'region': $scope.thisuser.selectedRegion,
                                                    'gsp_advertisements' :$scope.thisuser.gsp_advertisements,
                                                      'gsp_totally_free' :$scope.thisuser.gsp_totally_free,
                                                      'gsp_free_to_play' :$scope.thisuser.gsp_free_to_play,
                                                      'gsp_subscription' :$scope.thisuser.gsp_subscription,
                                                      'gsp_sticker_price_purchase' :$scope.thisuser.gsp_sticker_price_purchase,
                                                      'twitch_streamer' :$scope.thisuser.twitch_streamer,
                                                      'twitch_channel_id' :$scope.thisuser.twitch_channel_id,
                                                      'opt_out_email_promotions' : $scope.thisuser.opt_out_email_promotions,
                                                      'opt_out_email_alerts' : $scope.thisuser.opt_out_email_alerts,
                                                      'defaultTeamTitle': $scope.thisuser.defaultTeamTitle,
                                                      'groupTagKeyIdStr' :groupTagKeyIdStr,
                                                      'discord_webhook': $scope.thisuser.discord_webhook,
                                                      'discord_subscribe_errors': $scope.thisuser.discord_subscribe_errors,
                                                      'discord_subscribe_transactions': $scope.thisuser.discord_subscribe_errors,
                                                      'discord_subscribe_consignments': $scope.thisuser.discord_subscribe_errors
                                                  }).then(function(resp) {

                                                    if (resp.response_successful) {
                                                      $state.go('home');
                                                    } else {
                                                      $mdDialog.show(
                                                        $mdDialog.alert()
                                                          .parent(angular.element(document.querySelector('#popupContainer')))
                                                          .clickOutsideToClose(true)
                                                          .title('There was a problem')
                                                          .textContent(resp.response_message)
                                                          .ariaLabel('Alert Dialog Demo')
                                                          .ok('Got it!')
                                                          //.targetEvent(ev)
                                                      );
                                                    }

                  });
              }
            };

            $scope.enableDeveloperTools = function(ev) {
                $mdDialog.show({
                  controller: DialogController,
                  templateUrl: '/app/partials/developer.agreement.html',
                  parent: angular.element(document.body),
                  targetEvent: ev,
                  clickOutsideToClose:true,
                  fullscreen: $scope.customFullscreen // Only for -xs, -sm breakpoints.
                })
                .then(function(answer) {
                  if (answer == 'agree') {
                    $scope.thisuser.developer = true;
                    $scope.saveReminder = "after you save changes."
                  }
                  else {
                    $scope.thisuser.developer = false;
                  }

                }, function() {
                  $scope.status = 'You cancelled the dialog.';
                });
              };

              function DialogController($scope, $mdDialog) {
                $scope.hide = function() {
                  $mdDialog.hide();
                };

                $scope.cancel = function() {
                  $mdDialog.cancel();
                };

                $scope.answer = function(answer) {
                  $mdDialog.hide(answer);
                };
              }

          }
      ]);
