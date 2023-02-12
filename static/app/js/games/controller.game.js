var controller = angular.module('uetopiaFrontEnd.controller.game', []);

controller.controller('uetopiaFrontEnd.controller.game', ['$rootScope', '$scope','$state','$stateParams','endpoints','$firebaseObject', '$firebaseArray', '$mdDialog',
    function GameCtrl($rootScope, $scope, $state, $stateParams, endpoints, $firebaseObject, $firebaseArray, $mdDialog) {

      $scope.servers = [];
      $scope.gameplayer = [];
      $scope.editGame = false;


    // look up from firebase
    var ref = firebase.database().ref().child('games').child($stateParams.key_id);
      $scope.game = $firebaseObject(ref);

    if ($rootScope.user && $rootScope.user.uid)
    {
      var ref = firebase.database().ref().child('games').child($stateParams.key_id).child('players').child($rootScope.user.uid);
        $scope.gameplayer = $firebaseObject(ref);
    }


      var array_ref = firebase.database().ref().child('games').child($stateParams.key_id).child('servers');
        $scope.servers = $firebaseArray(array_ref);

        var cluster_array_ref = firebase.database().ref().child('games').child($stateParams.key_id).child('clusters');
          $scope.clusters = $firebaseArray(cluster_array_ref);

      var player_array_ref = firebase.database().ref().child('games').child($stateParams.key_id).child('players').orderByChild('-updated').limitToFirst(20);
        $scope.players = $firebaseArray(player_array_ref);

      var mode_array_ref = firebase.database().ref().child('games').child($stateParams.key_id).child('game_modes').orderByChild('onlineSubsystemReference');
        $scope.modes = $firebaseArray(mode_array_ref);

      var tournament_array_ref = firebase.database().ref().child('games').child($stateParams.key_id).child('tournaments');
        $scope.tournaments = $firebaseArray(tournament_array_ref);

      var eventfeed_ref = firebase.database().ref().child('games').child($stateParams.key_id).child('eventfeed');
        $scope.eventfeed = $firebaseArray(eventfeed_ref);

        $scope.showDonateDialog = function(ev) {
          // Appending dialog to document.body to cover sidenav in docs app
          var confirm = $mdDialog.prompt()
            .title('How much CRED would you like to donate to this game?')
            .textContent('This is a non-refundable donation.')
            .placeholder('10')
            .ariaLabel('Donation Amount')
            .initialValue('10')
            .targetEvent(ev)
            .ok('Donate')
            .cancel('Nevermind');

          $mdDialog.show(confirm).then(function(result) {
            endpoints.post('transactions', 'gameDonate', {'key_id': $stateParams.key_id,
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


    }
])
