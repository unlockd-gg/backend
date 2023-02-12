var controller = angular.module('uetopiaFrontEnd.controller.group.game.detail', []);

controller.controller('uetopiaFrontEnd.controller.group.game.detail', ['$scope', 'endpoints', '$state','$mdDialog','$stateParams',
    function groupRoleDetailCtl($scope, endpoints, $state, $mdDialog, $stateParams) {

      $scope.groupGame = {};
      $scope.loaded = false;
      $scope.ads_loaded = false;
      $scope.userCanEditAds = false;
      $scope.groupKeyId = $stateParams.key_id;
      $scope.groupGameKeyId = $stateParams.groupGameKeyId;
      $scope.gameKeyId = "";
      $scope.ads = [];

      // look up from firebase
      // don't bother because this is not actually a gameKeyId
      // this is a group_game_key_id
      //var ref = firebase.database().ref().child('games').child($stateParams.groupGameKeyId);
      //  $scope.game = $firebaseObject(ref);

      // get the permissions for this user
      endpoints.post('groups', 'groupUserGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            // Check for membership
            if (resp.response_successful) {
              $scope.userPermissions = resp;
              $scope.userIsMember = true;
              $scope.userCanEditAds = $scope.userPermissions.edit_ads;

            }

        });

      console.log($stateParams.key_id);
      endpoints.post('groups', 'groupGameGet', {'key_id': $stateParams.groupGameKeyId}).then(function(resp) {
          console.log(resp.response_message);
            $scope.groupGame = resp;
            $scope.loaded = true;
            $scope.gameKeyId = resp.gameKeyId;

        });

      // get the ads for this game
      endpoints.post('ads', 'adsCollectionGetPage', {'groupGameKeyId': $stateParams.groupGameKeyId}).then(function(resp) {
          console.log(resp.response_message);
            $scope.ads = resp.ads;
            $scope.ads_loaded = true;
        });


    	$scope.submit = function() {
        $scope.groupGame.key_id = $stateParams.groupGameKeyId;
    		endpoints.post('groups', 'groupGameUpdate', $scope.groupGame).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
              if (resp.response_successful) {
                $state.go('groups');
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

      $scope.remove = function(groupGame) {
        endpoints.post('groups', 'groupGameDelete',{'key_id': $stateParams.groupGameKeyId}).then(function(resp) {
              console.log(resp.response_message);
                $scope.gamelevellink = resp;
                //chatService.append({textMessage: resp.response_message });
                $state.go('groupdetail', {key_id: $stateParams.key_id });
            });



        //return promise;
      };


    }
]);
