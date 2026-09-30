from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """Token generator for "verify your email" links.

    Includes ``is_active`` in the hash so a token becomes invalid as soon as
    the account has already been verified/activated once.
    """

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{user.password}{timestamp}{user.is_active}"


email_verification_token = EmailVerificationTokenGenerator()
