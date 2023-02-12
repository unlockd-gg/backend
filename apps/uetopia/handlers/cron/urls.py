from webapp2 import Route

routes = [

    Route('/cron/server/player/deactivate_stale', 'apps.uetopia.handlers.cron.deactivate_stale_server_players.DeactivateStalePlayersHandler', name='cron-server-players-deactivate-stale'),
    Route('/cron/server/instance/process', 'apps.uetopia.handlers.cron.server_instance_process.ServerInstanceProcessHandler', name='cron-server-instance-process'),
    Route('/cron/server/balance_exceeded/process','apps.uetopia.handlers.cron.server_game_transfer.ServerGameTransferHandler', name='task-server-game-transfer'),

    Route('/cron/match/player/deactivate_stale', 'apps.uetopia.handlers.cron.deactivate_stale_match_players.DeactivateStaleMatchPlayersHandler', name='cron-match-players-deactivate-stale'),

    Route('/cron/tournament/expire', 'apps.uetopia.handlers.cron.tournament.expire.TournamentExpireHandler', name='tournament-expire'),

    Route('/cron/bigquery/start', 'apps.uetopia.handlers.cron.bigquery_tasks_start.BigQueryTasksStartHandler', name='cron-big-query-tasks-start'),

    Route('/cron/currency/update', 'apps.uetopia.handlers.cron.currency_update.CronCurrencyUpdateHandler', name='cron-currency-update'),

    Route('/cron/badges/remove_expired', 'apps.uetopia.handlers.cron.remove_expired_badges.RemoveExpiredBadgesHandler', name='cron-remove-expired-badges'),

    Route('/cron/vendors/remove_stale', 'apps.uetopia.handlers.cron.remove_stale_vendors.RemoveStaleVendorsHandler', name='cron-remove-stale-vendors')


    ]
