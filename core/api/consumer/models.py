# from sqlalchemy import (JSON, Boolean, Column, Date, DateTime, Enum,
#                         ForeignKey, Integer, String)

# from core.database.connection import Base
# from core.models.mixin import DeviceType, GenderType, TimeStamp


# class ConsumerProfile(Base, TimeStamp):

#     __tablename__ = "consumer_profile"
#     id = Column(Integer, primary_key=True)
#     users_id = Column(Integer, ForeignKey("users.id"), unique=True)
#     dob = Column(Date)
#     gender = Column(Enum(GenderType), nullable=False)
#     address1 = Column(String(100))
#     address2 = Column(String(100))
#     city = Column(String(20))
#     district = Column(String(20))
#     state = Column(String(20))
#     country = Column(String(20))
#     postal_code = Column(String(20))
#     current_location = Column(JSON)
#     device_platform = Column(Enum(DeviceType))
#     fcm_token = Column(String(1024))
#     last_login = Column(DateTime)
#     email_verified = Column(Boolean, default=False)
#     profile_image = Column(String())
#     phone_number_verified = Column(Boolean, default=False)

#     class Config:
#         orm_mode = True


# class SocialMedia(Base, TimeStamp):
#     __tablename__ = 'social_media'
#     id = Column(Integer, primary_key=True)
#     name = Column(String(20), nullable=False)
#     column_name = Column(String(20), nullable=False)
    

# class FollowedSocialMedia(Base, TimeStamp):
#     __tablename__ = 'followed_social_media'
#     id = Column(Integer, primary_key=True)
#     users_id = Column(Integer, ForeignKey("users.id"), unique=True)
#     facebook_followed = Column(Boolean, default=False)
#     youtube_followed = Column(Boolean, default=False)
#     twitter_followed = Column(Boolean, default=False)
#     whatsapp_followed = Column(Boolean, default=False)
#     linkedin_followed = Column(Boolean, default=False)
#     telegram_followed = Column(Boolean, default=False)
#     instagram_followed = Column(Boolean, default=False)
#     discord_followed = Column(Boolean, default=False)

