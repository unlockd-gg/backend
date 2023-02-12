var controller = angular.module('uetopiaFrontEnd.controller.developer.server', []);

controller.controller('uetopiaFrontEnd.controller.developer.server', ['$scope','$state','$stateParams','endpoints',
    function DevGameCtrl($scope, $state, $stateParams, endpoints) {

      var gameKeyId = parseInt($stateParams.gameKeyId);
      var serverClusterKeyId = parseInt($stateParams.serverClusterKeyId);

      $scope.loaded_game_server = false;
      $scope.loaded_game_server_links = false;
      $scope.loaded_game_server_transactions = false;
      $scope.loaded_vendors = false;
      $scope.loaded_instances = false;

      $scope.show_links = true; // don't show links for instances or shards


      $scope.serverlinks = [];
      $scope.transactions = [];
      $scope.server_instances = [];
      $scope.servertags = [];

      $scope.viewEditForm = false;
      $scope.toggleViewEditForm = function () {
        $scope.viewEditForm = !$scope.viewEditForm;
      }

      $scope.viewTransactions= false;
      $scope.toggleViewTransactions = function () {
        $scope.viewTransactions = !$scope.viewTransactions;
      }

      $scope.viewCredentials= false;
      $scope.toggleViewCredentials = function () {
        $scope.viewCredentials = !$scope.viewCredentials;
      }




      endpoints.post('servers', 'serverLinkCollectionGetPage', {'originServerKeyId': $stateParams.key_id}).then(function(resp) {
          console.log(resp);
              if (resp.server_links ){
                $scope.serverlinks = resp.server_links;
                $scope.loaded_game_server_links = true;
              } else {
                $scope.serverlinks =  [];
                $scope.loaded_game_server_links = true;
              }
            });

      endpoints.post('transactions', 'transactionCollectionGetPage', {'serverKeyId': $stateParams.key_id, 'transactionType': 'server'}).then(function(resp) {
          console.log(resp);
              if (resp.transactions ){
                $scope.transactions = resp.transactions;
                $scope.loaded_game_server_transactions = true;
              } else {
                $scope.transactions =  [];
                $scope.loaded_game_server_transactions = true;
              }
            });

      endpoints.post('games', 'gameLevelsCollectionDeveloperGetPage', {'gameKeyId': gameKeyId}).then(function(resp) {
          console.log(resp);
              if (resp.game_levels ){
                $scope.game_levels = resp.game_levels;
              } else {
                $scope.game_levels =  [];
              }
            });

      endpoints.post('vendors', 'collectionGetPage', {'serverKeyId': $stateParams.key_id, }).then(function(resp) {
          console.log(resp);
              if (resp.vendors ){
                $scope.vendors = resp.vendors;
                $scope.loaded_vendors = true;
              } else {
                $scope.vendors =  [];
                $scope.loaded_vendors = true;
              }
            });



      console.log($stateParams.key_id);
      endpoints.post('servers', 'get', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.server = resp;
            $scope.targetgamelevel = resp.gameLevelKeyId;
            $scope.loaded_game_server = true;

            if (resp.requireBadgeTags)
            {
              console.log('found tags');
              $scope.servertags = resp.requireBadgeTags;
            }
            else
            {
              console.log('did not find tags');
              $scope.servertags = [];
            }

            // dont show links for instances or shards
            if ($scope.server.instanced_from_template || $scope.server.sharded_from_template )
            {
              $scope.show_links = false;
            }

            if (resp.sharded_server_template)
            {
              console.log('sharded server');


              endpoints.post('servers', 'serversCollectionGetPage', {'sharded_from_template_serverKeyId': $stateParams.key_id}).then(function(resp) {
                  console.log(resp);
                      if (resp.servers ){
                        $scope.shards = resp.servers;
                        $scope.loaded_shards = true;
                      } else {
                        $scope.shards =  [];
                        $scope.loaded_shards = true;
                      }
                    });





            }
            if (resp.instance_server_template)
            {
              console.log('instanced server');

              endpoints.post('servers', 'serversCollectionGetPage', {'instanced_from_template_serverKeyId': $stateParams.key_id}).then(function(resp) {
                  console.log(resp);
                      if (resp.servers ){
                        $scope.server_instances = resp.servers;
                        $scope.loaded_instances = true;
                      } else {
                        $scope.server_instances =  [];
                        $scope.loaded_instances = true;
                      }
                    });


            }


        });

        $scope.submit = function(form, server) {
          if (!form.$invalid) {
            server.key_id = $stateParams.key_id,
            server.requireBadgeTags = $scope.servertags;
            endpoints.post('servers', 'update', server).then(function(resp) {
                console.log(resp.response_message);
                  $scope.server = resp;
                  //chatService.append({textMessage: resp.response_message });
                  //updateServer.$setPristine();
                  console.log(resp);
                  $state.go('developerserverclusterdetail', {'gameKeyId':server.gameKeyId, 'key_id': server.serverClusterKeyId});

              });
          }
        };

        $scope.remove = function(server) {
          endpoints.post('servers', 'delete', {'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                //chatService.append({textMessage: resp.response_message });
                  $scope.server = resp;
                  $state.go('developerserverclusterdetail', {'gameKeyId':$stateParams.gameKeyId, 'key_id': $stateParams.serverClusterKeyId});
              });



          //return promise;
        };
    }
])
