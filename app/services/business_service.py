from datetime import datetime, timezone
from uuid import uuid4

from app.models.business import BusinessCreate, BusinessResponse, BusinessUpdate
from app.repositories.business_repository import BusinessRepository


repository = BusinessRepository()


def create_business(business: BusinessCreate) -> BusinessResponse:
    business_response = BusinessResponse(
        id=str(uuid4()),
        tenant_id=business.tenant_id,

        name=business.name,
        website=business.website,
        phone=business.phone,
        email=business.email,

        address=business.address,
        city=business.city,
        state=business.state,
        zip_code=business.zip_code,

        timezone=business.timezone,
        services=business.services,

        sales_rep_id=business.sales_rep_id,

        status="active",
        created_at=datetime.now(timezone.utc),
        )

    return repository.save(business_response)

def get_business(business_id: str) -> BusinessResponse | None:
    return repository.get_by_id(business_id)

def update_business(business_id: str, updates: BusinessUpdate) -> BusinessResponse | None:
    update_data = updates.model_dump(exclude_unset=True)

    return repository.update(
        business_id,
        update_data,
    )

def delete_business(business_id: str) -> bool:
    return repository.delete(business_id)
