"""
Model for Locations Details

All of the models are stored in this module
"""

import logging
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_X, ST_Y
from shapely.geometry import Point
from service.models import PersistentBase, DataValidationError
from service import db

logger = logging.getLogger('flask.app')


class LocationDetails(db.Model, PersistentBase):
    """The LocationDetails DB Class

    Derives:
        db.Model (SQLAlchemy): SQLAlchemy
        PersistentBase: DB class template

    Raises:
        DataValidationError: Invalid Attribute
        DataValidationError: Invalid LocationDetail, Missing Data
        DataValidationError: Invalid LocationDetail, No data or Bad Data
    """


    ################################
    # Table Schema #################
    ################################

    # CREATE TABLE location_details (
    #     id INT AUTO_INCREMENT PRIMARY KEY,
    #     coordinate POINT NOT NULL
    # );

    __tablename__ = 'locations_details'
    id = db.Column(db.Integer, primary_key = True)
    location = db.Column(Geometry(geometry_type='POINT', srid=3857), nullable = False)


    ################################
    # SERIALIZE/DESERIALIZE ########
    ################################

    def serialize(self) -> dict:
        """Serializer

        Returns:
            dict: The serialized object
        """
        result = {
            "id": id,
            "lon": ST_X(self.location).scalar(),
            "lat": ST_Y(self.location).scalar()
        }
        return result


    def deserialize(self, data: dict) -> None:
        """
        Deserializes a Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.location = Point(data['lon'],data['lat'])

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid LocationDetail: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Shopcart: body of request contained bad or no data "
                + str(error)
            ) from error


    def __repr__(self) -> str:
        return f"<id:{self.id}, lon:{ST_X(self.location).scalar()},\
          lat:{ST_Y(self.location).scalar()}"
