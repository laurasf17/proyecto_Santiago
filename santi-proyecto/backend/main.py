import os

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session, declarative_base


# ============================================================
# 1. CONFIGURACIÓN DE BASE DE DATOS
# ============================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:@localhost/mis_tareas_db_santi"
)

# Railway puede entregar mysql://...
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "mysql://",
        "mysql+pymysql://",
        1
    )

# Railway puede entregar postgres://...
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )


# ============================================================
# 2. CONFIGURACIÓN DE SQLALCHEMY
# ============================================================

Base = declarative_base()

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ============================================================
# 3. MODELO DE BASE DE DATOS
# ============================================================

class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(100))
    descripcion = Column(String(255))


# Crear las tablas si no existen
Base.metadata.create_all(bind=engine)


# ============================================================
# 4. FASTAPI
# ============================================================

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# 5. CONEXIÓN A LA BASE DE DATOS
# ============================================================

def get_db():

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# 6. RUTAS
# ============================================================

@app.get("/")
def ruta_principal():
    return {
        "mensaje": "Bienvenido a la API de Tareas, ya casi nos vamos"
    }


@app.get("/tareas")
def obtener_tareas(db: Session = Depends(get_db)):
    return db.query(Tarea).all()


@app.post("/tareas")
def crear_tarea(
    titulo: str,
    descripcion: str,
    db: Session = Depends(get_db)
):
    nueva_tarea = Tarea(
        titulo=titulo,
        descripcion=descripcion
    )

    db.add(nueva_tarea)
    db.commit()
    db.refresh(nueva_tarea)

    return nueva_tarea