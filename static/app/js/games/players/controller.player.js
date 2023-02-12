var controller = angular.module('uetopiaFrontEnd.controller.game.player', []);

controller.controller('uetopiaFrontEnd.controller.game.player', ['$scope','$state','$stateParams','endpoints','$mdDialog','$firebaseObject',
    function GamePlayerCtrl($scope, $state, $stateParams, endpoints, $mdDialog, $firebaseObject) {

      $scope.loaded = false;

      $scope.player = [];
      //$scope.server_clusters = [];
      $scope.selected_server_cluster = null;
      console.log($stateParams.key_id);

      var ref = firebase.database().ref().child('games').child($stateParams.key_id);
        $scope.game = $firebaseObject(ref);

        endpoints.post('games', 'gamePlayerGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp);

                $scope.player = resp;
                $scope.selected_server_cluster = resp.lastServerClusterKeyId;
                $scope.loaded = true;

                if ($scope.player.showGameOnProfile == null) {
                  $scope.player.showGameOnProfile = true;
                }



            });


        endpoints.post('servers', 'serverClusterCollectionGetPage', {'gameKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);

                $scope.server_clusters = resp.server_clusters;

            });

        $scope.submit = function(form, player) {
          if (!form.$invalid) {
            player.key_id = $stateParams.key_id;
            console.log($scope.selected_server_cluster);
            console.log($stateParams.key_id);
            player.lastServerClusterKeyId = $scope.selected_server_cluster;
            endpoints.post('games', 'gamePlayerUpdate', player).then(function(resp) {
                console.log(resp.response_message);

                  if (resp.response_successful) {
                    $state.go('gamedetail', { key_id: $stateParams.key_id});
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

    }
])
