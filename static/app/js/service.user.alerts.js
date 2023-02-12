(function (angular) {

  function fbUserAlerts($firebaseArray, session) {
    // create a reference to the database location where we will store our data

    var session_auth_data = session.getAuthData();
    var alertArray = {};

    this.removeAlert= function(alert) {
      console.log('removeAlert')
    alertArray.$remove(alert);
  };

    if (session_auth_data && session_auth_data.uid) {

      var ref = firebase.database().ref().child('users').child(session_auth_data.uid).child('alerts');
      // this uses AngularFire to create the synchronized array
      alertArray = $firebaseArray(ref);
      return alertArray;
      //return $firebaseArray(ref);
    } else {
      return null;
    }
  }

  // Inject dependencies
  fbUserAlerts.$inject = ['$firebaseArray', 'session'];

  // Export
  angular
    .module('uetopiaFrontEnd')
    .factory('fbUserAlerts', fbUserAlerts);

})(angular);
