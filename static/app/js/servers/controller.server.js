var controller = angular.module('uetopiaFrontEnd.controller.server', []);

controller.controller('uetopiaFrontEnd.controller.server', ['$scope','$rootScope','$state','$stateParams','endpoints','$firebaseObject', '$firebaseArray', '$mdDialog',
    function GameCtrl($scope, $rootScope, $state, $stateParams, endpoints, $firebaseObject, $firebaseArray,  $mdDialog) {


      $scope.editServer = false;
      $scope.gameKeyId = $stateParams.gameKeyId;
      $scope.my_server_player = {};
      $scope.shards = [];

      $scope.foundMyServerPlayer = false;
      $scope.play_status_changing = false;



      $scope.showDonateDialog = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.prompt()
          .title('How much CRED would you like to donate to this server?')
          .textContent('This is a non-refundable donation.')
          .placeholder('10')
          .ariaLabel('Donation Amount')
          .initialValue('10')
          .targetEvent(ev)
          .ok('Donate')
          .cancel('Nevermind');

        $mdDialog.show(confirm).then(function(result) {
          endpoints.post('transactions', 'serverDonate', {'key_id': $stateParams.key_id,
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

      // look up the server from firebase
      var ref = firebase.database().ref().child('servers').child($stateParams.key_id);
      $scope.server = $firebaseObject(ref);

      $scope.server.$loaded().then(function() {
          if ($scope.server.sharded_server_template) {
            var shard_array_ref = firebase.database().ref().child('servers').child($stateParams.key_id).child('shards');
            $scope.shards = $firebaseArray(shard_array_ref);
          }
      });

      var array_ref = firebase.database().ref().child('servers').child($stateParams.key_id).child('players');
      $scope.server_players = $firebaseArray(array_ref);

      // look up my server player record - if it exists
      var my_sp_ref = firebase.database().ref().child('servers').child($stateParams.key_id).child('players').child($rootScope.user.uid);
      $scope.my_server_player = $firebaseObject(my_sp_ref);
      //console.log($scope.my_server_player);

      $scope.showPlayStart = function(ev) {
        // Appending dialog to document.body to cover sidenav in docs app
        var confirm = $mdDialog.prompt()
          .title('How much CRED would you like to bring with you to this server?')
          .textContent('Any unspent or earned CRED will be returned on playEnd')
          .placeholder('100')
          .ariaLabel('Amount to bring')
          .initialValue('100')
          .targetEvent(ev)
          .ok('Play')
          .cancel('Nevermind');

        $mdDialog.show(confirm).then(function(result) {
          $scope.play_status_changing = true;
          endpoints.post('servers', 'serverPlayStart', {'key_id': $stateParams.key_id,
                                                'currencyHold': parseInt(result)
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
          $scope.status = 'You didn\'t start play.';
        });
      };

      $scope.doPlayStart = function() {
        $scope.play_status_changing = true;
        $state.go('serverplayerdetail',{ 'gameKeyId': $scope.gameKeyId, 'key_id': $stateParams.key_id})
      }

      $scope.doPlayEnd = function() {
          endpoints.post('servers', 'serverPlayEnd', {'key_id': $stateParams.key_id
                                              }).then(function(resp) {
              console.log(resp.response_message);
                //$scope.game = resp;
                //chatService.append({textMessage: resp.response_message });
                //form.$setPristine();
                console.log(resp);
                //$state.go('home');
                $scope.play_status_changing = true;
            });
      };

      var unwatch = $scope.my_server_player.$watch(function() {
        console.log("$scope.my_server_player changed!");
        $scope.play_status_changing = false;
      });

      // at some time in the future, we can unregister using
      //unwatch();






    }
])
