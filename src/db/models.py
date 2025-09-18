from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey, UniqueConstraint


class Base(DeclarativeBase):
    pass


class City(Base):
    __tablename__ = "cities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wikidata_id: Mapped[str | None] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    country: Mapped[str | None] = mapped_column(String(255))
    population: Mapped[int | None] = mapped_column(Integer)
    population_year: Mapped[int | None] = mapped_column(Integer)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str | None] = mapped_column(String(255))
    last_updated: Mapped[str | None] = mapped_column(String(64))

    museums: Mapped[list["Museum"]] = relationship(back_populates="city")


class Museum(Base):
    __tablename__ = "museums"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    wikidata_id: Mapped[str | None] = mapped_column(String(32), index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    city_id: Mapped[int | None] = mapped_column(ForeignKey("cities.id"))
    wikipedia_url: Mapped[str | None] = mapped_column(String(512))
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    source: Mapped[str | None] = mapped_column(String(255))
    last_updated: Mapped[str | None] = mapped_column(String(64))

    city: Mapped[City | None] = relationship(back_populates="museums")
    stats: Mapped[list["MuseumStat"]] = relationship(back_populates="museum")

    __table_args__ = (
        UniqueConstraint("name", "city_id", name="uq_museum_name_city"),
    )


class MuseumStat(Base):
    __tablename__ = "museum_stats"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    museum_id: Mapped[int] = mapped_column(ForeignKey("museums.id"))
    year: Mapped[int] = mapped_column(Integer, index=True)
    visitors: Mapped[int] = mapped_column(Integer)
    source: Mapped[str | None] = mapped_column(String(255))
    last_updated: Mapped[str | None] = mapped_column(String(64))

    museum: Mapped[Museum] = relationship(back_populates="stats")

    __table_args__ = (
        UniqueConstraint("museum_id", "year", name="uq_museum_year"),
    )


__all__ = ["Base", "City", "Museum", "MuseumStat"]
