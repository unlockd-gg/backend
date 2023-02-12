var controller = angular.module('uetopiaFrontEnd.controller.developer.blog.post.create', []);

controller.controller('uetopiaFrontEnd.controller.developer.blog.post.create', ['$scope', 'endpoints', '$state', '$stateParams','$sce',
    function devBlogPostCreateCtl($scope, endpoints, $state, $stateParams, $sce) {

      $scope.posttags = [];
      var gameKeyId = parseInt($stateParams.gameKeyId);
      $scope.post = {};

      //$scope.postBody = $sce.trustAsHtml($scope.post.body);

      $scope.displaySafeHtml = function(html){
        return $sce.trustAsHtml(html);
      }

    	$scope.submitAdd = function(form) {
        if ($scope.post.length == 0)
        {
          alert('at least one tag is required.');
        }
        else
        {
          if (!form.$invalid) {
            $scope.post.tags = $scope.posttags;
        		endpoints.post('blog', 'postCreate', $scope.post).then(function(resp) {
                  //chatService.append({textMessage: resp.response_message });
                	$state.go('blogpostlist');
            	});
            }
        }

    	}
    }
]);
