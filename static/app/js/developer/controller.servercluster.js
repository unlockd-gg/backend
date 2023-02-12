var controller = angular.module('uetopiaFrontEnd.controller.developer.servercluster', []);

controller.controller('uetopiaFrontEnd.controller.developer.servercluster', ['$scope','$state','$stateParams','endpoints',
    function DevGameCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_game_server_cluster = false;
      $scope.loaded_game_servers = false;

      $scope.servers = [];

      $scope.viewEditForm = false;
      $scope.toggleViewEditForm = function () {
        $scope.viewEditForm = !$scope.viewEditForm;
      }

      endpoints.post('servers', 'serversCollectionGetPage', {'serverClusterKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.servers ){
                $scope.servers = resp.servers;
                $scope.loaded_game_servers = true;
              } else {
                $scope.servers =  [];
                $scope.loaded_game_servers = true;
              }
            });

      console.log($stateParams.key_id);
      endpoints.post('servers', 'serverClustersGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.servercluster = resp;
            $scope.loaded_game_server_cluster = true;
        });

        $scope.submit = function(form, servercluster) {
          //if (!form.$invalid) {
          servercluster.key_id = $stateParams.key_id;
            endpoints.post('servers', 'serverClusterUpdate', servercluster).then(function(resp) {
                console.log(resp.response_message);
                  $scope.servercluster = resp;
                  //chatService.append({textMessage: resp.response_message });
                  //updateServerCluster.$setPristine();
                  console.log(resp);
                  $state.go('developergamedetail', {'key_id':servercluster.gameKeyId});
              });
          //}
        };

        $scope.remove = function(servercluster) {
          endpoints.post('servers', 'serverClusterDelete', {'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                //chatService.append({textMessage: resp.response_message });
                  $scope.game = resp;
                  $state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
              });



          //return promise;
        };

        $scope.clone = function(servercluster) {
          endpoints.post('servers', 'serverClusterClone', {'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                //chatService.append({textMessage: resp.response_message });
                  $scope.game = resp;
                  $state.go('developergamedetail', {key_id: $stateParams.gameKeyId });
              });



          //return promise;
        };


    }
])
