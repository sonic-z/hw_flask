import pydantic


class UserBase(pydantic.BaseModel):
    name: str
    password: str

    @pydantic.field_validator("password")
    @classmethod
    def check_password(cls, value):
        if len(value) < 8:
            raise ValueError("password is too short")
        return value


class CreateUser(UserBase):
    name: str
    password: str


class UpdateUser(UserBase):
    name: str | None = None
    password: str | None = None
    

class AdsBase(pydantic.BaseModel):
    header: str
    text: str
    price: int


class CreateAd(AdsBase):
    header: str
    text: str
    price: int
    owner_id: int


class UpdateAd(AdsBase):
    header: str | None = None
    text: str | None = None
    price: int | None = None
    owner_id: int | None = None
