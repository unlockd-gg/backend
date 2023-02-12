var controller = angular.module('uetopiaFrontEnd.controller.user.cred.buy', []);

controller.controller('uetopiaFrontEnd.controller.user.cred.buy', ['$scope', 'endpoints', '$rootScope', '$window', '$mdDialog',
    function userCredBuyCtl($scope, endpoints, $rootScope, $window, $mdDialog) {

      $scope.CredAmountToBuy = 0;
      $scope.InvoiceNumber = null;
      $scope.AmountSelectedBitpay = false;
      $scope.AmountSelectedBraintree = false;
      $scope.ShowPurchaseOptions = true;
      $scope.BitPayRedirectUrl = null;
      $scope.showChooseAWayToPayButton = false;
      $scope.showBraintreeDropIn = false;
      $scope.showTransactionSummary = false;

      $scope.hasCalledBack = false;
      $scope.showConfirmButton = false;
      $scope.showLoadingPaymentUINotification = true;
      $scope.showTransactionComplete = false;

      $rootScope.CREDValue.$loaded().then(function() {
          console.log($rootScope.CREDValue.$value);
          $scope.CredAmountToBuy1 = Math.floor( 5.00 / $rootScope.CREDValue.$value ) ;
          $scope.CredAmountToBuy2 = Math.floor( 10.00 / $rootScope.CREDValue.$value) ;
          $scope.CredAmountToBuy3 = Math.floor( 20.00 / $rootScope.CREDValue.$value) ;
          $scope.CredAmountToBuy4 = Math.floor( 40.00 / $rootScope.CREDValue.$value) ;

      });


      $scope.SelectBuyCred1 = function () {
        console.log('buyCred1');
        $scope.CredAmountToBuy = Math.floor( 5.00 / $rootScope.CREDValue.$value ) ;
        $scope.USDAmountToBuy = 5.00;

        $scope.buycred1bool = true;
        $scope.buycred2bool = false;
        $scope.buycred3bool = false;
        $scope.buycred4bool = false;

        $scope.showChooseAWayToPayButton  = true;
        //$scope.$apply();
      }


      $scope.SelectBuyCred2= function () {
        console.log('buyCred2');
        $scope.CredAmountToBuy = Math.floor( 10.00 / $rootScope.CREDValue.$value)  ;
        $scope.USDAmountToBuy = 10.00;

        $scope.buycred1bool = false;
        $scope.buycred2bool = true;
        $scope.buycred3bool = false;
        $scope.buycred4bool = false;

        $scope.showChooseAWayToPayButton  = true;
        //$scope.$apply();
      }


      $scope.SelectBuyCred3= function () {
        console.log('buyCred3');
        $scope.CredAmountToBuy = Math.floor( 20.00 / $rootScope.CREDValue.$value) ;
        $scope.USDAmountToBuy = 20.00;

        $scope.buycred1bool = false;
        $scope.buycred2bool = false;
        $scope.buycred3bool = true;
        $scope.buycred4bool = false;

        $scope.showChooseAWayToPayButton  = true;
        //$scope.$apply();
      }


      $scope.SelectBuyCred4= function () {
        console.log('buyCred4');
        $scope.CredAmountToBuy = Math.floor( 40.00 / $rootScope.CREDValue.$value) ;
        $scope.USDAmountToBuy = 40.00;

        $scope.buycred1bool = false;
        $scope.buycred2bool = false;
        $scope.buycred3bool = false;
        $scope.buycred4bool = true;

        $scope.showChooseAWayToPayButton  = true;
        //$scope.$apply();
      }


      $scope.CreateBitPayInvoice = function (USDAmountToBuy) {
        $scope.AmountSelectedBitpay = true;
        $scope.ShowPurchaseOptions = false;
        //$scope.CredAmountToBuy = USDAmountToBuy / $rootScope.CREDValue.$value;
        console.log($scope.CredAmountToBuy);

        endpoints.post('transactions', 'createBitpayInvoice', {'amountBTC': $scope.CredAmountToBuy ,
                                                      }).then(function(resp) {
                                                        if (resp.bitpayurl)
                                                        {
                                                          console.log(resp.bitpayurl);
                                                          $scope.BitPayRedirectUrl = resp.bitpayurl;
                                                          $window.open(resp.bitpayurl, '_blank');
                                                        }



          });
      }

      $scope.CreateBraintreeToken = function () {
        $scope.AmountSelectedBraintree = true;
        $scope.ShowPurchaseOptions = false;
        //$scope.USDAmountToBuy = USDAmountToBuy;
        //$scope.CredAmountToBuy = USDAmountToBuy / $rootScope.CREDValue.$value;
        console.log($scope.CredAmountToBuy);
        $scope.showChooseAWayToPayButton = false;
        $scope.showBraintreeDropIn = true;
        $scope.showTransactionSummary = true;

        endpoints.post('transactions', 'createBraintreeToken', {'amountBTC': $scope.CredAmountToBuy ,
                                                      }).then(function(resp) {
                                                        if (resp.token)
                                                        {
                                                          console.log(resp.token);
                                                          var button = document.querySelector('#submit-button');
                                                          $scope.showConfirmButton = true;

                                                          braintree.setup(resp.token,
                                                              'dropin', {
                                                              container: 'dropin-container',
                                                              onReady: function () {
                                                                console.log('braintree ready');
                                                                $scope.showLoadingPaymentUINotification = false;
                                                                $scope.$apply();
                                                              },
                                                              onPaymentMethodReceived: function (obj) {
                                                                  $scope.$apply(function() {
                                                                      $scope.hasCalledBack = true;
                                                                      //alert('Did the scope variable change? Yes!');
                                                                      console.log(obj);
                                                                      //obj.nonce has the payment nonce that we need to submit back

                                                                      endpoints.post('transactions', 'createBraintreeTransaction', {'payment_method_nonce': obj.nonce ,
                                                                                                                                    'amountUSD': $scope.USDAmountToBuy,
                                                                                                                    }).then(function(resp) {
                                                                                                                      console.log(resp);
                                                                                                                      // check response for success
                                                                                                                      if (resp.response_successful)
                                                                                                                      {
                                                                                                                        $mdDialog.show(
                                                                                                                          $mdDialog.alert()
                                                                                                                            .parent(angular.element(document.querySelector('#popupContainer')))
                                                                                                                            .clickOutsideToClose(true)
                                                                                                                            .title('Payment Successful.')
                                                                                                                            .textContent('Your CRED will be available in your account in a few seconds.')
                                                                                                                            .ariaLabel('CRED Purchase')
                                                                                                                            .ok('Got it!')
                                                                                                                            //.targetEvent(ev)
                                                                                                                        ).finally(function(){
                                                                                                                          console.log('123');
                                                                                                                          $scope.showBraintreeDropIn = false;
                                                                                                                          $scope.showTransactionComplete = true;
                                                                                                                          $scope.showTransactionSummary = false;
                                                                                                                        });
                                                                                                                      }
                                                                                                                      else
                                                                                                                      {
                                                                                                                        $mdDialog.show(
                                                                                                                          $mdDialog.alert()
                                                                                                                            .parent(angular.element(document.querySelector('#popupContainer')))
                                                                                                                            .clickOutsideToClose(true)
                                                                                                                            .title('Payment Fail.')
                                                                                                                            .textContent(resp.response_message)
                                                                                                                            .ariaLabel('CRED Purchase')
                                                                                                                            .ok('Got it!')
                                                                                                                            //.targetEvent(ev)
                                                                                                                        );
                                                                                                                      }
                                                                                                                      // redirect
                                                                                                                      // display dialog if error



                                                                        });
                                                                  });
                                                              }

                                                          });

/*
                                                          braintree.dropin.create({
                                                            authorization: resp.token,
                                                            container: '#dropin-container'
                                                          }, function (createErr, instance) {
                                                            button.addEventListener('click', function () {
                                                              instance.requestPaymentMethod(function (err, payload) {
                                                                // Submit payload.nonce to your server
                                                              });
                                                            });
                                                          });

*/


                                                        }



          });

      }


    }
]);
