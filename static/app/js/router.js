var router = angular.module('uetopiaFrontEnd.router', []);

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
                    title: 'Home',
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
                            controller: 'uetopiaFrontEnd.controller.home',
                            templateUrl: '/app/partials/home.html',

                            },
                        'body@home': { templateUrl: '/app/partials/home.body.html'},
                        'footer@home': { templateUrl: '/app/partials/footer.html' },
                        'console@home': { templateUrl: '/app/partials/console.html' },
                        //'friends@home': { templateUrl: '/app/partials/friends.html' }
                    },
                })

                .state('profile', {
                    url: '/profile',
                    title: 'Profile',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.profile',
                            templateUrl: '/app/partials/user.detail.html',
                        },
                        'nav@profile': { templateUrl: '/app/partials/nav.html' }
                      },
                  })


                  .state('faq', {
                      url: '/faq',
                      title: 'FAQ',
                      views :  {
                          '': {
                              controller: 'uetopiaFrontEnd.controller.faq',
                              templateUrl: '/app/partials/faq.html',
                          },
                          'nav@faq': { templateUrl: '/app/partials/nav.html' }
                        },
                    })

                  .state('api', {
                      url: '/api',
                      title: 'API Documentation',
                      views :  {
                          '': {
                              controller: 'uetopiaFrontEnd.controller.api',
                              templateUrl: '/app/partials/api.html',
                          },
                          'nav@faq': { templateUrl: '/app/partials/nav.html' }
                        },
                    })

                    .state('costs', {
                        url: '/costs',
                        title: 'Usage Costs',
                        views :  {
                            '': {
                                controller: 'uetopiaFrontEnd.controller.costs',
                                templateUrl: '/app/partials/costs.html',
                            },
                            'nav@faq': { templateUrl: '/app/partials/nav.html' }
                          },
                      })








                  .state('agreement', {
                      url: '/agreement',
                      title: 'Agreement',
                      views :  {
                          '': {
                              controller: 'uetopiaFrontEnd.controller.agreement',
                              templateUrl: '/app/partials/user.agreement.html',
                          },
                          'nav@profile': { templateUrl: '/app/partials/nav.html' }
                        },
                    })




                  .state('exposetoken', {
                      url: '/token_login',
                      title: 'Token',
                      resolve: {
                        // controller will not be loaded until $requireSignIn resolves
                        // Auth refers to our $firebaseAuth wrapper in the factory below
                        "currentAuth": ["Auth", function(Auth) {
                          // $requireSignIn returns a promise so the resolve waits for it to complete
                          // If the promise is rejected, it will throw a $stateChangeError (see above)
                          return Auth.$requireSignIn();
                        }]
                      },
                      views :  {
                          '': {
                              controller: 'uetopiaFrontEnd.controller.token.expose',
                              templateUrl: '/app/partials/token.expose.html',
                          },
                        },
                    })

                .state('adminhome', {
                    url :'/admin/',
                    title: 'Admin',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.admin',
                            templateUrl: '/app/partials/admin/index.html',

                            },
                        'adminnav@adminhome': { templateUrl: '/app/partials/admin/admin_nav.html' },
                        'body@adminhome': { templateUrl: '/app/partials/admin/body.html'},
                        'footer@adminhome': { templateUrl: '/app/partials/footer.html' },
                        'console@adminhome': { templateUrl: '/app/partials/console.html' }
                    },
                })

                .state('adminusers', {
                    url :'/admin/users/',
                    title: 'Admin Users',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.admin.users',
                            templateUrl: '/app/partials/admin/users.html',
                        },
                        'nav@adminusers': { templateUrl: '/app/partials/nav.html' },
                    },
                })

                .state('adminuserdetail', {
                    url :'/admin/users/:key_id',
                    title: 'Admin User Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.admin.user.detail',
                            templateUrl: '/app/partials/admin/user.detail.html',
                        },
                        'nav@adminuserdetail': { templateUrl: '/app/partials/nav.html' },
                    },
                })

                .state('admingames', {
                    url :'/admin/games/',
                    title: 'Admin Games',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.admin.games',
                            templateUrl: '/app/partials/admin/games.html',
                        },
                    },
                })

                .state('admingamedetail', {
                    url :'/admin/games/:key_id',
                    title: 'Admin Game Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.admin.game',
                            templateUrl: '/app/partials/admin/game.detail.html',
                        },
                    },
                })

                .state('adminserverdetail', {
                    url :'/admin/games/:gameKeyId/server/:key_id',
                    title: 'Admin Server Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.admin.server',
                            templateUrl: '/app/partials/admin/server.detail.html',
                        },
                    },
                })

                // DEVELOPER

                .state('developerhome', {
                    url :'/developer/',
                    title: 'Developer Home',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer',
                            templateUrl: '/app/partials/developer/index.html',

                            },
                        'nav@developerhome': { templateUrl: '/app/partials/nav.html' },
                        'body@developerhome': { templateUrl: '/app/partials/developer/body.html'},
                        'footer@developerhome': { templateUrl: '/app/partials/footer.html' },
                        'console@developerhome': { templateUrl: '/app/partials/console.html' }
                    },
                })



                .state('developerdocumentation', {
                    url :'/developer/documentation',
                    title: 'Developer Documentation',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.documentation',
                            templateUrl: '/app/partials/developer/documentation.html',
                        },
                        'nav@developerdocumentation': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergamecreate', {
                    url :'/developer/game/create',
                    title: 'Developer Game Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.create',
                            templateUrl: '/app/partials/developer/game.create.html',
                        },
                        'nav@developergamecreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergamedetail', {
                    url: '/developer/game/:key_id',
                    title: 'Developer Game Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game',
                            templateUrl: '/app/partials/developer/game.detail.html',
                        },
                        'nav@developergamedetail': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                // Developer Game Mode

                .state('developergamemodecreate', {
                    url :'/developer/game/:gameKeyId/mode/create',
                    title: 'Developer Game Mode Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.mode.create',
                            templateUrl: '/app/partials/developer/game.mode.create.html',
                        },
                        'nav@developergamemodecreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergamemodedetail', {
                    url :'/developer/game/:gameKeyId/mode/:key_id',
                    title: 'Developer Game Mode',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.gameMode',
                            templateUrl: '/app/partials/developer/game.mode.html',
                        },
                        'nav@developergamemodecreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergamemodead', {
                    url : '/developer/game/:gameKeyId/mode/:gameModeKeyId/ad/:key_id',
                    title: 'Developer Game Mode Ad',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.gameModeAd',
                            templateUrl: '/app/partials/developer/game.mode.ad.html',
                        },
                        'nav@developergamemodead': { templateUrl: '/app/partials/nav.html' }
                    },
                })



                // Developer Game Level


                .state('developergamelevelcreate', {
                    url :'/developer/game/:gameKeyId/level/create',
                    title: 'Developer Game Level Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.level.create',
                            templateUrl: '/app/partials/developer/game.level.create.html',
                        },
                        'nav@developergamelevelcreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergameleveldetail', {
                    url :'/developer/game/:gameKeyId/level/:key_id',
                    title: 'Developer Game Level',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.gameLevel',
                            templateUrl: '/app/partials/developer/game.level.html',
                        },
                        'nav@developergamelevelcreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                // Developer Game Level Link

                .state('developergamelevellinkcreate', {
                    url :'/developer/game/:gameKeyId/level/:gameLevelKeyId/link/create',
                    title: 'Developer Game Level Link Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.level.link.create',
                            templateUrl: '/app/partials/developer/game.level.link.create.html',
                        },
                        'nav@developergamelevellinkcreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergamelevellinkdetail', {
                    url :'/developer/game/:gameKeyId/level/:gameLevelKeyId/link/:key_id',
                    title: 'Developer Game Level Link',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.gameLevelLink',
                            templateUrl: '/app/partials/developer/game.level.link.html',
                        },
                        'nav@developergamelevellinkcreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                // Developer Game Data

                .state('developergamedatacreate', {
                    url :'/developer/game/:gameKeyId/data/create',
                    title: 'Developer Game Data Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.data.create',
                            templateUrl: '/app/partials/developer/game.data.create.html',
                        },
                        'nav@developergamedatacreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergamedatadetail', {
                    url :'/developer/game/:gameKeyId/data/:key_id',
                    title: 'Developer Game Data',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.gameData',
                            templateUrl: '/app/partials/developer/game.data.html',
                        },
                        'nav@developergamedatadetail': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                // Developer Game Players

                .state('developergameplayers', {
                    url :'/developer/game/:gameKeyId/players/',
                    title: 'Developer Game Players',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.players',
                            templateUrl: '/app/partials/developer/game.players.html',
                        },
                        'nav@developergameplayers': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergameplayerdetail', {
                    url :'/developer/game/:gameKeyId/players/:gamePlayerKeyId',
                    title: 'Developer Game Players',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.player.detail',
                            templateUrl: '/app/partials/developer/game.player.detail.html',
                        },
                        'nav@developergameplayerdetail': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergamecharacterdetail', {
                    url :'/developer/game/:gameKeyId/players/:gamePlayerKeyId/characters/:gameCharacterKeyId',
                    title: 'Developer Game Character',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.character.detail',
                            templateUrl: '/app/partials/developer/game.character.detail.html',
                        },
                        'nav@developergamecharacterdetail': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergameplayersnapshotdetail', {
                    url :'/developer/game/:gameKeyId/players/:gamePlayerKeyId/snapshots/:gamePlayerSnapshotKeyId',
                    title: 'Developer Game Player Snapshot',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.player.snapshot.detail',
                            templateUrl: '/app/partials/developer/game.player.snapshot.detail.html',
                        },
                        'nav@developergamecharacterdetail': { templateUrl: '/app/partials/nav.html' }
                    },
                })


                // Developer Game Offers
                .state('developergameoffers', {
                    url :'/developer/game/:gameKeyId/offers/',
                    title: 'Developer Game Offers',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.offers',
                            templateUrl: '/app/partials/developer/game.offers.html',
                        },
                        'nav@developergameoffers': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergameoffercreate', {
                    url :'/developer/game/:gameKeyId/offer_create',
                    title: 'Developer Game Offer Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.offer.create',
                            templateUrl: '/app/partials/developer/game.offer.create.html',
                        },
                        'nav@developergameoffercreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergameofferdetail', {
                    url :'/developer/game/:gameKeyId/offers/:offerKeyId',
                    title: 'Developer Game Offer Edit',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.offer',
                            templateUrl: '/app/partials/developer/game.offer.detail.html',
                        },
                        'nav@developergameoffer': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                // Developer Game Vouchers

                .state('developergamevouchercreate', {
                    url :'/developer/game/:gameKeyId/offers/:offerKeyId/voucher_create',
                    title: 'Developer Game Voucher Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.voucher.create',
                            templateUrl: '/app/partials/developer/game.voucher.create.html',
                        },
                        'nav@developergamevouchercreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergamevoucherdetail', {
                    url :'/developer/game/:gameKeyId/offers/:offerKeyId/vouchers/:voucherKeyId',
                    title: 'Developer Game Voucher Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.voucher',
                            templateUrl: '/app/partials/developer/game.voucher.detail.html',
                        },
                        'nav@developergamevoucherdetail': { templateUrl: '/app/partials/nav.html' }
                    },
                })


                // Developer Game Consignments



                .state('developergameconsignments', {
                    url :'/developer/game/:gameKeyId/consignments/',
                    title: 'Developer Game Consignments',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.consignments',
                            templateUrl: '/app/partials/developer/game.consignments.html',
                        },
                        'nav@developergameconsignments': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergameconsignmentcreate', {
                    url :'/developer/game/:gameKeyId/consignment_create',
                    title: 'Developer Game Consignment Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.consignment.create',
                            templateUrl: '/app/partials/developer/game.consignment.create.html',
                        },
                        'nav@developergameconsignmentcreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developergameconsignmentdetail', {
                    url :'/developer/game/:gameKeyId/consignments/:consignmentKeyId',
                    title: 'Developer Game Consignment Edit',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.consignment',
                            templateUrl: '/app/partials/developer/game.consignment.detail.html',
                        },
                        'nav@developergameconsignment': { templateUrl: '/app/partials/nav.html' }
                    },
                })






                // Developer Server Cluster

                .state('developerserverclustercreate', {
                    url :'/developer/game/:gameKeyId/servercluster/create',
                    title: 'Developer Server Cluster Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.servercluster.create',
                            templateUrl: '/app/partials/developer/servercluster.create.html',
                        },
                        'nav@developerserverclustercreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developerserverclusterdetail', {
                    url :'/developer/game/:gameKeyId/servercluster/:key_id',
                    title: 'Developer Server Cluster Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.servercluster',
                            templateUrl: '/app/partials/developer/servercluster.detail.html',
                        },
                        'nav@developerserverclusterdetail': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                // Developer Server

                .state('developerservercreate', {
                    url :'/developer/game/:gameKeyId/servercluster/:serverClusterKeyId/server/create',
                    title: 'Developer Server Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.server.create',
                            templateUrl: '/app/partials/developer/server.create.html',
                        },
                        'nav@developerservercreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developerserverdetail', {
                    url :'/developer/game/:gameKeyId/servercluster/:serverClusterKeyId/server/:key_id',
                    title: 'Developer Server Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.server',
                            templateUrl: '/app/partials/developer/server.detail.html',
                        },
                        'nav@developerserverdetail': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developerserverlinkcreate', {
                    url :'/developer/game/:gameKeyId/servercluster/:serverClusterKeyId/server/:serverKeyId/link/create',
                    title: 'Developer Server Link Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.serverlink.create',
                            templateUrl: '/app/partials/developer/serverlink.create.html',
                        },
                        'nav@developerserverlinkcreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developerserverlinkdetail', {
                    url :'/developer/game/:gameKeyId/servercluster/:serverClusterKeyId/server/:serverKeyId/link/:key_id',
                    title: 'Developer Server Link Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.serverlink',
                            templateUrl: '/app/partials/developer/serverlink.detail.html',
                        },
                        'nav@developerserverlinkdetail': { templateUrl: '/app/partials/nav.html' }
                    },
                })


                .state('developervendortypecreate', {
                    url :'/developer/game/:gameKeyId/vendortypes/create',
                    title: 'Developer Server Link Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.vendor.type.create',
                            templateUrl: '/app/partials/developer/vendor.type.create.html',
                        },
                        'nav@developervendortypecreate': { templateUrl: '/app/partials/nav.html' }
                    },
                })

                .state('developervendortypedetail', {
                    url :'/developer/game/:gameKeyId/vendortypes/:key_id',
                    title: 'Developer Vendor Type Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.vendor.type',
                            templateUrl: '/app/partials/developer/vendor.type.detail.html',
                        },
                        'nav@developervendortypedetail': { templateUrl: '/app/partials/nav.html' }
                    },
                })


                // DEVELOPER GAME PATCH
                .state('developergamepatch', {
                    url :'/developer/game/:gameKeyId/patch',
                    title: 'Developer Game Patch',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.developer.game.patch.deploy',
                            templateUrl: '/app/partials/developer/game.patch.html',
                        },
                        'nav@developergamepatch': { templateUrl: '/app/partials/nav.html' }
                    },
                })





                // TOURNAMENT

                .state('tournamentcreate', {
                    url: '/game/:key_id/tournament/create',
                    title: 'Tournament Create',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.tournament.create',
                            templateUrl: '/app/partials/games/tournaments/create.html',
                        },
                        'nav@tournamentcreate': { templateUrl: '/app/partials/nav.html' }
                      },
                  })

                .state('tournamentdetail', {
                    url: '/game/:gameKeyId/tournament/:key_id',
                    title: 'Tournament Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.tournament',
                            templateUrl: '/app/partials/games/tournaments/tournament.detail.html',
                        },
                        'nav@tournamentdetail': { templateUrl: '/app/partials/nav.html' }
                      },
                  })

                // GAME

                .state('gamedetail', {
                    url: '/game/:key_id',
                    title: 'Game Detail',
                    views :  {
                        '': {
                            controller: 'uetopiaFrontEnd.controller.game',
                            templateUrl: '/app/partials/games/game.detail.html',
                        },
                        'nav@gamedetail': { templateUrl: '/app/partials/nav.html' }
                      },
                  })



                  .state('gameplayerdetail', {
                      url: '/game/:key_id/play',
                      title: 'Game Player Detail',
                      views :  {
                          '': {
                              controller: 'uetopiaFrontEnd.controller.game.player',
                              templateUrl: '/app/partials/games/players/player.detail.html',
                          },
                          'nav@gameplayerdetail': { templateUrl: '/app/partials/nav.html' }
                        },
                    })


                    .state('gamemetagameconnect', {
                        url: '/game/:key_id/metagame/connect',
                        title: 'Game MetaGame Connect',
                        views :  {
                            '': {
                                controller: 'uetopiaFrontEnd.controller.game.metagame.connect',
                                templateUrl: '/app/partials/games/metagame.connect.html',
                            },
                            'nav@gamemetagameconnect': { templateUrl: '/app/partials/nav.html' }
                          },
                      })

                      // SERVERCLUSTER

                      .state('clusterdetail', {
                          url: '/game/:gameKeyId/cluster/:key_id',
                          title: 'Server Cluster Detail',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.servercluster',
                                  templateUrl: '/app/partials/games/clusters/cluster.detail.html',
                              },
                              'nav@clusterdetail': { templateUrl: '/app/partials/nav.html' }
                            },
                        })







                    // SERVER

                    .state('serverdetail', {
                        url: '/game/:gameKeyId/cluster/:clusterKeyId/server/:key_id',
                        title: 'Server Detail',
                        views :  {
                            '': {
                                controller: 'uetopiaFrontEnd.controller.server',
                                templateUrl: '/app/partials/servers/server.detail.html',
                            },
                            'nav@serverdetail': { templateUrl: '/app/partials/nav.html' }
                          },
                      })

                      .state('serverplayerdetail', {
                          url: '/game/:gameKeyId/server/:key_id/play',
                          title: 'Server Player Detail',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.server.player',
                                  templateUrl: '/app/partials/servers/players/player.detail.html',
                              },
                              'nav@gameplayerdetail': { templateUrl: '/app/partials/nav.html' }
                            },
                        })


                    // USER
                    .state('usertransactiondetail', {
                        url: '/user/transactions',
                        title: 'My Transactions',
                        views :  {
                            '': {
                                controller: 'uetopiaFrontEnd.controller.user.transactions',
                                templateUrl: '/app/partials/users/transactions.html',
                            },
                          },
                      })

                      .state('usersearch', {
                          url: '/user/search',
                          title: 'Search for a user',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.user.search',
                                  templateUrl: '/app/partials/users/search.html',
                              },
                            },
                        })

                        .state('userprofile', {
                            url: '/user/:key_id',
                            title: 'User Profile',
                            views :  {
                                '': {
                                    controller: 'uetopiaFrontEnd.controller.user.profile',
                                    templateUrl: '/app/partials/users/profile.html',
                                },
                              },
                          })

                        .state('userreferral', {
                            url: '/user/:key_id/referral',
                            title: 'User refarral',
                            views :  {
                                '': {
                                    controller: 'uetopiaFrontEnd.controller.user.referral',
                                    templateUrl: '/app/partials/users/referral.html',
                                },
                              },
                          })

                        .state('usercredbuy', {
                            url: '/user/cred/buy',
                            title: 'Get More CRED',
                            views :  {
                                '': {
                                    controller: 'uetopiaFrontEnd.controller.user.cred.buy',
                                    templateUrl: '/app/partials/users/cred.buy.html',
                                },
                              },
                          })

                          .state('userbadges', {
                              url: '/user_badges',
                              title: 'Badge List',
                              views :  {
                                  '': {
                                      controller: 'uetopiaFrontEnd.controller.user.badges',
                                      templateUrl: '/app/partials/users/badges.html',
                                  },
                                },
                            })

                            .state('userbadgedetail', {
                                url: '/user_badges/:key_id',
                                title: 'Badge Detail',
                                views :  {
                                    '': {
                                        controller: 'uetopiaFrontEnd.controller.user.badge.detail',
                                        templateUrl: '/app/partials/users/badge.detail.html',
                                    },
                                  },
                              })






                    // VOUCHERS

                    .state('voucherredeem', {
                        url: '/user/voucher/redeem',
                        title: 'Redeem a voucher',
                        views :  {
                            '': {
                                controller: 'uetopiaFrontEnd.controller.voucher.redeem',
                                templateUrl: '/app/partials/users/voucher.redeem.html',
                            },
                          },
                      })


                    .state('offerclaim', {
                        url: '/user/offer/:offerKeyId/claim',
                        title: 'Claim an offer',
                        views :  {
                            '': {
                                controller: 'uetopiaFrontEnd.controller.offer.claim',
                                templateUrl: '/app/partials/users/offer.claim.html',
                            },
                          },
                      })






                    // GROUPS


                      .state('groups', {
                          url: '/groups/',
                          title: 'Groups',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.groups',
                                  templateUrl: '/app/partials/groups/list.html',
                              },
                            },
                        })

                      .state('groupcreate', {
                          url: '/groups/create',
                          title: 'Group Create',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.group.create',
                                  templateUrl: '/app/partials/groups/create.html',
                              },
                            },
                        })


                      .state('groupdetail', {
                          url: '/groups/:key_id',
                          title: 'Group Detail',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.group',
                                  templateUrl: '/app/partials/groups/detail.html',
                              },
                              'nav@groupdetail': { templateUrl: '/app/partials/nav.html' }
                            },
                        })

                      .state('grouproledetail', {
                          url: '/groups/:key_id/roles/:roleKeyId',
                          title: 'Group Role Detail',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.group.role.detail',
                                  templateUrl: '/app/partials/groups/roles/detail.html',
                              },
                              'nav@groupdetail': { templateUrl: '/app/partials/nav.html' }
                            },
                        })

                      .state('groupuserdetail', {
                          url: '/groups/:key_id/users/:userKeyId',
                          title: 'Group User Detail',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.group.user.detail',
                                  templateUrl: '/app/partials/groups/users/detail.html',
                              },
                              'nav@groupuserdetail': { templateUrl: '/app/partials/nav.html' }
                            },
                        })

                        .state('groupgamecreate', {
                            url: '/groups/:key_id/games/',
                            title: 'Group Game Create',
                            views :  {
                                '': {
                                    controller: 'uetopiaFrontEnd.controller.group.game.create',
                                    templateUrl: '/app/partials/groups/games/create.html',
                                },
                                'nav@groupgamecreate': { templateUrl: '/app/partials/nav.html' }
                              },
                          })

                      .state('groupgamedetail', {
                          url: '/groups/:key_id/games/:groupGameKeyId',
                          title: 'Group Game Detail',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.group.game.detail',
                                  templateUrl: '/app/partials/groups/games/detail.html',
                              },
                              'nav@groupgamedetail': { templateUrl: '/app/partials/nav.html' }
                            },
                        })

                      .state('groupadcreate', {
                          url: '/groups/:key_id/games/:groupGameKeyId/ad_create',
                          title: 'Group Ad Create',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.group.ad.create',
                                  templateUrl: '/app/partials/groups/ads/create.html',
                              },
                              'nav@groupadcreate': { templateUrl: '/app/partials/nav.html' }
                            },
                        })

                      .state('groupaddetail', {
                          url: '/groups/:groupKeyId/games/:groupGameKeyId/ad/:key_id',
                          title: 'Group Ad Detail',
                          views :  {
                              '': {
                                  controller: 'uetopiaFrontEnd.controller.group.ad.detail',
                                  templateUrl: '/app/partials/groups/ads/detail.html',
                              },
                              'nav@groupaddetail': { templateUrl: '/app/partials/nav.html' }
                            },
                        })


                        //// BLOG

                        .state('blogpostlist', {
                            url: '/blog/',
                            title: 'Blog',
                            views :  {
                                '': {
                                    controller: 'uetopiaFrontEnd.controller.blog.posts',
                                    templateUrl: '/app/partials/blog/posts/list.html',
                                },
                                'nav@groupaddetail': { templateUrl: '/app/partials/nav.html' }
                              },
                          })

                          .state('blogpostcreate', {
                              url: '/blog_post_create',
                              title: 'Blog Post Create',
                              views :  {
                                  '': {
                                      controller: 'uetopiaFrontEnd.controller.developer.blog.post.create',
                                      templateUrl: '/app/partials/blog/posts/create.html',
                                  },
                                  'nav@groupaddetail': { templateUrl: '/app/partials/nav.html' }
                                },
                            })


                            .state('blogpost', {
                                url: '/blog/:slugify_url',
                                title: 'Blog Post',
                                views :  {
                                    '': {
                                        controller: 'uetopiaFrontEnd.controller.blog.post',
                                        templateUrl: '/app/partials/blog/posts/post.html',
                                    },
                                    'nav@groupaddetail': { templateUrl: '/app/partials/nav.html' }
                                  },
                              })





















    }])
