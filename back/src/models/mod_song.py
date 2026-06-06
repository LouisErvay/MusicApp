from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Uuid, func

from fastapi_files.models import File as PluginFile

from src.core.psql_db import Base

# Rend la table `file` (plugin) visible dans le même MetaData que Song,
# afin que SQLAlchemy puisse résoudre la FK song.file_id -> file.id.
PluginFile.__table__.to_metadata(Base.metadata)


class Song(Base):
    __tablename__ = "song"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    file_id = Column(Uuid(as_uuid=True), ForeignKey("file.id"), nullable=False)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
