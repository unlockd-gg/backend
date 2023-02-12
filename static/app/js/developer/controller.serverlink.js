var controller = angular.module('uetopiaFrontEnd.controller.developer.serverlink', []);

controller.controller('uetopiaFrontEnd.controller.developer.serverlink', ['$scope','$state','$stateParams','endpoints',
    function DevGameCtrl($scope, $state, $stateParams, endpoints) {

      $scope.loaded_game_server_link = false;

      console.log($stateParams.key_id);
      endpoints.post('servers', 'serverLinkGet', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.serverlink = resp;
            $scope.loaded_game_server_link = true;
        });

        $scope.submit = function(form, serverlink) {
          if (!form.$invalid) {
            endpoints.post('servers', 'serverLinkUpdate', {'key_id': $stateParams.key_id,
                                                        'title': serverlink.title,
                                                        'description': serverlink.description,
                                                        'permissionCanMount': serverlink.permissionCanMount,
                                                          'permissionCanUserTravel': serverlink.permissionCanUserTravel,
                                                          'permissionCanDismount': serverlink.permissionCanDismount,
                                                          'isEntryPoint': serverlink.isEntryPoint,
                                                          'resourcesUsedToTravel': serverlink.resourcesUsedToTravel,
                                                            'resourceAmountsUsedToTravel': serverlink.resourceAmountsUsedToTravel,
                                                            'currencyCostToTravel':  serverlink.currencyCostToTravel,
                                                            'coordLocationX': serverlink.coordLocationX,
                                                            'coordLocationY': serverlink.coordLocationY,
                                                            'coordLocationZ': serverlink.coordLocationZ,
                                                            'rotationX': serverlink.rotationX,
                                                            'rotationY': serverlink.rotationY,
                                                            'rotationZ': serverlink.rotationZ,
                                                            'destinationLocationX': serverlink.destinationLocationX,
                                                            'destinationLocationY': serverlink.destinationLocationY,
                                                            'destinationLocationZ': serverlink.destinationLocationZ,
                                                            'targetStatusCreating': serverlink.targetStatusCreating,
                                                            'targetStatusProvisioned': serverlink.targetStatusProvisioned,
                                                            'targetStatusOnline': serverlink.targetStatusOnline,
                                                        }).then(function(resp) {
                console.log(resp.response_message);
                  $scope.serverlink = resp;
                  //chatService.append({textMessage: resp.response_message });
                  //form.$setPristine();
                  console.log(resp);
                  $state.go('developerserverdetail', {gameKeyId: $stateParams.gameKeyId, serverClusterKeyId: $stateParams.serverClusterKeyId, key_id: $stateParams.serverKeyId });
              });
          }
        };

        $scope.remove = function(server) {
          endpoints.post('servers', 'serverLinkDelete',{'key_id': $stateParams.key_id}).then(function(resp) {
                console.log(resp.response_message);
                  $scope.serverlink = resp;
                  //chatService.append({textMessage: resp.response_message });
                  $state.go('developerserverdetail', {gameKeyId: $stateParams.gameKeyId, serverClusterKeyId: $stateParams.serverClusterKeyId, key_id: $stateParams.serverKeyId });
              });



          //return promise;
        };
    }
])
