var controller = angular.module('uetopiaFrontEnd.controller.user.search', []);

controller.controller('uetopiaFrontEnd.controller.user.search', ['$scope', 'endpoints', '$state',
    function userSearchCtl($scope, endpoints, $state) {

      $scope.showInvite  = false;

    	$scope.submitAdd = function() {
    		endpoints.post('users', 'usersGet', $scope.thisusersearch).then(function(resp) {
              //chatService.append({textMessage: resp.response_message });
              if (resp.response_successful) {
                $state.go('userprofile', {'key_id': resp.key_id});
              } else {
                $scope.showInvite = true;
              }


        	});
    	}
    }
]);
