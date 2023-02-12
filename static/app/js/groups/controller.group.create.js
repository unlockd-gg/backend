var controller = angular.module('uetopiaFrontEnd.controller.group.create', []);

controller.controller('uetopiaFrontEnd.controller.group.create', ['$scope', 'endpoints', '$state','$mdDialog',
    function groupCreateCtl($scope, endpoints, $state, $mdDialog) {

    	$scope.submitAdd = function() {
    		endpoints.post('groups', 'create', $scope.group).then(function(resp) {
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
    }
]);
