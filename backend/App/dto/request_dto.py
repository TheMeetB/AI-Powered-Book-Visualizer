from pydantic import BaseModel, EmailStr


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRegisterRequest(UserLoginRequest):
    username: str


class UserDeleteRequest(UserLoginRequest):
    pass


class ForgetPasswordRequest(BaseModel):
    email: EmailStr


class ForgetPasswordOtpRequest(ForgetPasswordRequest):
    otp: int


class ResetPasswordRequest(ForgetPasswordRequest):
    password: str


class TokenData(BaseModel):
    email: EmailStr | None = None


class RefreshTokenData(BaseModel):
    token: str
