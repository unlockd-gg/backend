var controller = angular.module('uetopiaFrontEnd.controller.servercluster', []);

controller.controller('uetopiaFrontEnd.controller.servercluster', ['$rootScope', '$scope','$state','$stateParams','endpoints','$firebaseObject', '$firebaseArray', '$mdDialog',
    function GameCtrl($rootScope, $scope, $state, $stateParams, endpoints, $firebaseObject, $firebaseArray, $mdDialog) {

      $scope.servers = [];

    // look up from firebase
    var ref = firebase.database().ref().child('games').child($stateParams.gameKeyId);
      $scope.game = $firebaseObject(ref);

      var clusterref = firebase.database().ref().child('games').child($stateParams.gameKeyId).child('clusters').child($stateParams.key_id);
        $scope.cluster = $firebaseObject(clusterref);

      var array_ref = firebase.database().ref().child('games').child($stateParams.gameKeyId).child('clusters').child($stateParams.key_id).child('servers');
        $scope.servers = $firebaseArray(array_ref);

      var player_array_ref = firebase.database().ref().child('games').child($stateParams.gameKeyId).child('clusters').child($stateParams.key_id).child('players').orderByChild('-updated').limitToFirst(20);
        $scope.players = $firebaseArray(player_array_ref);

      var eventfeed_ref = firebase.database().ref().child('games').child($stateParams.gameKeyId).child('clusters').child($stateParams.key_id).child('eventfeed');
        $scope.eventfeed = $firebaseArray(eventfeed_ref);

      var leaderboard_ref = firebase.database().ref().child('games').child($stateParams.gameKeyId).child('clusters').child($stateParams.key_id).child('leaderboard');
        $scope.leaderboard = $firebaseArray(leaderboard_ref);


    }
])
