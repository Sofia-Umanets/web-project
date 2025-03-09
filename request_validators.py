import re
from datetime import date
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

class SexEnum(StrEnum):
    male = "male"
    female = "female"

class LanguageEnum(StrEnum):
    pascal = "Pascal"
    c = "C"
    cpp = "C++"
    javascript = "JavaScript"
    php = "PHP"
    python = "Python"
    java = "Java"
    haskel = "Haskel"
    clojure = "Clojure"
    prolog = "Prolog"
    scala = "Scala"
    go = "Go"

class RequestModel(BaseModel):
    name: str = Field(..., max_length=150)
    phone: PhoneNumber = Field(..., max_length=20)
    email: EmailStr = Field(..., max_length=100)
    birthday: date
    sex: SexEnum
    biography: str
    languages: list[LanguageEnum]
    agree_to_terms: bool = Field(..., description="Согласие с условиями")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if re.fullmatch(r"([a-zA-Zа-яА-ЯёЁ\s]+)", value) is None:
            raise ValueError("The value is not a valid name")
        return value

    @field_validator("birthday")
    @classmethod
    def validate_birthday(cls, value: date) -> date:
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if 18 <= age <= 110:
            return value
        raise ValueError("The value is not a valid birthday")

    @field_validator("agree_to_terms")
    @classmethod
    def validate_agree_to_terms(cls, value: bool) -> bool:
        if not value:
            raise ValueError("You must agree to the terms and conditions")
        return value