from webapp2 import Route

routes = [

    ## platform token request and data transmit
    Route('/me','apps.uetopia.handlers.auth_me.IndexHandler', name='login-auth-me'),

    ##redirect test for 4.17
    Route('/4.16/t_login_complete_R','apps.uetopia.handlers.token_login_redirect.TokenLoginRedirectHandler', name='login-token-redirect'),

    ## handler to clean up the database when a server or match crash is detected.
    Route('/webhooks/crash_detected/<serverKeyId>/<serverSecret>','apps.uetopia.handlers.webhooks.on_vm_crash.OnVmCrashHandler', name='webhook-vm-crash'),


    ]
