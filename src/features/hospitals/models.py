from sqlmodel import Field, SQLModel


class Hospital(SQLModel, table=True):
    """
    Represents Hospital A, Hospital B, etc.
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    short_name: str = Field(
        unique=True,
        index=True,
        max_length=50,
    )


class MasterSlot(SQLModel, table=True):
    """
    The available shifts created by Admins.
    """

    id: int | None = Field(default=None, primary_key=True)
    hospital_id: int = Field(foreign_key="hospital.id")
    day_of_week: str
    specialty: str | None = Field(default=None)
    physician: str
    time_block: str
    contact_email: str
