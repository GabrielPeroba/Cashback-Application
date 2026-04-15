from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = FastAPI()

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    try:
        conn = psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None
    
def obter_ip(request: Request):
    x_forwarded = request.headers.get('X-Forwarded-For')
    if x_forwarded:
        # Se vier uma lista como "IP_CLIENTE, IP_PROXY", pegamos só o primeiro!
        return x_forwarded.split(',')[0].strip()
    return request.client.host

# =========================================================
# NOVO: Função que cria a tabela automaticamente no banco!
# =========================================================
def init_db():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cashback_history (
                        id SERIAL PRIMARY KEY,
                        ip_address VARCHAR(45) NOT NULL,
                        is_vip BOOLEAN NOT NULL,
                        purchase_value NUMERIC(10, 2) NOT NULL,
                        cashback_value NUMERIC(10, 2) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
            conn.commit()
            print("Tabela verificada/criada com sucesso!")
        except Exception as e:
            print(f"Erro ao criar tabela: {e}")
        finally:
            conn.close()

# Executa a função assim que o servidor liga
init_db()
# =========================================================

class CompraRequest(BaseModel):
    valor_compra: float
    is_vip: bool

def calcular_cashback(valor_final_compra: float, is_vip: bool) -> float:
    cashback_base = valor_final_compra * 0.05
    if valor_final_compra > 500.00:
        cashback_base *= 2
    
    cashback_bonus_vip = 0.0
    if is_vip:
        cashback_bonus_vip = cashback_base * 0.10
        
    return round(cashback_base + cashback_bonus_vip, 2)

@app.post("/api/calcular")
async def processar_compra(compra: CompraRequest, request: Request):
    client_ip = obter_ip(request)
    cashback_final = calcular_cashback(compra.valor_compra, compra.is_vip)
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO cashback_history (ip_address, is_vip, purchase_value, cashback_value)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (client_ip, compra.is_vip, compra.valor_compra, cashback_final)
                )
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail="Erro ao salvar no banco de dados.")
        finally:
            conn.close()
            
    return {"cashback": cashback_final, "ip": client_ip}

@app.get("/api/historico")
async def obter_historico(request: Request):
    client_ip = obter_ip(request)
    
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Sem conexão com o banco.")
        
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT is_vip, purchase_value, cashback_value, created_at 
                FROM cashback_history 
                WHERE ip_address = %s 
                ORDER BY created_at DESC
                """,
                (client_ip,)
            )
            historico = cursor.fetchall()
            return {"ip": client_ip, "historico": historico}
    finally:
        conn.close()

@app.get("/api/setup")
def setup_database():
    """Rota temporária para forçar a criação da tabela no banco de dados"""
    conn = get_db_connection()
    if not conn:
        return {"status": "erro", "mensagem": "Falha de conexão. Verifique se a variável DATABASE_URL está correta no Render."}
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cashback_history (
                    id SERIAL PRIMARY KEY,
                    ip_address VARCHAR(45) NOT NULL,
                    is_vip BOOLEAN NOT NULL,
                    purchase_value NUMERIC(10, 2) NOT NULL,
                    cashback_value NUMERIC(10, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        return {"status": "sucesso", "mensagem": "A tabela cashback_history foi criada e está pronta para uso!"}
    except Exception as e:
        return {"status": "erro_banco", "detalhe": str(e)}
    finally:
        conn.close()
