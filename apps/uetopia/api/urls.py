from webapp2 import Route

routes = [
    Route('/api/v1/server/info', 'apps.uetopia.api.v1.server.info.InfoHandler', name="api-server"),
    Route('/api/v1/server/links', 'apps.uetopia.api.v1.server.links.get_list.GetLinksHandler', name="api-get-server-links"),
    Route('/api/v1/server/links/<serverKeyId>/mount', 'apps.uetopia.api.v1.server.links.mount.MountLinkHandler', name="api-mount-server-links"),
    Route('/api/v1/server/down_ready', 'apps.uetopia.api.v1.server.down_ready.DownReadyHandler', name="api-server-down-ready"),
    Route('/api/v1/server/report', 'apps.uetopia.api.v1.server.results.PutMatchResultsHandler', name="api-server-report"),

    ##Route('/api/v1/server/credentials', 'apps.uetopia.api.v1.server.credentials.CredentialsHandler', name="api-server-credentials"),
    Route('/api/v1/server/player/<userid>/activate', 'apps.uetopia.api.v1.server.player.activate.ActivatePlayerHandler', name="api-server-player-activate"),
    Route('/api/v1/server/player/<userid>/deactivate', 'apps.uetopia.api.v1.server.player.deactivate.DeactivatePlayerHandler', name="api-server-player-deactivate"),
    Route('/api/v1/server/player/<userid>/purchase', 'apps.uetopia.api.v1.server.player.purchase.serverPlayerPurchaseHandler', name="api-server-player-purchase"),
    Route('/api/v1/server/player/<userid>/reward', 'apps.uetopia.api.v1.server.player.reward.serverPlayerRewardHandler', name="api-server-player-reward"),
    Route('/api/v1/server/<targetServerKeyId>/player/<userid>/transfer', 'apps.uetopia.api.v1.server.player.transfer.TransferPlayerHandler', name="api-server-transfer-player"),
    Route('/api/v1/game/player/<gamePlayerKeyId>', 'apps.uetopia.api.v1.game.player.get.gamePlayerGetHandler', name="api-game-user-get"),
    Route('/api/v1/game/player/<gamePlayerKeyId>/update', 'apps.uetopia.api.v1.game.player.update.gamePlayerUpdateHandler', name="api-game-user-update"),


    # /Users/ed/appengine_projects/ue4t/apps/uetopia/api/v1/game/user_region_change.py
    Route('/api/v1/user/regionChange', 'apps.uetopia.api.v1.game.player.user_region_change.UserRegionChangeHandler', name="api-user-region-change"),

    ## MATCHMAKER
    Route('/api/v1/matchmaker/info', 'apps.uetopia.api.v1.game.matchmaker.info.InfoHandler', name="api-matchmaker-info"),
    Route('/api/v1/match/player/<userid>/activate', 'apps.uetopia.api.v1.game.matchmaker.player.activate.ActivateMatchPlayerHandler', name="api-matchmaker-player-activate"),
    Route('/api/v1/matchmaker/results', 'apps.uetopia.api.v1.game.matchmaker.results.PutMatchMakerResutlsHandler', name="api-matchmaker-results"),

    ## METAGAME
    Route('/api/v1/game/metagame/verify', 'apps.uetopia.api.v1.game.metagame.player_validate.gamePlayerValidateHandler', name="api-metagame-player-verify"),
    Route('/api/v1/game/metagame/match_begin', 'apps.uetopia.api.v1.game.metagame.match_begin.matchBeginHandler', name="api-metagame-match-begin"),
    Route('/api/v1/game/metagame/user/get', 'apps.uetopia.api.v1.game.metagame.player_data_get.playerDataGetHandler', name="api-metagame-player-data-get"),
    Route('/api/v1/game/metagame/user/update', 'apps.uetopia.api.v1.game.metagame.player_data_update.playerDataUpdateHandler', name="api-metagame-player-data-update"),

    ## DROPS
    Route('/api/v1/game/player/<gamePlayerKeyId>/drops/create', 'apps.uetopia.api.v1.game.player.drops.create.createDropHandler', name="api-game-player-drop-create"),
    Route('/api/v1/game/drops/', 'apps.uetopia.api.v1.game.player.drops.list.dropListHandler', name="api-game-player-drop-list"),
    Route('/api/v1/game/drops/<dropKeyId>', 'apps.uetopia.api.v1.game.player.drops.claim.dropClaimHandler', name="api-game-player-drop-claim"),

    ## GKP
    Route('/api/v1/server/groups/gkp/start', 'apps.uetopia.api.v1.server.groups.gkp.start.serverGroupGKPStartHandler', name="api-server-group-gkp-start"),
    Route('/api/v1/server/groups/gkp/end', 'apps.uetopia.api.v1.server.groups.gkp.end.serverGroupGKPEndHandler', name="api-server-group-gkp-end"),

    ## Party/Team
    Route('/api/v1/server/team/getUserTeam', 'apps.uetopia.api.v1.server.team.getUserTeam.GetUserTeamHandler', name="api-server-team-get"),


    # VENDORS
    Route('/api/v1/server/vendor/create', 'apps.uetopia.api.v1.server.vendors.create.CreateVendorHandler', name="api-server-vendor-create"),
    Route('/api/v1/server/vendor/<vendorKeyId>', 'apps.uetopia.api.v1.server.vendors.get.GetVendorHandler', name="api-server-vendor-get"),
    Route('/api/v1/server/vendor/<vendorKeyId>/update', 'apps.uetopia.api.v1.server.vendors.update.UpdateVendorHandler', name="api-server-vendor-update"),
    Route('/api/v1/server/vendor/<vendorKeyId>/delete', 'apps.uetopia.api.v1.server.vendors.delete.DeleteVendorHandler', name="api-server-vendor-delete"),
    Route('/api/v1/server/vendor/<vendorKeyId>/withdraw', 'apps.uetopia.api.v1.server.vendors.withdraw.WithdrawFromVendorHandler', name="api-server-vendor-withdraw"),
    Route('/api/v1/server/vendor/<vendorKeyId>/item/create', 'apps.uetopia.api.v1.server.vendors.items.create.CreateVendorItemHandler', name="api-server-vendor-item-create"),
    Route('/api/v1/server/vendor/<vendorKeyId>/item/<vendorItemKeyId>/delete', 'apps.uetopia.api.v1.server.vendors.items.delete.DeleteVendorItemHandler', name="api-server-vendor-item-delete"),
    Route('/api/v1/server/vendor/<vendorKeyId>/item/<vendorItemKeyId>/buy', 'apps.uetopia.api.v1.server.vendors.items.buy.BuyVendorItemHandler', name="api-server-vendor-item-buy"),
    Route('/api/v1/server/vendor/<vendorKeyId>/item/<vendorItemKeyId>/decline', 'apps.uetopia.api.v1.server.vendors.items.decline_offer.DeclineVendorItemOfferHandler', name="api-server-vendor-item-decline"),
    Route('/api/v1/server/vendor/<vendorKeyId>/item/<vendorItemKeyId>/claim', 'apps.uetopia.api.v1.server.vendors.items.claim.ClaimVendorItemHandler', name="api-server-vendor-item-claim"),

    ## Game Data
    Route('/api/v1/game/data/', 'apps.uetopia.api.v1.game.data.get_list.GetDataListHandler', name="api-game-data-get-list"),
    Route('/api/v1/game/data/<key_id_str>', 'apps.uetopia.api.v1.game.data.get.GetDataHandler', name="api-game-data-get"),


    ## Unprotected Public
    ## For UEtopia Online Subsystem
    Route('/api/v1/game/<gameKeyId>/servers/', 'apps.uetopia.api.v1.game.servers.GetServersHandler', name="api-game-servers"),
    Route('/api/v1/game/<gameKeyId>/servers/<userKeyId>', 'apps.uetopia.api.v1.game.user_servers.UserServersHandler', name="api-user-servers"),
    Route('/api/v1/game/<gameKeyId>/matchmaker/start', 'apps.uetopia.api.v1.game.matchmaker.start.MatchmakerStartHandler', name="api-game-matchmaker-start"),
    Route('/api/v1/game/<gameKeyId>/matchmaker/cancel', 'apps.uetopia.api.v1.game.matchmaker.cancel.MatchmakerCancelHandler', name="api-game-matchmaker-cancel"),
    Route('/api/v1/game/<gameKeyId>/matchmaker/check', 'apps.uetopia.api.v1.game.matchmaker.check.MatchmakerCheckHandler', name="api-game-matchmaker-check"),

    ## Webhooks
    Route('/webhooks/onDisconnect','apps.uetopia.handlers.webhooks.on_disconnect.OnDisconnectHandler', name='webhook-on-disconnect'),
    Route('/webhooks/onConnect','apps.uetopia.handlers.webhooks.on_connect.OnConnectHandler', name='webhook-on-connect'),

    ]
