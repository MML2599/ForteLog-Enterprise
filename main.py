import sys
if not hasattr(sys, "maxint"):
    sys.maxint = 9223372036854775807
import os
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import bcrypt
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")
SECRET_KEY = os.getenv("SECRET_KEY", "SUA_CHAVE_SEGRETA_PROVISORIA")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)

class AssetModel(Base):
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    serial_number = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class LogModel(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, nullable=False)
    action = Column(String, nullable=False)
    target_id = Column(Integer, nullable=True)
    details = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(bind=engine)

# FORÇA A CRIAÇÃO DO USUÁRIO ADMIN DIRETAMENTE
db_init = SessionLocal()
try:
    user_exists = db_init.query(UserModel).filter(UserModel.username == "miranda_admin").first()
    if not user_exists:
        hashed = bcrypt.hashpw("123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        db_init.add(UserModel(username="miranda_admin", password_hash=hashed, role="Admin"))
        db_init.commit()
finally:
    db_init.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI(title="MilLog API v2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        from_attributes = True

class AssetCreate(BaseModel):
    name: str
    serial_number: str
    status: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    # Garante que não vai quebrar se a pasta templates ainda não existir
    if not os.path.exists(html_path):
        return "<h1>MilLog API v2 ativa!</h1><p>Crie a pasta 'templates/index.html' para ver a interface.</p>"
    with open(html_path, "r", encoding="utf-8") as file:
        return file.read()

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not bcrypt.checkpw(form_data.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    access_token = jwt.encode({"sub": user.username, "role": user.role, "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/assets", status_code=201)
def add_asset(asset: AssetCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        new_asset = AssetModel(name=asset.name, serial_number=asset.serial_number, status=asset.status)
        db.add(new_asset)
        db.commit()
        db.add(LogModel(user=payload["sub"], action="CRIAR", target_id=new_asset.id, details=f"Cadastrou o ativo {new_asset.name}"))
        db.commit()
        return {"message": "Sucesso"}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

@app.get("/assets", tags=["Inventário"])
def list_assets(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        # Valida o token antes de permitir listar os dados
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Busca usando o SQLAlchemy de forma limpa e profissional
        assets = db.query(AssetModel).all()
        
        return [
            {
                "id": asset.id, 
                "name": asset.name, 
                "serial_number": asset.serial_number, 
                "status": asset.status, 
                "registered_at": asset.created_at
            } 
            for asset in assets
        ]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

@app.get("/logs")
def view_logs(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return db.query(LogModel).order_by(LogModel.created_at.desc()).all()
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
