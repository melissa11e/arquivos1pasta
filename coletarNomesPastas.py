import os
import shutil
import pandas as pd
from datetime import datetime
import shutil

# --- Caminhos ---
funcSet = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\umasopasta\funcionarios\agosto25"
caminhoExcel = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\umasopasta\coletarNomesPastas.xlsx"
caminho_planilhas = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\umasopasta\planilhasIDCPF"


# =============================================================
# ETAPA 1 - Eliminar subpastas
# =============================================================

# deixar só documentos pdf
#apagar pastas que sobram vazias

# Caminho da pasta principal (ajuste esse caminho!)
caminhoFunc = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\umasopasta\funcionarios\agosto25"

# Função para encurtar nomes de arquivos muito grandes
def encurtar_nome(arquivo, limite=100): #garante que o nome do arquivo não ultrapasse o limite
    nome, ext = os.path.splitext(arquivo) #separa o nome e a extensão
    if len(nome) > limite: #se o nome for maior que o limite
        nome = nome[:limite - 3] + "..." #corta o nome e adiciona "..."
    return nome + ext #retorna o novo nome com a extensão

# Percorre todas as pastas de funcionários
for funcionario in os.listdir(caminhoFunc): #está fazendo uma lista dos funcionarios na pasta. os.listdir faz uma lista
    caminhoFuncionario = os.path.join(caminhoFunc, funcionario) #está fazendo o caminho de cada pasta de funcionario
    
    # Garante que é uma pasta (não um arquivo solto)
    if os.path.isdir(caminhoFuncionario):
        print(f"📂 Organizando arquivos de: {funcionario}")
        
        # Percorre todas as subpastas dentro da pasta do funcionário
        for raiz, _, arquivos in os.walk(caminhoFuncionario): #os.walk percorre toda a pasta do funcionario
            for arquivo in arquivos:
                origem = os.path.join(raiz, arquivo)
                destino = os.path.join(caminhoFuncionario, arquivo)
                
                # Evita mover se já estiver na pasta principal
                if raiz != caminhoFuncionario:
                    try:
                        # Encurta o nome se for muito longo
                        arquivo_curto = encurtar_nome(arquivo) #usa a função para evitar nomes longos
                        destino = os.path.join(caminhoFuncionario, arquivo_curto) #cria o caminho com o nome encurtado

                        # Se já existir um arquivo com o mesmo nome, renomeia
                        if os.path.exists(destino):
                            nome, ext = os.path.splitext(arquivo_curto)
                            novo_nome = f"{nome}_duplicado{ext}"
                            destino = os.path.join(caminhoFuncionario, novo_nome)
                        
                        shutil.move(origem, destino)
                    except Exception as e:
                        print(f"⚠️ Erro ao mover {arquivo}: {e}")

        print(f"✅ Concluído: {funcionario}\n")

print("🏁 Todos os arquivos foram organizados!")

# =============================================================
# ETAPA 2 + 3 - Coleta nomes, junta com planilhas e atualiza CPFs
# =============================================================

dfs_ref = []
for arquivo in os.listdir(caminho_planilhas):
    if arquivo.endswith(".xlsx"):
        caminho_arquivo = os.path.join(caminho_planilhas, arquivo)
        df_temp = pd.read_excel(caminho_arquivo, dtype=str)
        colunas = [c.strip().upper().replace(" ", "_") for c in df_temp.columns]
        df_temp.columns = colunas

        col_id = next((c for c in colunas if "ID" in c and "VAGA" in c), None)
        col_cpf = next((c for c in colunas if "CPF" in c), None)
        col_nome = next((c for c in colunas if "NOME" in c), None)

        if col_id and col_cpf:
            colunas_para_pegar = {col_id: "Id da vaga", col_cpf: "CPF"}
            if col_nome:
                colunas_para_pegar[col_nome] = "Nome completo"
            df_filtrado = df_temp[list(colunas_para_pegar.keys())].rename(columns=colunas_para_pegar)
            dfs_ref.append(df_filtrado)

