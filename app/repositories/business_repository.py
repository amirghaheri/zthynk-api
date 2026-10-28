from app.models.business import BusinessResponse


class BusinessRepository:

    def __init__(self):
        self.businesses: dict[str, BusinessResponse] = {}

    def save(self, business: BusinessResponse) -> BusinessResponse:
        self.businesses[business.id] = business
        return business

    def get_by_id(self, business_id: str) -> BusinessResponse | None:
        return self.businesses.get(business_id)

    def update(
        self,
        business_id: str,
        updates: dict,
    ) -> BusinessResponse | None:
        business = self.businesses.get(business_id)

        if business is None:
            return None

        for field, value in updates.items():
            setattr(business, field, value)

        self.businesses[business_id] = business

        return business

    def delete(self, business_id: str) -> bool:
        if business_id not in self.businesses:
            return False

        del self.businesses[business_id]
        return True
