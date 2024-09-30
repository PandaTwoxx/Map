"""
Model for Locations

All of the models are stored in this module
"""

import logging
from service.models import PersistentBase, DataValidationError
from service import db

logger = logging.getLogger('flask.app')


class UsersLocations(db.Model, PersistentBase):
    """The UsersLocations DB Class

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

    # CREATE TABLE users_locations (
    #     id INT AUTO_INCREMENT PRIMARY KEY,
    #     user_id INT NOT NULL,
    #     location_id INT NOT NULL,
    #     FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    #     FOREIGN KEY (location_id) REFERENCES locations(id) ON DELETE CASCADE
    # );

    __tablename__ = 'users_locations'
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))

    ################################
    # SERIALIZE/DESERIALIZE ########
    ################################

    def serialize(self) -> dict:
        """Serializer

        Returns:
            dict: The serialized object
        """
        result = {
            "id": self.id,
            "user_id": self.user_id,
            "location_id": self.location_id,
        }
        return result
    
    def deserialize(self, data: dict) -> None:
        """
        Deserializes a Shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data['id']
            self.user_id = data['user_id']
            self.location_id = data['location_id']
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
        return f"<id:{self.id}, user_id:{self.user_id}, location_id:{self.location}>"
