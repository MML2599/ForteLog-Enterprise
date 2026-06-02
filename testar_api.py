import requests
import random

BASE_URL = "http://127.0.0.1:8000"

def rodar_testes():
    print("\n--- INICIANDO TESTES DO BACKEND (ForteLog Enterprise  ) ---\n")
    
    # 1. EFETUAR LOGIN (O usuário já é criado automaticamente pela API v2)
    print("[1/4] Efetuando login com o usuário criado automaticamente...")
    login_data = {
        "username": "miranda_admin",
        "password": "123"
    }
    
    try:
        token_res = requests.post(f"{BASE_URL}/token", data=login_data)
        if token_res.status_code == 200:
            token = token_res.json().get("access_token")
            print("🟢 Token JWT gerado com sucesso!\n")
        else:
            print(f"🔴 Falha no login. Status: {token_res.status_code} | Detalhes: {token_res.text}")
            return
    except requests.exceptions.ConnectionError:
        print("🔴 Erro de Conexão: Certifique-se de que a API está rodando com 'uvicorn main:app --reload'")
        return

    # Cabeçalho padrão de autenticação para as próximas rotas corporativas
    headers = {"Authorization": f"Bearer {token}"}

    # 2. CADASTRAR UM NOVO ATIVO MILITAR/CORPORATIVO
    print("[2/4] Cadastrando um novo ativo para o inventário...")
    
    # Gera um número aleatório para evitar o erro 500 de número de série duplicado no banco
    num_aleatorio = random.randint(10000, 99999)
    
    asset_data = {
        "name": "Servidor Dell PowerEdge R750",
        "serial_number": f"BR-MIL-{num_aleatorio}",
        "status": "Operacional"
    }
    
    asset_res = requests.post(f"{BASE_URL}/assets", json=asset_data, headers=headers)
    
    # Tratamento seguro para exibir a resposta mesmo que não seja um JSON válido
    try:
        conteudo_resposta = asset_res.json()
    except Exception:
        conteudo_resposta = asset_res.text

    print(f"Status: {asset_res.status_code} | Resposta: {conteudo_resposta}")
    
    if asset_res.status_code == 201 or asset_res.status_code == 200:
        print("🟢 Ativo registrado com sucesso no banco de dados!\n")
    else:
        print("🟡 Nota: O servidor recusou o cadastro. Verifique os logs do terminal da sua API.\n")

    # 3. LISTAR ATIVOS DO INVENTÁRIO
    print("[3/4] Testando: Listagem de ativos cadastrados no inventário...")
    list_res = requests.get(f"{BASE_URL}/assets", headers=headers)
    print(f"Status: {list_res.status_code}")
    print("Ativos encontrados:")
    print(list_res.json())
    print("🟢 Listagem executada com sucesso!\n")

    # 4. EXIBIR AUDITORIA DE LOGS DE SEGURANÇA
    print("[4/4] Consultando os Logs de Auditoria (Trilha de Segurança)...")
    logs_res = requests.get(f"{BASE_URL}/logs", headers=headers)
    print(f"Status: {logs_res.status_code}")
    print("Últimas ações registradas na auditoria:")
    
    try:
        logs_data = logs_res.json()
        for log in logs_data[:3]:  # Mostra apenas as 3 últimas linhas para ficar limpo
            print(f"  - [{log['created_at']}] Usuário: {log['user']} | Ação: {log['action']} | Detalhes: {log['details']}")
        print("\n🟢 Testes de auditoria finalizados com sucesso!")
    except Exception:
        print(f"🔴 Falha ao ler logs do servidor. Resposta bruta: {logs_res.text}")

if __name__ == "__main__":
    rodar_testes()
