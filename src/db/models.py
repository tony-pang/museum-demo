from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint


class Base(DeclarativeBase):
    """
    Base class for all models.
    """
    pass


class City(Base):
    """
    City model.
    """
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wikidata_id: Mapped[str | None] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    country: Mapped[str | None] = mapped_column(String(255))
    population: Mapped[int | None] = mapped_column(Integer)
    last_updated: Mapped[str | None] = mapped_column(String(64))

    museums: Mapped[list["Museum"]] = relationship(back_populates="city")


class Museum(Base):
    """
    Museum model.
    """
    __tablename__ = "museums"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wikidata_id: Mapped[str | None] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    city_id: Mapped[int | None] = mapped_column(ForeignKey("cities.id"))
    last_updated: Mapped[str | None] = mapped_column(String(64))

    city: Mapped[City | None] = relationship(back_populates="museums")
    stats: Mapped[list["MuseumStat"]] = relationship(back_populates="museum")

    __table_args__ = (
        UniqueConstraint("name", "city_id", name="uq_museum_name_city"),
    )


class MuseumStat(Base):
    """
    Museum stat model.
    """
    __tablename__ = "museum_stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    museum_id: Mapped[int] = mapped_column(ForeignKey("museums.id"))
    year: Mapped[int] = mapped_column(Integer, index=True)
    visitors: Mapped[int] = mapped_column(Integer)
    last_updated: Mapped[str | None] = mapped_column(String(64))

    museum: Mapped[Museum] = relationship(back_populates="stats")

    __table_args__ = (
        UniqueConstraint("museum_id", "year", name="uq_museum_year"),
    )


__all__ = ["Base", "City", "Museum", "MuseumStat"]
