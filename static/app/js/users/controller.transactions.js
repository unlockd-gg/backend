var controller = angular.module('uetopiaFrontEnd.controller.user.transactions', []);

controller.controller('uetopiaFrontEnd.controller.user.transactions', ['$scope', 'endpoints',
    function userTransactionsCtl($scope, endpoints) {

      $scope.transactions = [];

      endpoints.post('transactions', 'transactionCollectionGetPage', {}).then(function(resp) {
              if (resp.transactions ){
                $scope.transactions = resp.transactions;
              } else {
                $scope.transactions =  [];
              }
            });

    }
]);
