from typing import Annotated

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

# camelCase 입력 alias (CMS는 camelCase, snake_case 모두 허용)
_IMAGE_IN = AliasChoices("imageUrl", "image_url")
_ACTIVE_IN = AliasChoices("isActive", "is_active")
_SORT_IN = AliasChoices("sortOrder", "sort_order")


class PlaceBase(BaseModel):
    """camelCase 입출력. CMS·안드로이드가 동일 camelCase 구조를 사용한다."""

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class PlaceCreate(PlaceBase):
    title: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=50)
    location: str = Field(min_length=1, max_length=500)
    hours: str | None = Field(default=None, max_length=200)
    fee: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=50)
    description: str | None = None
    image_url: Annotated[
        str | None, Field(validation_alias=_IMAGE_IN, serialization_alias="imageUrl")
    ] = None
    is_active: Annotated[
        bool, Field(validation_alias=_ACTIVE_IN, serialization_alias="isActive")
    ] = True
    sort_order: Annotated[
        int, Field(ge=0, validation_alias=_SORT_IN, serialization_alias="sortOrder")
    ] = 0


class PlaceUpdate(PlaceBase):
    title: Annotated[str | None, Field(min_length=1, max_length=200)] = None
    category: Annotated[str | None, Field(min_length=1, max_length=50)] = None
    location: Annotated[str | None, Field(min_length=1, max_length=500)] = None
    hours: Annotated[str | None, Field(max_length=200)] = None
    fee: Annotated[str | None, Field(max_length=200)] = None
    phone: Annotated[str | None, Field(max_length=50)] = None
    description: str | None = None
    image_url: Annotated[str | None, Field(validation_alias=_IMAGE_IN)] = None
    is_active: Annotated[bool | None, Field(validation_alias=_ACTIVE_IN)] = None
    sort_order: Annotated[int | None, Field(ge=0, validation_alias=_SORT_IN)] = None


class PlaceResponse(PlaceBase):
    """안드로이드/CMS 공용 평탄 응답. by_alias 직렬화로 imageUrl 등 camelCase 출력."""

    id: int
    title: str
    category: str
    location: str
    hours: str | None = None
    fee: str | None = None
    phone: str | None = None
    description: str | None = None
    image_url: Annotated[str | None, Field(serialization_alias="imageUrl")] = None
    is_active: Annotated[bool, Field(serialization_alias="isActive")]
    sort_order: Annotated[int, Field(serialization_alias="sortOrder")]
