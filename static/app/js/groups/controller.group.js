var controller = angular.module('uetopiaFrontEnd.controller.group', []);

controller.controller('uetopiaFrontEnd.controller.group', ['$rootScope', '$scope', '$state', '$stateParams', 'endpoints', '$firebaseObject', '$firebaseArray', '$mdDialog',
    function GroupCtrl($rootScope, $scope, $state, $stateParams, endpoints, $firebaseObject, $firebaseArray, $mdDialog) {

      $scope.groupUser = [];
      $scope.userIsOwner = false;
      $scope.userIsMember = false;
      $scope.userCanEditGroupRoles = false;
      $scope.userCanEditMemberRoles = false;
      $scope.userCanEditGames = false;
      $scope.userCanViewTransactions = false;
      $scope.viewEditForm = false;
      $scope.viewRolesForm = false;
      $scope.viewGamesForm = false;
      $scope.viewMemberForm = false;
      $scope.groupEditableData = {};
      $scope.userPermissions = {};
      $scope.groupRoles = [];
      $scope.transactions = [];


      $scope.toggleViewEditForm = function () {
        if ($scope.userIsOwner ){
          $scope.viewEditForm = !$scope.viewEditForm;
        }
      }
      $scope.toggleViewRolesForm = function () {
        if ($scope.userIsOwner ){
          $scope.viewRolesForm = !$scope.viewRolesForm;
        }
      }
      $scope.toggleViewGamesForm = function () {
        if ($scope.userIsOwner ){
          $scope.viewGamesForm = !$scope.viewGamesForm;
        }
      }
      $scope.toggleViewMemberForm = function () {
          $scope.viewMemberForm = !$scope.viewMemberForm;
      }

      $scope.viewTransactions= false;
      $scope.toggleViewTransactions = function () {
        $scope.viewTransactions = !$scope.viewTransactions;
      }

    // look up from firebase
    var ref = firebase.database().ref().child('groups').child($stateParams.key_id);
      $scope.group = $firebaseObject(ref);

    var user_array_ref = firebase.database().ref().child('groups').child($stateParams.key_id).child('users').orderByChild('-updated');
      $scope.users = $firebaseArray(user_array_ref);

    var tournament_array_ref = firebase.database().ref().child('groups').child($stateParams.key_id).child('tournaments');
      $scope.tournaments = $firebaseArray(tournament_array_ref);

    var eventfeed_ref = firebase.database().ref().child('groups').child($stateParams.key_id).child('eventfeed');
      $scope.eventfeed = $firebaseArray(eventfeed_ref);

    $scope.group.$loaded()
      .then(function(){
          // get the permissions for this user if they exist
          if ($rootScope.userAccount)
          {
            endpoints.post('groups', 'groupUserGet', {'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                  // Check for membership
                  if (resp.response_successful) {
                    $scope.userPermissions = resp;
                    $scope.userIsMember = true;
                    $scope.userCanEditGroupRoles = $scope.userPermissions.update_group_roles;
                    $scope.userCanEditMemberRoles = $scope.userPermissions.update_player_roles;
                    $scope.userCanEditGames = $scope.userPermissions.update_games;
                    $scope.userCanViewTransactions = $scope.userPermissions.view_transactions;
                    // also get the list of roles
                    // These are the roles that exist within the group.
                    if ($scope.userPermissions.update_group_roles) {
                      console.log('loading roles from endpoints');
                      endpoints.post('groups', 'groupRoleCollectionGet', {'key_id': $stateParams.key_id}).then(function(resp) {
                          console.log(resp.response_message);
                            $scope.groupRoles = resp.roles;
                        });

                    }
                    if ($scope.userPermissions.view_transactions) {
                      console.log('loading transactions from endpoints');
                      endpoints.post('transactions', 'transactionCollectionGetPage', {'groupKeyId': $stateParams.key_id, 'transactionType': 'group'}).then(function(resp) {
                          console.log(resp);
                              if (resp.transactions ){
                                $scope.transactions = resp.transactions;
                              } else {
                                $scope.transactions =  [];
                              }
                            });
                    }
                  }

              });


              if ($rootScope.userAccount.key == $scope.group.ownerPlayerKeyId ) {
                $scope.userIsOwner = true;
                console.log('loading group data from endpoints');
                endpoints.post('groups', 'get', {'key_id': $stateParams.key_id}).then(function(resp) {
                    console.log(resp.response_message);
                      $scope.groupEditableData = resp;
                  });

            }
          }



      });

      //var group_user_ref = firebase.database().ref().child('group_members').child($stateParams.key_id).child('users').child($rootScope.user.uid);
      //  $scope.groupUser = $firebaseObject(ref);


      $scope.submit = function(form, group) {
        if (!form.$invalid) {
          $scope.group.key_id = $stateParams.key_id;
          endpoints.post('groups', 'update', $scope.groupEditableData).then(function(resp) {
              console.log(resp.response_message);
                //$scope.game = resp;
                form.$setPristine();
                console.log(resp);
                //chatService.append({textMessage: resp.response_message });
                $state.go('home');
            });
        }
      };

      $scope.joingroup = function(ev) {
        console.log('joingroup');

          // Appending dialog to document.body to cover sidenav in docs app
          var confirm2 = $mdDialog.prompt()
            .title('Include a personal message with your application')
            .textContent($scope.group.application_message)
            .placeholder('Personal Message')
            .ariaLabel('Personal Message')
            .initialValue('')
            .targetEvent(ev)
            .ok('Apply to Join!')
            .cancel('Nevermind.  I do not want to apply.');

          $mdDialog.show(confirm2).then(function(result) {
            //$scope.status = 'You decided to name your dog ' + result + '.';


            $scope.group.key_id = $stateParams.key_id;
            $scope.group.application_message = result;

            endpoints.post('groups', 'groupJoin', $scope.group).then(function(resp) {
                console.log(resp.response_message);
                  //$scope.game = resp;
                  //form.$setPristine();
                  console.log(resp);
                  //chatService.append({textMessage: resp.response_message });
                  $state.go('home');
              });

          }, function() {
            $scope.status = 'You didn\'t apply';
          });






      };


        $scope.showDonateDialog = function(ev) {
          // Appending dialog to document.body to cover sidenav in docs app
          var confirm = $mdDialog.prompt()
            .title('How much CRED would you like to donate to this group?')
            .textContent('This is a non-refundable donation.')
            .placeholder('10')
            .ariaLabel('Donation Amount')
            .initialValue('10')
            .targetEvent(ev)
            .ok('Donate')
            .cancel('Nevermind');

          $mdDialog.show(confirm).then(function(result) {
            endpoints.post('transactions', 'groupDonate', {'key_id': $stateParams.key_id,
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
