"""
Model for Locations

All of the models are stored in this module
"""

import logging
from service.models import PersistentBase, DataValidationError
from service import db

logger = logging.getLogger('flask.app')


class Location(db.Model, PersistentBase):
    """The Location DB Class

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

    # CREATE TABLE locations (
    #     id INT AUTO_INCREMENT PRIMARY KEY,
    #     address varchar(255) NOT NULL,
    #     name varchar(255) NOT NULL,
    #     description varchar(255) NOT NULL,
    #     location_details_id INT NOT NULL,
    #     FOREIGN KEY (location_details_id) REFERENCES location_details(id) ON DELETE CASCADE
    # );

    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key = True)
    address = db.Column(db.String(255), nullable = False)
    name = db.Column(db.String(255), nullable = False)
    description = db.Column(db.String(255), nullable = False)
    location_details_id = db.Column(db.Integer, db.ForeignKey('location_details.id', ondelete='CASCADE'))
    location_details = db.relationship('LocationDetails', backref='locations')

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
            "address": self.address,
            "name": self.name,
            "description": self.description,
            "location_details_id": self.location_details_id,
            "location_details": self.location_details.serialize()
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
            self.address = data['address']
            self.name = data['name']
            self.description = data['description']
            self.location_details_id = data['location_details_id']
            self.location_details.deserialize(data['location_details'])

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
        return f"<id:{self.id}, address:{self.address}, name:{self.name},\
              description:{self.description}, location_details_id:{self.location_details_id},\
                location_details:{self.location_details}>"
