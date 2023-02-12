var controller = angular.module('uetopiaFrontEnd.controller.developer.serverlink.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.serverlink.create', ['$scope', 'endpoints', '$state', '$stateParams',
    function devServerLinkCreateCtl($scope, endpoints, $state, $stateParams) {

      var gameKeyId = $stateParams.gameKeyId;
      var serverClusterKeyId = $stateParams.serverClusterKeyId;
      var serverKeyId = $stateParams.serverKeyId;
      $scope.serverlink = {};  // In case the user does not select anything
      endpoints.post('servers', 'serversCollectionGetPage', {'serverClusterKeyId': $stateParams.serverClusterKeyId}).then(function(resp) {
        console.log(resp);
            if (resp.servers ){
              $scope.servers = resp.servers;
            } else {
              $scope.servers =  [];
            }
          });


    	$scope.submitAdd = function() {
        $scope.serverlink.gameKeyId = gameKeyId;
        $scope.serverlink.serverClusterKeyId = serverClusterKeyId;
        $scope.serverlink.serverKeyId = serverKeyId;
        $scope.serverlink.originServerKeyId = $stateParams.serverKeyId;
        $scope.serverlink.targetServerKeyId = $scope.targetserver;
        endpoints.post('servers', 'serverLinkCreate', $scope.serverlink).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });

              $state.go('developerserverdetail', {gameKeyId: $stateParams.gameKeyId, serverClusterKeyId: $stateParams.serverClusterKeyId, key_id: $stateParams.serverKeyId });
        	});
    	}
    }
]);
