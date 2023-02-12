var router = angular.module('uetopiaFrontEnd.tokenapp.router', []);

router
    .config(['$urlRouterProvider',
        function($urlRouterProvider) {
            $urlRouterProvider.otherwise("/");
        }]);

router
    .config(['$stateProvider',
        function($stateProvider) {

            $stateProvider


                .state('home', {
                    url :'/',
                    title: 'Token',
                      resolve: {
                        // controller will not be loaded until $requireSignIn resolves
                        // Auth refers to our $firebaseAuth wrapper in the factory below
                        //"currentAuth": ["Auth", function(Auth) {
                          // $requireSignIn returns a promise so the resolve waits for it to complete
                          // If the promise is rejected, it will throw a $stateChangeError (see above)
                          //return Auth.$requireSignIn();
                        //}]
                      },
                      views :  {
                          '': {
                              controller: 'uetopiaFrontEnd.controller.token.expose',
                              templateUrl: '/app/partials/token.expose.html',
                          },
                        },
                    })

                    


    }])
