from itertools import chain
from sqlalchemy.orm import Session, load_only
from sqlalchemy.dialects.postgresql import insert

from core.api.users.models import Users
from core.api.consumer.models import ConsumerProfile, SocialMedia, FollowedSocialMedia
from core.api.users.crud import get_user_by_email





def get_recent_referrals_profile(db : Session, referral_code : int, user_id : int):
    profile_data = db.query(
        Users.full_name, Users.id, ConsumerProfile.profile_image, Users.created_at
        ).select_from(Users).join(
            ConsumerProfile, Users.id==ConsumerProfile.users_id, isouter=True).filter(Users.referred_by==referral_code
            ).all()
    return profile_data