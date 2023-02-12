import logging
import datetime
from google.appengine.api import users
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from apps.uetopia.controllers.server_instances import ServerInstancesController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.providers.compute_engine_pricing import compute_engine_pricing_dict
from configuration import *

class ServerInstanceProcessHandler(BaseHandler):
    def get(self):
        logging.info('Cron Server Instance process')
        siController = ServerInstancesController()
        lockController = TransactionLockController()
        transactionController = TransactionsController()

        ## get any pending instance record
        any_pending_record = siController.get_any_pending()

        total_sum_minutes_billable =0
        total_sum_currency_billable = 0

        if any_pending_record:
            logging.info('found a pending record')
            if any_pending_record.instanceType == 'match':
                logging.info('doing match specific processing')
                all_pending_for_this_server = siController.get_pending_by_gameKeyId(any_pending_record.gameKeyId)
                transactionType = 'game'

            else:
                logging.info('found a pending record for: %s' %any_pending_record.serverTitle)

                ## check to see if this is an instanced or sharded server - which is going to need special handling.
                ## on second thought - let's just change the server instance record to reflect the parent server to begin with
                
                all_pending_for_this_server = siController.get_pending_by_serverKeyId(any_pending_record.serverKeyId)
                transactionType = 'server'

            logging.info('Found %s pending records'% len(all_pending_for_this_server))

            for this_pending_server_record in all_pending_for_this_server:
                logging.info('processing record')
                if this_pending_server_record.machine_type:
                    logging.info('found a machine type')
                    total_sum_minutes_billable = total_sum_minutes_billable + this_pending_server_record.uptime_minutes_billable

                    ## grab the hourly rate from our static dict
                    logging.info('this_pending_server_record.region_name: %s' %this_pending_server_record.region_name)
                    logging.info('this_pending_server_record.machine_type: %s' %this_pending_server_record.machine_type)
                    try:
                        this_servers_hourly_rate = compute_engine_pricing_dict[this_pending_server_record.region_name][this_pending_server_record.machine_type]
                    except:
                        logging.error("unable to find hourly rate for %s / %s" %(this_pending_server_record.region_name, this_pending_server_record.machine_type))
                        this_servers_hourly_rate = .01
                    this_servers_minute_rate = this_servers_hourly_rate / 60.0
                    logging.info('this_servers_hourly_rate: %s' %this_servers_hourly_rate)
                    logging.info('this_servers_minute_rate: %s' %this_servers_minute_rate)

                    total_sum_currency_billable = total_sum_currency_billable + (this_pending_server_record.uptime_minutes_billable * this_servers_minute_rate)
                    ##  mark this instance record as processed
                this_pending_server_record.processed = True
                siController.update(this_pending_server_record)


            logging.info('total_sum_minutes_billable: %s' %total_sum_minutes_billable)
            logging.info('total_sum_currency_billable: %s' %total_sum_currency_billable)

            ## convert USD to CRED
            total_sum_cred_billable = total_sum_currency_billable * 100.0 * USD_TO_CRED_CONVERSION

            if total_sum_cred_billable > 0.0:
                description = "Instance Bill"
                recipient_transaction = transactionController.create(
                    amountInt = int(-total_sum_cred_billable),
                    description = description,
                    gameKeyId = any_pending_record.gameKeyId,
                    gameTitle = any_pending_record.gameTitle,
                    serverKeyId = any_pending_record.serverKeyId,
                    serverTitle = any_pending_record.serverTitle,
                    transactionType = transactionType,
                    transactionClass = "instance bill",
                    transactionSender = False,
                    transactionRecipient = True,
                    submitted = True,
                    processed = False,
                    materialIcon = MATERIAL_ICON_SERVER_BILL,
                    materialDisplayClass = "md-accent"
                )

                if any_pending_record.instanceType == 'match':
                    ## only start pushable tasks.  If they are not pushable, there is already a task running.
                    pushable = lockController.pushable("game:%s"%any_pending_record.gameKeyId)
                    if pushable:
                        logging.info('game pushable')
                        taskUrl='/task/game/transaction/process'
                        taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                                "key_id": any_pending_record.gameKeyId
                                                                                            }, countdown=2)

                else:

                    ## only start pushable tasks.  If they are not pushable, there is already a task running.
                    pushable = lockController.pushable("server:%s"%any_pending_record.serverKeyId)
                    if pushable:
                        logging.info('server pushable')
                        taskUrl='/task/server/transaction/process'
                        taskqueue.add(url=taskUrl, queue_name='serverTransactionProcess', params={
                                                                                                "key_id": any_pending_record.serverKeyId
                                                                                            }, countdown=2)

                ## restart task
                taskUrl = '/cron/server/instance/process'
                taskqueue.add(url=taskUrl, queue_name='serverInstanceProcess', countdown=20)
        else:
            logging.info('No pending instances to process')

        return self.render_json_response(
            total_sum_currency_billable= total_sum_currency_billable,
        )

    def post(self):
        return self.get()
