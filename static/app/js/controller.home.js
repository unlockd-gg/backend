var controller = angular.module('uetopiaFrontEnd.controller.home', []);

controller.controller('uetopiaFrontEnd.controller.home', ['$scope','endpoints','$firebaseArray',
    function homeCtl($scope, endpoints, $firebaseArray) {

      var array_ref = firebase.database().ref().child('games').orderByChild("invisible_developer_setting").equalTo(false);;
      $scope.games = $firebaseArray(array_ref);




    }
]);
