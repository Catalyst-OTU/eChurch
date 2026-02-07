from pydantic import BaseModel


## pydantic model for reset password request
class ResetPasswordRequest(BaseModel):
    email: str


## Pydantic model for resetting the password
class ResetPasswordForm(BaseModel):
    token: str
    new_password: str
