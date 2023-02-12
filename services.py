import fix_path
import endpoints

#from api_collection import api_collection
from service import users
from service import games
from service import servers
from service import transactions
from service import user_relationships
from service import groups
from service import teams
from service import chat
from service import tournaments
from service import vendors
from service import characters
from service import ads
from service import offers
from service import vouchers
from service import badges
from service import blog
from service import consignments

# don't do it this way - results in one big API
#app = endpoints.api_server([api_collection])


app = endpoints.api_server([ users.UsersApi,
                                games.GamesApi,
                                servers.ServersApi,
                                transactions.TransactionsApi,
                                user_relationships.UserRelationshipsApi,
                                groups.GroupsApi,
                                teams.TeamsApi,
                                chat.ChatApi,
                                tournaments.TournamentApi,
                                vendors.VendorsApi,
                                characters.CharactersApi,
                                ads.AdsApi,
                                offers.OffersApi,
                                vouchers.VouchersApi,
                                badges.BadgesApi,
                                blog.BlogApi,
                                consignments.ConsignmentsApi ], restricted=False)



## TO CREATE THE OPENAPI FILES USE THIS
## This shit does not work.
## python lib/endpoints/endpointscfg.py get_openapi_spec service.ads.AdsApi service.characters.CharactersApi service.chat.ChatApi service.games.GamesApi service.groups.GroupsApi service.servers.ServersApi service.teams.TeamsApi service.tournaments.TournamentApi service.transactions.TransactionsApi service.user_relationships.UserRelationshipsApi service.users.UsersApi service.vendors.VendorsApi --hostname ue4topia.appspot.com --x-google-api-name

## then deploy it using
## gcloud endpoints services deploy charactersv1openapi.json adsv1openapi.json chatv1openapi.json gamesv1openapi.json groupsv1openapi.json serversv1openapi.json teamsv1openapi.json tournamentsv1openapi.json transactionsv1openapi.json userrelationshipsv1openapi.json usersv1openapi.json vendorsv1openapi.json
