var controller = angular.module('uetopiaFrontEnd.controller.tournament', []);

controller.controller('uetopiaFrontEnd.controller.tournament', ['$rootScope', '$scope','$state','$stateParams','endpoints','$firebaseObject', '$firebaseArray', '$mdDialog',
    function GameCtrl($rootScope, $scope, $state, $stateParams, endpoints, $firebaseObject, $firebaseArray, $mdDialog) {

      $scope.teams = [];
      $scope.tiers = [];
      $scope.sponsors = [];
      $scope.userIsOwner = false;
      $scope.viewEditForm = false;
      $scope.inputSponsor = {};

      $scope.toggleViewEditForm = function () {
        if ($scope.userIsOwner ){
          $scope.viewEditForm = !$scope.viewEditForm;
        }
      }


    // look up from firebase
    var tournament_ref = firebase.database().ref().child('games').child($stateParams.gameKeyId).child('tournaments').child($stateParams.key_id);
      $scope.tournament = $firebaseObject(tournament_ref);

    var tournament_teams_array_ref = firebase.database().ref().child('games').child($stateParams.gameKeyId).child('tournaments').child($stateParams.key_id).child('teams');
      $scope.teams = $firebaseArray(tournament_teams_array_ref);

    var tournament_tiers_array_ref = firebase.database().ref().child('games').child($stateParams.gameKeyId).child('tournaments').child($stateParams.key_id).child('tiers');
      $scope.tiers = $firebaseArray(tournament_tiers_array_ref);

    var tournament_sponsors_array_ref = firebase.database().ref().child('games').child($stateParams.gameKeyId).child('tournaments').child($stateParams.key_id).child('sponsors');
      $scope.sponsors = $firebaseArray(tournament_sponsors_array_ref);


    // If the data is not in firebase, it may have been archived.  Look it up from the backend instead
    $scope.tournament.$loaded(function() {
       var dataExists = $scope.tournament.$value !== null;
       console.log(dataExists);
       if (!dataExists) {
         console.log($stateParams.key_id);
         endpoints.post('tournaments', 'tournamentGet', {'key_id': $stateParams.key_id}).then(function(resp) {
             console.log(resp.response_message);
               $scope.tournament = resp;
               $scope.teams = resp.teams;
               $scope.tiers = resp.tiers;
               $scope.sponsors = resp.sponsors;
           });

       }
       if ($rootScope.userAccount.key == $scope.tournament.hostUserKeyId ) {
         $scope.userIsOwner = true;
       }
    });

    //$scope.tournament.$watch(function(a) {
    //  console.log(a, 'msg');
    //})

    tournament_ref.on('value', function(snapshot) {
      console.log('tournament updated');
      console.log(snapshot.val());
      if (!snapshot.val()) {
        console.log('tournament was removed from firebase.');
        endpoints.post('tournaments', 'tournamentGet', {'key_id': $stateParams.key_id}).then(function(resp) {
            console.log(resp.response_message);
              $scope.tournament = resp;
              $scope.teams = resp.teams;
              $scope.tiers = resp.tiers;
              $scope.sponsors = resp.sponsors;
          });
      }
    });


    $scope.submit = function(form, inputSponsor) {
      if (!form.$invalid) {
        $scope.viewEditForm = false;
        $scope.inputSponsor.tournamentKeyId = $stateParams.key_id;
        endpoints.post('tournaments', 'tournamentSponsorCreate', $scope.inputSponsor).then(function(resp) {
            console.log(resp.response_message);
              //$scope.game = resp;
              form.$setPristine();
              console.log(resp);
              //chatService.append({textMessage: resp.response_message });
              //$state.go('home');
          });
      }
    };

    }
])
