"""
Model for Locations

All of the models are stored in this module
"""

import logging
from service.models import PersistentBase, DataValidationError
from service import db

logger = logging.getLogger('flask.app')


class User(db.Model, PersistentBase):
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

    # CREATE TABLE users (
    #     id INT AUTO_INCREMENT PRIMARY KEY,
    #     firstname varchar(255) NOT NULL,
    #     lastname varchar(255) NOT NULL,
    #     username varchar(255) NOT NULL,
    #     PASSWORD varchar(255) NOT NULL,
    #     email varchar(255) NOT NULL,
    #     CONSTRAINT unique_username UNIQUE(username),
    #     CONSTRAINT unique_email UNIQUE(email)
    # );


    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(255), nullable = False)
    lastname = db.Column(db.String(255), nullable = False)
    username = db.Column(db.String(255), nullable = False, unique = True)
    email = db.Column(db.String(255), nullable = False, unique = True)
    password = db.Column(db.String(255), nullable = False)

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
            "firstname": self.firstname,
            "lastname": self.lastname,
            "username": self.username,
            "email": self.email,
            "password": self.password
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
            self.firstname = data['firstname']
            self.lastname = data['lastname']
            self.username = data['username']
            self.email = data['email']
            self.password = data['password']

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
        return f"<id:{self.id}, firstname:{self.firstname}, lastname:{self.lastname},\
              username:{self.username}, email:{self.email},\
                password:{self.password}>"
