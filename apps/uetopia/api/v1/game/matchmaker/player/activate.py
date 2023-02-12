import logging
import datetime
import string
import json
from apps.handlers import BaseHandler
from google.appengine.api import taskqueue
from apps.uetopia.controllers.servers import ServersController
from apps.uetopia.controllers.games import GamesController
from apps.uetopia.controllers.game_modes import GameModesController
from apps.uetopia.controllers.server_players import ServerPlayersController
from apps.uetopia.controllers.users import UsersController
from apps.uetopia.controllers.transactions import TransactionsController
from apps.uetopia.controllers.game_players import GamePlayersController
from apps.uetopia.controllers.transaction_lock import TransactionLockController
from apps.uetopia.controllers.match_players import MatchPlayersController
from apps.uetopia.controllers.match import MatchController
from configuration import *

class ActivateMatchPlayerHandler(BaseHandler):
    def post(self, userid):
        """
        Check if user can be activated
        Requires http headers:  Key, Sign
        Requires POST parameters:  userid, nonce
        """

        serverController = ServersController()
        uController = UsersController()
        spController = ServerPlayersController()
        #cController = CurrencyController()
        gpController = GamePlayersController()
        lockController = TransactionLockController()
        transactionController = TransactionsController()
        matchPlayersController = MatchPlayersController()
        matchController = MatchController()
        gmController = GameModesController()



        match = matchController.verify_signed_auth(self.request)

        if match == False:
            logging.info('auth failure')
            return self.render_json_response(
                authorization = False
            )
        else:
            logging.info('auth success')

            incoming_userid = userid #self.request.POST.get('userid', None)

            logging.info("incoming_userid: %s" % incoming_userid)
            logging.info("matchKey: %s" % match.key.urlsafe())
            logging.info("matchKeyId: %s" % match.key.id())

            authorized = False
            activated = False
            previously_active = False
            user_key_id = None
            player_name = None
            player_currency = 0
            player_rank = 1600
            auth_deny_reason = "None"
            player_userid = None
            game_player_key_id = None
            team_id = None

            if incoming_userid:
                logging.info('userid found in post')
                #logging.info('player_userid: %s' %player_userid)

                ## grab the game so we can populate the active user feed
                game = GamesController().get_by_key_id(match.gameKeyId)

                ## set the platfromID from the incoming request, we want to hand it back even if it can't be found
                player_userid = incoming_userid


                #if platform_player_connection:
                user = uController.get_by_key_id(int(incoming_userid))

                if user:
                    logging.info('user found')

                    user_key_id = user.key.id()

                    # grab this user's game user Key
                    game_player = gpController.get_by_gameKeyId_userKeyId(match.gameKeyId, user.key.id())
                    if game_player:
                        game_player_key_id = game_player.key.id()
                    else:
                        logging.error("Game user NOT found.")

                        ## push an alert out to firebase
                        description = "%s Game Permissions not set.  Setup your game permissions first!" %game.title
                        taskUrl='/task/user/alert/create'
                        action_button='/#/game/%s/play'%game.key.id()
                        taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': user.firebaseUser,
                                                                                        'material_icon': MATERIAL_ICON_GAME,
                                                                                        'importance': 'md-primary',
                                                                                        ## TODO this message can be more helpful
                                                                                        'message_text': description,
                                                                                        'action_button_color': 'primary',
                                                                                        'action_button_sref': action_button
                                                                                        }, countdown = 0,)

                        ## this should not happen.  returning false
                        return self.render_json_response(
                            authorization = True,
                            player_authorized = False,
                            user_key_id = incoming_userid,
                            player_userid = incoming_userid,
                        )

                    # first check to make sure there is a match user member record
                    match_player = matchPlayersController.get_by_matchKeyId_userKeyId(match.key.id(), user.key.id() )

                    if match_player:
                        logging.info('match_player found')
                        #logging.info('server_player currencyCurrent: %s' % server_player.currencyCurrent)


                        ##if match_player.pending_authorize:
                        ##    logging.info('server_player Set to pending authorize')

                        ##if match_player.active:
                        ##    previously_active = True

                        # deal with possible admission fee
                        # if it's not a tournament
                        if not match.tournamentKeyId:
                            logging.info('This is not a tournament match - Doing admission fee processing')

                            ## make sure they haven't already paid admission
                            if not match_player.matchmakerPaidAdmission:
                                logging.info('matchmakerPaidAdmission is false.  charging admission fee')

                                game_mode = gmController.get_by_key_id(match.gameModeKeyId)
                                if not game_mode:
                                    logging.error('game mode not found.')

                                if game_mode.admissionFeePerPlayer > 0:
                                    logging.info('admissionFee is enabled')
                                    ## Handle admissions fee

                                    ## handle transactions and transaction notifications
                                    description = "Joined match: %s" %match.title

                                    ## Create a transaction for the withdrawl -user
                                    transaction = TransactionsController().create(
                                        userKeyId = user.key.id(),
                                        firebaseUser = user.firebaseUser,
                                        description = description,
                                        amountInt = -game_mode.admissionFeePerPlayer,
                                        transactionType = "user",
                                        transactionClass = "match activate",
                                        transactionSender = True,
                                        transactionRecipient = False,
                                        submitted = True,
                                        processed = False,
                                        materialIcon = MATERIAL_ICON_SERVER_AUTHORIZE,
                                        materialDisplayClass = "md-accent"
                                        )

                                    pushable = lockController.pushable("user:%s"%user.key.id())
                                    if pushable:
                                        logging.info('user pushable')
                                        taskUrl='/task/user/transaction/process'
                                        taskqueue.add(url=taskUrl, queue_name='userTransactionProcess', params={
                                                                                                            "key_id": user.key.id()
                                                                                                        }, countdown=2)



                                    ## create a transaction for the deposit +game
                                    description = "Admission Fee from: %s" %user.title
                                    recipient_transaction = transactionController.create(
                                        amountInt = game_mode.admissionFeePerPlayer,
                                        description = description,
                                        gameKeyId = game.key.id(),
                                        gameTitle = game.title,
                                        transactionType = "game",
                                        transactionClass = "admission fee",
                                        transactionSender = False,
                                        transactionRecipient = True,
                                        submitted = True,
                                        processed = False,
                                        materialIcon = MATERIAL_ICON_ADMISSION_FEE,
                                        materialDisplayClass = "md-primary"
                                    )

                                    ## only start pushable tasks.  If they are not pushable, there is already a task running.
                                    pushable = lockController.pushable("game:%s"%game.key.id())
                                    if pushable:
                                        logging.info('game pushable')
                                        taskUrl='/task/game/transaction/process'
                                        taskqueue.add(url=taskUrl, queue_name='gameTransactionProcess', params={
                                                                                                                "key_id": game.key.id()
                                                                                                            }, countdown=2)
                                    ## push an alert out to firebase
                                    ## muting this for now I dont think we need it.
                                    """

                                    description = "%s CRED admission fee paid to %s" %(game_mode.admissionFeePerPlayer, game.title)
                                    taskUrl='/task/user/alert/create'
                                    taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'firebase_user': user.firebaseUser,
                                                                                                    'material_icon': MATERIAL_ICON_ADMISSION_FEE,
                                                                                                    'importance': 'md-primary',
                                                                                                    ## TODO this message can be more helpful
                                                                                                    'message_text': description,
                                                                                                    'action_button_color': 'primary',
                                                                                                    'action_button_sref': '/profile'
                                                                                                    }, countdown = 0,)
                                    """
                                    match_player.matchmakerPaidAdmission = True

                        ## set return values
                        authorized = True
                        user_key_id = user.key.id()
                        player_name = user.title
                        activated = True
                        player_rank = match_player.rank
                        team_id = match_player.teamId

                        ## Update the match_player record
                        match_player.active = True
                        match_player.joined = True
                        #server_player.authorized = True
                        match_player.pending_authorize = False

                        matchPlayersController.update(match_player)

                    else:
                        logging.info('match_player NOT found')

                        ## deny them

                else:
                    logging.info('user NOT found')

            if authorized:
                taskUrl='/task/user/firebase/update'
                playingLink = '/#/game/%s/'%match.gameKeyId
                taskqueue.add(url=taskUrl, queue_name='firebaseUpdate', params={'key_id': user.key.id(),
                                                                                'playingGame': game.title,
                                                                                'playingGameKeyId': game.key.id(),
                                                                                'playingLink': playingLink,
                                                                                'online': True }, countdown = 2,)

            logging.info("game_player_key_id: %s" %game_player_key_id)

            return self.render_json_response(
                authorization = True,
                player_authorized = authorized,
                player_previously_active = previously_active,
                user_key_id = str(user_key_id),
                #player_name = player_name,
                #player_currency = player_currency,
                #player_rank = player_rank,
                player_userid = player_userid,
                game_player_key_id = str(game_player_key_id),
                team_id = team_id
            )
