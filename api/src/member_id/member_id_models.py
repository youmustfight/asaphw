from datetime import datetime
from sqlalchemy import Column, Date, DateTime, Integer, Text
from dbs.sa_models import BaseModel

# MemberID Schema Thoughts:
# - thought about making a separate 'Identification Number' table, but it'll be convenient to do look up here for now
# - make unique check required to throw err
# - this is likely over kill, but creating a whole member, so it can throw an error if the member id is already taken

class MemberID(BaseModel):
    __tablename__ = "member_id"
    id = Column(Integer(), primary_key=True)
    value = Column(Text(), unique=True)
    created_at = Column(DateTime(timezone=True))
    # TODO: user = relationship("User", back_populates="member_id")
    def serialize(self):
        return {
            # "id": self.id, # this func is for API responses, so we don't want to show database ids
            "value": self.value,
            "created_at": str(self.created_at)
        }
