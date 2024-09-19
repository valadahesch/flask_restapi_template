from .sys_response import *
from .response_schema import marsh_response


class SSOUser:
    UserID = ''
    UserName = ''
    DisplayName = ''
    FirstName = ''
    LastName = ''
    NickName = ''
    UserType = ''
    CompanyName = ''
    Mobile = ''
    Email = ''
    TimeDiff = ''
    OEMBrand = ''
    Language = ''

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def to_dict(self):
        return {
            "user_id": self.UserID, "user_name": self.UserName, "dp_name": self.DisplayName,
            "first_name": self.FirstName, "last_name": self.LastName, "nick_name": self.NickName,
            "user_type": self.UserType, "company_name": self.CompanyName, "mobile": self.Mobile,
            "email": self.Email, "time_diff": self.TimeDiff, "oem_brand": self.OEMBrand,
            "language": self.Language
        }