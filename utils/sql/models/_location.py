from sqlalchemy import Column, ForeignKey, Integer, Float, String
from utils.sql import Base


class Location(Base):
    __tablename__ = '_locations'

    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('_restaurants.id'))

    # Lat. expresses distance north or south of the Equator
    latitude = Column(Float)
    # Lon. expresses distance east or west from the Prime Meridian
    longitude = Column(Float)

    # Ex.
    #   street_address = "1345 2nd Avenue"
    #   addressLocality = "New York"
    #   addressRegion = "New York"
    #   postalCode = 10021
    street_address = Column(String)
    addressLocality = Column(String)
    addressRegion = Column(String)
    postalCode = Column(Integer)

    neighborhood = Column(String)
