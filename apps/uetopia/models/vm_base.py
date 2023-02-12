from google.appengine.ext import ndb

class VMBase(ndb.Model):
    """ This is the base model for VM instances.  Servers and Matches use this """

    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    title = ndb.StringProperty(indexed=False)
    description = ndb.TextProperty(indexed=False)

    hostAddress = ndb.StringProperty(indexed=False)
    hostPort = ndb.StringProperty(indexed=False)
    hostConnectionLink = ndb.StringProperty(indexed=False)

    gameKeyId = ndb.IntegerProperty()
    gameTitle = ndb.StringProperty(indexed=False)

    admissionFee = ndb.IntegerProperty(indexed=False)

    ## Api stuff
    apiKey = ndb.StringProperty()
    apiSecret = ndb.StringProperty(indexed=False)

    ## Unreal Engine Online Subsystem
    session_host_address = ndb.StringProperty(indexed=False)
    session_id = ndb.StringProperty(indexed=False)

    # FOR CONTINUOUS - moving this to server clusters
    ## VM Creation Settings - the "continuous_server" part is just legacy.  We could refactor this.
    ## these are used by both servers and matchmaker.
    continuous_server_project = ndb.StringProperty(indexed=False)
    continuous_server_bucket = ndb.StringProperty(indexed=False)
    continuous_server_region = ndb.StringProperty(indexed=True)
    continuous_server_zone = ndb.StringProperty(indexed=False)
    continuous_server_source_disk_image = ndb.StringProperty(indexed=False)
    continuous_server_machine_type = ndb.StringProperty(indexed=False)

    ## these can be overridden by individual servers, but they are also in server cluster
    continuous_server_startup_script_location = ndb.StringProperty(indexed=False)
    continuous_server_shutdown_script_location = ndb.StringProperty(indexed=False)

    checkUnusedTaskName = ndb.StringProperty(indexed=False) # hang on to the check unused task so we can kill it when a user logs in.
