var controller = angular.module('uetopiaFrontEnd.controller.blog.posts', []);

controller.controller('uetopiaFrontEnd.controller.blog.posts', ['$scope','$state','$stateParams','endpoints',
    function DevGameCtrl($scope, $state, $stateParams, endpoints) {

      $scope.posts = [];
      $scope.headerPost = {};
      $scope.highlightPost1 = null;
      $scope.highlightPost2 = null;
      $scope.highlightPost3 = null;
      $scope.highlightPost4 = null;

      $scope.show_header_posts = false;

      $scope.loaded_posts = false;

      endpoints.post('blog', 'postCollectionGetPage').then(function(resp) {
          console.log(resp);
              if (resp.posts ){
                $scope.posts = resp.posts;
                $scope.loaded_posts = true;

                // Set the header and highlight posts
                if ($scope.posts.length > 0 )
                {
                  $scope.headerPost = $scope.posts.shift();
                  $scope.show_header_posts = true;
                }; // end if > 0

                if ($scope.posts.length > 0 )
                {
                  //console.log('found #2 post');
                  $scope.highlightPost1 = $scope.posts.shift();
                  //console.log($scope.highlightPost1.title );
                }; // end if > 0

                if ($scope.posts.length > 0 )
                {
                  //console.log('found #2 post');
                  $scope.highlightPost2 = $scope.posts.shift();
                  //console.log($scope.highlightPost1.title );
                }; // end if > 0

                if ($scope.posts.length > 0 )
                {
                  //console.log('found #2 post');
                  $scope.highlightPost3 = $scope.posts.shift();
                  //console.log($scope.highlightPost1.title );
                }; // end if > 0

                if ($scope.posts.length > 0 )
                {
                  //console.log('found #2 post');
                  $scope.highlightPost4 = $scope.posts.shift();
                  //console.log($scope.highlightPost1.title );
                }; // end if > 0

              } else {
                $scope.posts =  [];
                $scope.loaded_posts = true;
              }
            });

    }
])
