var controller = angular.module('uetopiaFrontEnd.controller.developer.game.patch.deploy', []);

controller.controller('uetopiaFrontEnd.controller.developer.game.patch.deploy', ['$scope', 'endpoints', '$state', '$stateParams',
    function devGamePatchDeployCtl($scope, endpoints, $state, $stateParams) {

      var gameKeyId = parseInt($stateParams.gameKeyId);
      $scope.gamepatch = {};
      $scope.gamepatch.patcher_server_shutdown_warning_chat = "This server will shutdown in 60 seconds for a patch.  To avoid data loss, log out of this server immediately.";
      $scope.gamepatch.patcher_discord_message = "Patch incoming in 60 seconds.  Finish any active matches.  Disconnect from non-match servers now.  Restart the game launcher to update."
      $scope.gamepatch.patcher_server_shutdown_seconds = 60;

    	$scope.submitAdd = function() {
        $scope.gamepatch.key_id = gameKeyId;

    		endpoints.post('games', 'gamePatchDeploy', $scope.gamepatch).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
            	$state.go('developergamedetail', {key_id: gameKeyId });
        	});
    	}
    }
]);
