var controller = angular.module('uetopiaFrontEnd.controller.blog.post', []);

controller.controller('uetopiaFrontEnd.controller.blog.post', ['$scope','$state','$stateParams','endpoints','$sce',
    function DevGameOfferCtrl($scope, $state, $stateParams, endpoints, $sce) {

      $scope.loaded_post = false;
      $scope.post = {};
      $scope.postBody = null;
      $scope.loaded_posts = false;
      $scope.posts = [];

      console.log($stateParams.key_id);

      endpoints.post('blog', 'postGet', {'slugify_url': $stateParams.slugify_url}).then(function(resp) {
          console.log(resp);
            $scope.post = resp;
            $scope.loaded_post = true;
            $scope.postBody = $sce.trustAsHtml(resp.body);
        });


        endpoints.post('blog', 'postCollectionGetPage').then(function(resp) {
            console.log(resp);
                if (resp.posts ){
                  $scope.posts =  resp.posts;
                  $scope.loaded_posts = true;
                } else {
                  $scope.posts =  [];
                  $scope.loaded_posts = true;
                }
              });

    }
])
