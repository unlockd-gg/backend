var controller = angular.module('uetopiaFrontEnd.controller.admin.server', []);

controller.controller('uetopiaFrontEnd.controller.admin.server', ['$scope','$state','$stateParams','endpoints',
    function GameCtrl($scope, $state, $stateParams, endpoints) {


      $scope.editServer = false;


      $scope.toggleServerEdit = function() {
        $scope.editServer= !$scope.editServer;
    };



      console.log($stateParams.key_id);
      endpoints.post('servers', 'get', {'key_id': $stateParams.key_id}).then(function(resp) {
          console.log(resp.response_message);
            $scope.server = resp;
        });

        $scope.submit = function(form, server) {
          if (!form.$invalid) {
            endpoints.post('servers', 'update', {'key_id': $stateParams.key_id,
                                                    'title': server.title,
                                                    'description': server.description,
                                                    'minimumCurrencyHold': server.minimumCurrencyHold,
                                                    'admissionFee': server.admissionFee,
                                                    'invisible_developer_setting': server.invisible_developer_setting,
                                                    'hostConnectionLink': server.hostConnectionLink,
                                                    'session_host_address': server.session_host_address,
                                                    'session_id':server.session_id,
                                                    'continuous_server':server.continuous_server,

                                                    //'continuous_server_project': server.continuous_server_project,
                                                    //'continuous_server_bucket': server.continuous_server_bucket,
                                                      //'continuous_server_zone': server.continuous_server_zone,
                                                      //'continuous_server_region': server.continuous_server_region,
                                                      //'continuous_server_source_disk_image': server.continuous_server_source_disk_image,
                                                      //'continuous_server_machine_type': server.continuous_server_machine_type,
                                                      //'continuous_server_startup_script_location': server.continuous_server_startup_script_location,
                                                      'continuous_server_entry': server.continuous_server_entry,
                                                      'continuous_server_provisioned': server.continuous_server_provisioned,

                                                      'adminRequest': true,

                                                  'invisible': server.invisible,

                                                }).then(function(resp) {
                console.log(resp.response_message);
                  $scope.server = resp;
                  //chatService.append({textMessage: resp.response_message });
                  form.$setPristine();
                  console.log(resp);
                  $state.go('home');
              });
          }
        };

    }
])
