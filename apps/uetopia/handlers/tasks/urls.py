from webapp2 import Route

routes = [

    ## SERVER/VM
    Route('/task/server/vm/allocate', 'apps.uetopia.handlers.tasks.server.vm.allocate.TaskAllocate', name='task-server-vm-allocate'),
    Route('/task/server/vm/deallocate', 'apps.uetopia.handlers.tasks.server.vm.deallocate.TaskDeallocate', name='task-server-vm-deallocate'),
    Route('/task/server/vm/waitfordone', 'apps.uetopia.handlers.tasks.server.vm.wait_for_done.TaskWaitForDone', name='task-server-vm-wait-for-done'),
    Route('/task/server/vm/checkunused', 'apps.uetopia.handlers.tasks.server.vm.check_unused.TaskCheckUnused', name='task-server-vm-check-unused'),

    ## SERVER/player
    Route('/task/server/player/deauthorize', 'apps.uetopia.handlers.tasks.server.players.deauthorize.TaskServerDeauthorize', name='task-server-deauthorize'),
    Route('/task/server/player/deactivate_all', 'apps.uetopia.handlers.tasks.server.players.deactivate_all.TaskServerDeactivateAll', name='task-server-deactivate-all'),

    ## MATCHMAKER
    Route('/task/game/match/queue/process', 'apps.uetopia.handlers.tasks.games.matches.queue_process.MatchQueueProcessHandler', name='task-game-match-queue-process'),
    Route('/task/game/match/matchmaker_complete', 'apps.uetopia.handlers.tasks.games.matches.matchmaker_complete.MatchMakerCompleteHandler', name='task-matchmaker-complete'),

    ## Server Manager
    Route('/task/game/servercluster/shardmanager', 'apps.uetopia.handlers.tasks.games.server_cluster_manager.GameServerClusterManagerHandler', name='task-game-server-cluster-manager'),

    ## Patcher
    Route('/task/game/patch/apply', 'apps.uetopia.handlers.tasks.games.patch_apply.PatchApplyHandler', name='task-game-patch-apply'),

    ## MATCHMAKER/VM
    Route('/task/matchmaker/vm/allocate', 'apps.uetopia.handlers.tasks.games.matches.vm.allocate.TaskAllocate', name='task-games-matches-vm-allocate'),
    Route('/task/matchmaker/vm/deallocate', 'apps.uetopia.handlers.tasks.games.matches.vm.deallocate.TaskDeallocate', name='task-games-matches-vm-deallocate'),
    Route('/task/matchmaker/vm/waitfordone', 'apps.uetopia.handlers.tasks.games.matches.vm.wait_for_done.TaskWaitForDone', name='task-games-matches-vm-wait-for-done'),
    Route('/task/matchmaker/vm/checkunused', 'apps.uetopia.handlers.tasks.games.matches.vm.check_unused.TaskCheckUnused', name='task-games-matches-vm-check-unused'),
    Route('/task/matchmaker/local_clear_key_secret', 'apps.uetopia.handlers.tasks.games.matches.match_local_clear_key_secret.MatchLocalClearKeySecretHandler', name='task-games-matches-local-clear-secret'),



    ## firebase tasks
    Route('/task/user/firebase/update','apps.uetopia.handlers.tasks.user.firebase_update.UserUpdateFirebaseHandler', name='task-user-firebase-update'),
    Route('/task/user/alert/create','apps.uetopia.handlers.tasks.user.alert_create.UserAlertCreateHandler', name='task-user-alert-create'),
    Route('/task/user/friends/firebase/update','apps.uetopia.handlers.tasks.user.friends.firebase_update.FriendUpdateFirebaseHandler', name='task-user-friends-firebase-update'),


    Route('/task/game/firebase/update','apps.uetopia.handlers.tasks.games.firebase_update.GameUpdateFirebaseHandler', name='task-game-firebase-update'),
    Route('/task/game/player/firebase/update','apps.uetopia.handlers.tasks.games.players.firebase_update.GamePlayerUpdateFirebaseHandler', name='task-game-player-firebase-update'),
    Route('/task/game/delete','apps.uetopia.handlers.tasks.games.delete.GameDeleteHandler', name='task-game-delete'),

    # game batch renaming tasks
    Route('/task/game/rename','apps.uetopia.handlers.tasks.games.rename.GameRenameHandler', name='task-game-rename'),
    Route('/task/group/game_batch_rename','apps.uetopia.handlers.tasks.groups.games.game_batch_rename.GamePlayerRenameHandler', name='task-group-game-rename'),
    Route('/task/game/players/game_batch_rename','apps.uetopia.handlers.tasks.games.players.game_batch_rename.GamePlayerRenameHandler', name='task-game-player-batch-rename'),
    Route('/task/server/game_batch_rename','apps.uetopia.handlers.tasks.server.game_batch_rename.ServerGameRenameHandler', name='task-server-game-rename'),

    # user batch renaming tasks
    Route('/task/game/player/user_batch_rename','apps.uetopia.handlers.tasks.games.players.user_batch_rename.GamePlayerUserRenameHandler', name='task-game-player-user-batch-rename'),

    ## firebase eventfeed
    Route('/task/game/events/update','apps.uetopia.handlers.tasks.games.events.firebase_update.GameEventUpdateFirebaseHandler', name='task-game-events-firebase-update'),
    Route('/task/group/events/update','apps.uetopia.handlers.tasks.groups.events.firebase_update.GroupEventUpdateFirebaseHandler', name='task-group-events-firebase-update'),
    Route('/task/user/events/update','apps.uetopia.handlers.tasks.user.events.firebase_update.UserEventUpdateFirebaseHandler', name='task-user-events-firebase-update'),
    Route('/task/game/cluster/events/update','apps.uetopia.handlers.tasks.games.server_clusters.eventfeed_firebase_update.ClusterEventUpdateFirebaseHandler', name='task-cluster-events-firebase-update'),

    ## firebase update
    Route('/task/servercluster/firebase/update','apps.uetopia.handlers.tasks.games.server_clusters.firebase_update.ServerClusterUpdateFirebaseHandler', name='task-servercluster-firebase-update'),
    Route('/task/server/firebase/update','apps.uetopia.handlers.tasks.server.firebase_update.ServerUpdateFirebaseHandler', name='task-server-firebase-update'),
    Route('/task/server/player/firebase/update','apps.uetopia.handlers.tasks.server.players.firebase_update.ServerPlayerUpdateFirebaseHandler', name='task-server-player-firebase-update'),
    Route('/task/group/firebase/update','apps.uetopia.handlers.tasks.groups.firebase_update.GroupUpdateFirebaseHandler', name='task-group-firebase-update'),
    Route('/task/group/user/firebase/update','apps.uetopia.handlers.tasks.groups.users.firebase_update.GroupUserUpdateFirebaseHandler', name='task-group-user-firebase-update'),
    Route('/task/group/game/firebase/update','apps.uetopia.handlers.tasks.groups.games.firebase_update.GroupGameUpdateFirebaseHandler', name='task-group-game-firebase-update'),

    Route('/task/tournament/push','apps.uetopia.handlers.tasks.games.tournament.push.TournamentPushHandler', name='task-tournament-push'),

    ## transactions
    Route('/task/server/transaction/process','apps.uetopia.handlers.tasks.server.transaction_queue_process.ServerTransactionQueueProcessHandler', name='task-server-transaction-process'),
    Route('/task/user/transaction/process','apps.uetopia.handlers.tasks.user.transaction_queue_process.UserTransactionQueueProcessHandler', name='task-user-transaction-process'),
    Route('/task/game/transaction/process','apps.uetopia.handlers.tasks.games.transaction_queue_process.GameTransactionQueueProcessHandler', name='task-game-transaction-process'),
    Route('/task/group/transaction/process','apps.uetopia.handlers.tasks.groups.transaction_queue_process.GroupTransactionQueueProcessHandler', name='task-group-transaction-process'),

    Route('/task/server/player/transaction/process','apps.uetopia.handlers.tasks.server.players.transaction_queue_process.ServerPlayerTransactionQueueProcessHandler', name='task-server-player-transaction-process'),
    Route('/task/vendor/transaction/process','apps.uetopia.handlers.tasks.vendor.transaction_queue_process.VendorTransactionQueueProcessHandler', name='task-vendor-transaction-process'),
    Route('/task/ad/transaction/process','apps.uetopia.handlers.tasks.ads.transaction_queue_process.AdTransactionQueueProcessHandler', name='task-ad-transaction-process'),

    Route('/task/transaction/firebase/update','apps.uetopia.handlers.tasks.transactions.firebase_update.TransactionUpdateFirebaseHandler', name='task-transaction-firebase-update'),

    ## teams
    Route('/task/team/update_player_noteam','apps.uetopia.handlers.tasks.teams.update_player_noteam.TeamUpdateFirebaseHandler', name='task-team-update-player-noteam'),
    Route('/task/team/firebase/update','apps.uetopia.handlers.tasks.teams.firebase_update.TeamUpdateFirebaseHandler', name='task-team-firebase-update'),
    Route('/task/team/delete','apps.uetopia.handlers.tasks.teams.delete.TeamDeleteHandler', name='task-team-delete'),

    ## chat
    Route('/task/chat/channel/list_changed','apps.uetopia.handlers.tasks.chat.channel_list_changed.ChatChannelListChangedHandler', name='task-chat-channel-list-changed'),
    Route('/task/chat/channel/send','apps.uetopia.handlers.tasks.chat.channel_send.ChatChannelSendHandler', name='task-chat-channel-send'),
    Route('/task/chat/send','apps.uetopia.handlers.tasks.chat.send.ChatSendHandler', name='task-chat-send'),
    Route('/task/chat/channel/delete','apps.uetopia.handlers.tasks.chat.channel_delete.ChatChannelDeleteHandler', name='task-chat-channel-delete'),

    ## tournament
    Route('/task/tournament/finish_signups','apps.uetopia.handlers.tasks.games.tournament.finish_signups.TaskTournamentFinishSignups', name='task-tournament-finish-signups'),
    Route('/task/tournament/round/start','apps.uetopia.handlers.tasks.games.tournament.round_start.TaskTournamentStartRound', name='task-tournament-round-start'),
    Route('/task/tournament/round/end','apps.uetopia.handlers.tasks.games.tournament.round_end.TaskTournamentEndRound', name='task-tournament-round-end'),
    Route('/task/tournament/finalize','apps.uetopia.handlers.tasks.games.tournament.finalize.TaskTournamentFinalize', name='task-tournament-finalize'),

    ## bigquery
    Route('/task/cloudstorage/clear', 'apps.uetopia.handlers.tasks.clear_cloud_storage.ClearCloudStorageHandler', name='task-clear-cloud-storage-handler'),
    Route('/task/bigquery/load', 'apps.uetopia.handlers.tasks.load_to_bigquery.LoadToBigQueryHandler', name='task-load-to-big-query'),

    # currency
    Route('/task/currency/firebase/update', 'apps.uetopia.handlers.tasks.currency.firebase_update.CurrencyUpdateFirebaseHandler', name='task-currency-firebase-update'),

    # BitPay
    Route('/callbacks/bitpay/invoice_status', 'apps.uetopia.handlers.bitpay.invoice_callback.BitPayInvoiceCallbackHandler', name='callback-bitpay-invoice-status'),

    # Vouchers
    Route('/task/voucher/attempt_redeem','apps.uetopia.handlers.tasks.vouchers.attempt_redeem.VoucherAttemptRedeemHandler', name='task-voucher-attempt-redeem'),

    # Badges / Tags
    Route('/task/game/player/tags_update','apps.uetopia.handlers.tasks.games.players.tags_update.GamePlayerUpdateTagsHandler', name='task-game-player-tags-update'),

    # Blog
    Route('/feed/','apps.uetopia.handlers.blog.feed.FeedHandler', name='blog-feed'),



    ]
