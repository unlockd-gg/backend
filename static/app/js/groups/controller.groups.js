var controller = angular.module('uetopiaFrontEnd.controller.groups', []);

controller.controller('uetopiaFrontEnd.controller.groups', ['$scope','endpoints','$firebaseArray',
    function homeCtl($scope, endpoints, $firebaseArray) {

      //$scope.games = [];

      var array_ref = firebase.database().ref().child('groups');
      $scope.groups = $firebaseArray(array_ref);




    }
]);
