var controller = angular.module('uetopiaFrontEnd.controller.user.profile', []);

controller.controller('uetopiaFrontEnd.controller.user.profile', ['$rootScope', '$scope','$state','$stateParams','endpoints','$firebaseObject', '$firebaseArray', '$sce', '$mdDialog',
    function GameCtrl($rootScope, $scope, $state, $stateParams, endpoints, $firebaseObject, $firebaseArray, $sce, $mdDialog) {

      $scope.thisuser = {};
      $scope.gameplayers = [];
      $scope.eventfeed = [];
      $scope.relationship = {};
      //$scope.streamUrl = "http://player.twitch.tv/?" + $rootScope.userAccount.twitch_channel_id;
      //$scope.streamEmbedUrl = $sce.trustAsResourceUrl($scope.streamUrl);

      $scope.createFriend = function () {
        $scope.relationship.friend = true;
        endpoints.post('user_relationships', 'create', {'key_id': $stateParams.key_id,
                                                      'friend': $scope.relationship.friend}).then(function(resp) {
              $scope.relationship = resp;

          });
      }

      $scope.toggleFriend = function () {
        $scope.relationship.friend = !$scope.relationship.friend;
        endpoints.post('user_relationships', 'edit', {'key_id': $stateParams.key_id,
                                                      'friend': $scope.relationship.friend}).then(function(resp) {
              $scope.relationship = resp;

          });
      }

      $scope.showTipDialog = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.prompt()
          .title('How much CRED would you like to tip to this user?')
          .textContent('This non-refundable.')
          .placeholder('10')
          .ariaLabel('Tip Amount')
          .initialValue('10')
          .targetEvent(ev)
          .ok('Tip')
          .cancel('Nevermind');

        $mdDialog.show(confirm).then(function(result) {
          endpoints.post('transactions', 'userTip', {'key_id': $stateParams.key_id,
                                                'amountInt': parseInt(result),
                                                }).then(function(resp) {
              console.log(resp.response_message);

              if (resp.response_successful == false) {
                $mdDialog.show(
                  $mdDialog.alert()
                      .parent(angular.element(document.querySelector('#popupContainer')))
                      .clickOutsideToClose(true)
                      .title('Error')
                      .textContent(resp.response_message)
                      .ariaLabel('Alert Dialog Demo')
                      .ok('Got it!')
                      .targetEvent(ev)
                );
              }
                console.log(resp);
            });
        }, function() {
          $scope.status = 'You didn\'t donate.';
        });
      };


    // look up from firebase
    var ref = firebase.database().ref().child('users-public').child($stateParams.key_id);
      $scope.thisuser = $firebaseObject(ref);

      $scope.streamUrl = "http://player.twitch.tv/?" + $scope.thisuser.twitch_channel_id;
      $scope.streamEmbedUrl = $sce.trustAsResourceUrl($scope.streamUrl);

      var ref = firebase.database().ref().child('users-public').child($stateParams.key_id).child('games');
        $scope.gameplayers = $firebaseArray(ref);

        var eventfeed_ref = firebase.database().ref().child('users-public').child($stateParams.key_id).child('eventfeed');
          $scope.eventfeed = $firebaseArray(eventfeed_ref);

        endpoints.post('user_relationships', 'get', {'key_id': $stateParams.key_id}).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
              $scope.relationship = resp;
              //$state.go('userprofile', {'key_id': resp.key_id});
              //$scope.thisuser = resp;
          });


    }
])
