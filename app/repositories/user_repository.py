from app.models.user import UserResponse


class UserRepository:
    def __init__(self):
        self.users: dict[str, UserResponse] = {}

    def create(self, user: UserResponse) -> UserResponse:
        self.users[user.id] = user
        return user

    def get_by_id(self, user_id: str) -> UserResponse | None:
        return self.users.get(user_id)

def update(self, user_id: str, updates: dict) -> UserResponse | None:
    user = self.users.get(user_id)

    if user is None:
        return None

    for field, value in updates.items():
        setattr(user, field, value)

    return user