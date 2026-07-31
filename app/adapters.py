from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def populate_user(self, request, sociallogin, data):

        user = super().populate_user(request, sociallogin, data)

        extra = sociallogin.account.extra_data

        if extra.get("given_name"):
            user.first_name = extra["given_name"]

        if extra.get("family_name"):
            user.last_name = extra["family_name"]

        return user