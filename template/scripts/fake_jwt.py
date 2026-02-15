import argparse
import secrets
from uuid import uuid4

import jwt


parser = argparse.ArgumentParser(description="Generate a fake user jwt, no support for machines yet.")
parser.add_argument(
    "--user-id",
    dest="user_id",
    type=str,
    default=str(uuid4()),
    help="The UUID of the user making the request.",
)
parser.add_argument(
    "--original-token",
    dest="original_token",
    default=secrets.token_urlsafe(32),
    type=str,
    help="The original API key from the user in webapp.",
)

group = parser.add_mutually_exclusive_group()
group.add_argument(
    "--client-id",
    dest="client_id",
    default=str(uuid4()),
    type=str,
    help="The UUID of the client related to the user making the request.",
)
group.add_argument(
    "--partner-id",
    dest="partner_id",
    type=str,
    help="The UUID of the partner related to the user making the request.",
)
parser.add_argument(
    "--portal-partner-id",
    dest="portal_partner_id",
    default=str(uuid4()),
    type=str,
    help="The UUID of the partner that has the portal_url configured as its white-label domain.",
)
parser.add_argument(
    "--first-name",
    dest="first_name",
    default="John",
    type=str,
    help="The first name of the user making the request.",
)
parser.add_argument(
    "--preposition",
    dest="preposition",
    default="",
    type=str,
    help="The preposition of the name of the user making the request.",
)
parser.add_argument(
    "--last-name",
    dest="last_name",
    default="Doe",
    type=str,
    help="The last name of the user making the request.",
)


def generate_fake_jwt(
    user_id: str,
    original_token: str,
    portal_partner_id: str,
    first_name: str,
    preposition: str,
    last_name: str,
    partner_id: str | None = None,
    client_id: str | None = None,
) -> str:
    """
    Generate a fake JWT token.
    """
    payload = {
        "type": "user",
        "sub": user_id,
        "original_token": original_token,
        "partner_id": partner_id,
        "client_id": client_id,
        "portal_partner_id": portal_partner_id,
        "portal_url": "https://partner.voipgrid.nl",
        "wiki_url": "https://wiki.voipgrid.nl/index.php/",
        "first_name": first_name,
        "preposition": preposition,
        "last_name": last_name,
    }
    return jwt.encode(payload, "NOT_VERY_SECRET_BUT_DOES_NOT_MATTER_FOR_FAKE_JWTS", "HS256")


if __name__ == "__main__":
    args = parser.parse_args()
    args_dict = vars(args)
    print(generate_fake_jwt(**args_dict))
