import logging
import datetime
from google.appengine.api import users
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.server_instances import ServerInstancesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from configuration import *

class ServerGameTransferHandler(BaseHandler):
    def get(self):
        logging.info('Cron Server Game Transfer')
        serverController = ServersController()
        siController = ServerInstancesController()
        lockController = TransactionLockController()
        transactionController = TransactionsController()

        transfer_amount = 0

        ## get any pending instance record
        any_exceeded_record = serverController.get_any_server_to_game_transfer_exceeded()


        if any_exceeded_record:
            logging.info('found an exceeded record')

            margin_amount = any_exceeded_record.server_to_game_transfer_threshold / 5
            transfer_amount = any_exceeded_record.serverCurrency - any_exceeded_record.server_to_game_transfer_threshold

            if transfer_amount > 0:

                transfer_amount = transfer_amount + margin_amount



                ## Transaction for the server
                description = "Server to Game Transfer"
                sender_transaction = transactionController.create(
                    amountInt = int(-transfer_amount),
                    description = description,
                    serverKeyId = any_exceeded_record.key.id(),
                    serverTitle = any_exceeded_record.title,
                    transactionType = 'server',
                    transactionClass = "server to game transfer",
                    transactionSender = True,
                    transactionRecipient = False,
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_SERVER_TO_GAME_TRANSFER,
                    materialDisplayClass = "md-accent"
                )

                ## only start pushable tasks.  If they are not pushable, there is already a task running.
                pushable = lockController.pushable("server:%s"%any_exceeded_record.key.id())
                if pushable:
                    logging.info('server pushable')
                    taskUrl='/task/server/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='serverTransactionProcess', params={
                                                                                            "key_id": any_exceeded_record.key.id()
                                                                                        }, countdown=2)



                ## transaction for the game
                description = "Server Transfer from: %s" %any_exceeded_record.title
                recipient_transaction = transactionController.create(
                    amountInt = transfer_amount,
                    ##amount = ndb.FloatProperty(indexed=False) # for display
                    ##newBalanceInt = ndb.IntegerProperty(indexed=False)
                    ##newBalance = ndb.FloatProperty(indexed=False) # for display
                    description = description,
                    ##userKeyId = authorized_user.key.id(),
                    ##firebaseUser = authorized_user.firebaseUser,
                    ##targetUserKeyId = ndb.IntegerProperty()
                    gameKeyId = any_exceeded_record.gameKeyId,
                    gameTitle = any_exceeded_record.gameTitle,

                    ##  transactions are batched and processed all at once.
                    transactionType = "game",
                    transactionClass = "server to game transfer",
                    transactionSender = False,
                    transactionRecipient = True,
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_SERVER_TO_GAME_TRANSFER,
                    materialDisplayClass = "md-primary"
                )


                ## only start pushable tasks.  If they are not pushable, there is already a task running.
                pushable = lockController.pushable("game:%s"%any_exceeded_record.gameKeyId)
                if pushable:
                    logging.info('game pushable')
                    taskUrl='/task/game/transaction/process'
                    taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                            "key_id": any_exceeded_record.gameKeyId
                                                                                        }, countdown=2)


                ## restart task
                taskUrl = '/cron/server/balance_exceeded/process'
                taskqueue.add(url=taskUrl, queue_name='serverBalanceProcess', countdown=2)

                ## turn off the pending flag
                any_exceeded_record.server_to_game_transfer_exceeded = False
                serverController.update(any_exceeded_record)

        else:
            logging.info('No servers to process')

        return self.render_json_response(
            transfer_amount= transfer_amount,
        )

    def post(self):
        return self.get()