if dfs_ref:
    df_ref = pd.concat(dfs_ref, ignore_index=True).drop_duplicates(subset=["Id da vaga"])
    df_ref["Id da vaga"] = df_ref["Id da vaga"].astype(str).str.strip()
    df_ref["CPF"] = df_ref["CPF"].astype(str).str.strip()
else:
    df_ref = pd.DataFrame(columns=["Id da vaga", "CPF", "Nome completo"])

if os.path.exists(caminhoExcel):
    df_principal = pd.read_excel(caminhoExcel, dtype=str)
else:
    df_principal = pd.DataFrame()

pastas = [nome for nome in os.listdir(funcSet) if os.path.isdir(os.path.join(funcSet, nome))]
dados = []
for p in pastas:
    partes = p.split(" - ")
    if len(partes) == 3:
        nome, id_vaga, data_str = partes
    elif len(partes) == 2:
        nome, id_vaga = partes
        data_str = ""
    else:
        nome, id_vaga, data_str = p, "", ""

    dados.append({
        "Nome": nome.strip(),
        "Id da vaga": id_vaga.strip(),
        "NOME_PASTA": p,
    })

df_novo = pd.DataFrame(dados)

if not df_principal.empty:
    df_final = pd.concat([df_principal, df_novo], ignore_index=True)
    df_final = df_final.drop_duplicates(subset=["NOME_PASTA"]).reset_index(drop=True)
else:
    df_final = df_novo.copy()

df_final["Id da vaga"] = df_final["Id da vaga"].astype(str).str.strip()
df_ref["Id da vaga"] = df_ref["Id da vaga"].astype(str).str.strip()
df_merge = df_final.merge(df_ref, on="Id da vaga", how="left", suffixes=("", "_novo"))

for coluna in ["CPF", "Nome completo"]:
    if coluna in df_merge.columns and f"{coluna}_novo" in df_merge.columns:
        df_merge[coluna] = df_merge[coluna].fillna(df_merge[f"{coluna}_novo"])
        df_merge.drop(columns=[f"{coluna}_novo"], inplace=True)

df_final = df_merge
df_final.to_excel(caminhoExcel, index=False)

total = len(df_final)
sem_cpf = df_final["CPF"].isna().sum() if "CPF" in df_final.columns else 0
print(f"✅ Planilha atualizada com sucesso! Total de registros: {total}")
print(f"📋 Linhas sem CPF: {sem_cpf}")

# =============================================================
# ETAPA 3 - Renomeia pastas com CPF e nome curto
# =============================================================

def encurtar_nome(nome, limite=100):
    """Evita nomes de pasta muito longos"""
    if len(nome) > limite:
        nome = nome[:limite - 3] + "..."
    return nome

print("\n🚀 Iniciando renomeação das pastas...")

for _, linha in df_final.iterrows():
    nome_pasta_antiga = linha.get("NOME_PASTA", "")
    nome_curto = linha.get("Nome", "")
    cpf = linha.get("CPF", "")

    if not cpf or not nome_pasta_antiga:
        continue  # pula se não tiver CPF

    pasta_antiga = os.path.join(funcSet, nome_pasta_antiga)
    if not os.path.exists(pasta_antiga):
        continue  # pula se não existir

    # monta novo nome
    nova_pasta_nome = encurtar_nome(f"{nome_curto} - {cpf}")
    pasta_nova = os.path.join(funcSet, nova_pasta_nome)

    # evita sobrescrever
    if os.path.exists(pasta_nova):
        print(f"⚠️ Já existe pasta com nome {nova_pasta_nome}, pulando...")
        continue

    try:
        os.rename(pasta_antiga, pasta_nova)
        print(f"✅ {nome_pasta_antiga} ➜ {nova_pasta_nome}")
        # atualiza o nome na planilha
        df_final.loc[df_final["NOME_PASTA"] == nome_pasta_antiga, "NOME_PASTA"] = nova_pasta_nome
    except Exception as e:
        print(f"❌ Erro ao renomear {nome_pasta_antiga}: {e}")

# salva novamente com os novos nomes
df_final.to_excel(caminhoExcel, index=False)
print("\n🏁 Renomeação concluída com sucesso!")




