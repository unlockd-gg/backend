from webapp2 import Route

routes = [

    Route('/gamepatch/<gameKeyId>/manifest.xml', 'apps.uetopia.handlers.patcher.get_manifest.GetManifestHandler', name='patcher-get-game-manifest'),
    Route('/gamepatch/me','apps.uetopia.handlers.patcher.auth_me.IndexHandler', name='patcher-login-auth-me')

    ]
