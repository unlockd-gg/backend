from webapp2 import Route

routes = [

    Route('/admin/user/reset_terms_accepted_flag', 'apps.uetopia.handlers.admin.reset_users_terms_accepted_flag.ResetUserTermsAcceptedFlagHandler', name='admin-users-reset-terms-accepted'),
    Route('/admin/user/set_server_instanced_template', 'apps.uetopia.handlers.admin.set_instanced_template.SetInstancedTemplateFlagHandler', name='admin-servers-set-instanced-template'),
    Route('/admin/user/batch_update_mailjet', 'apps.uetopia.handlers.admin.batch_update_mailjet_lists.BatchUpdateMailjetHandler', name='admin-batch_update_mailjet'),
    #Route('/admin/one_time_update_group_members_gkp', 'apps.uetopia.handlers.admin.one_time_update_group_member_gkp.UpdateGroupMemberGkpHandler', name='admin-one-time-update-group-gkp'),




    ]
