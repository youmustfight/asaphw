from sqlalchemy import Column, Date, DateTime, Integer, Text
from sqlalchemy.orm import relationship, validates

from dbs.sa_models import BaseModel
from utils.validators import is_valid_country_code, is_valid_date

# User Schema Thoughts:
# -  created for verification purposes against member_id


class User(BaseModel):
    __tablename__ = "user"

    # --- fields
    id = Column(Integer(), primary_key=True)
    first_name = Column(Text())
    last_name = Column(Text())
    date_of_birth = Column(Date())
    origin_country_code = Column(Text())
    created_at = Column(DateTime(timezone=True))
    # --- relations
    member_id = relationship("MemberID", back_populates="user")

    # --- validations
    @validates("date_of_birth")
    def validate_country_code(self, key, date_of_birth):
        is_valid_date(date_of_birth) # will throw if invalid
        return date_of_birth

    @validates("origin_country_code")
    def validate_country_code(self, key, country_code):
        is_valid_country_code(country_code) # will throw if invalid
        return country_code
    
    # --- helpers
    def serialize(self):
        return {
            # this func is for API responses, so we don't want to show database ids and personal info not used by frontends
            "first_name": self.first_name,
            "last_name": self.last_name,
            "created_at": str(self.created_at)
        }
