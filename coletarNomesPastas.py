import os
import pandas as pd
from datetime import datetime
#ele precisa coletar, fazer a tabela, ai eu preciso fazer um código q una as outras tabelas de id e cpf, dps quando unir, lançar aqui e fazr relação id cpf.
# --- Caminhos ---
funcSet = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\setembro"
caminhoExcel = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\umasopasta\coletarNomesPastas.xlsx"
caminho_planilhas = r"C:\Users\melissa.lemes\OneDrive - HITSS DO BRASIL SERVIÇOS TECNOLOGICOS LTDA\Área de Trabalho\coletando cpf"

# --- 1. Lê todas as planilhas com ID e CPF ---
dfs_ref = []
for arquivo in os.listdir(caminho_planilhas):
    if arquivo.endswith(".xlsx"):
        caminho_arquivo = os.path.join(caminho_planilhas, arquivo)
        df_temp = pd.read_excel(caminho_arquivo, dtype=str)
        # padroniza os nomes das colunas
        df_temp.columns = [c.strip().upper().replace(" ", "_") for c in df_temp.columns]

        if "ID_DA_VAGA" in df_temp.columns and "CPF" in df_temp.columns:
            dfs_ref.append(df_temp[["ID_DA_VAGA", "CPF"]].rename(columns={"ID_DA_VAGA": "CD_VAGA"}))

if dfs_ref:
    df_ref = pd.concat(dfs_ref, ignore_index=True).drop_duplicates(subset=["CD_VAGA"])
    df_ref["CD_VAGA"] = df_ref["CD_VAGA"].astype(str).str.strip()
    df_ref["CPF"] = df_ref["CPF"].astype(str).str.strip()
else:
    df_ref = pd.DataFrame(columns=["CD_VAGA", "CPF"])

# --- 2. Lê a planilha principal ---
if os.path.exists(caminhoExcel):
    df_principal = pd.read_excel(caminhoExcel, dtype=str)
else:
    df_principal = pd.DataFrame()

# --- 3. Coleta os nomes das pastas e cria DataFrame ---
pastas = [nome for nome in os.listdir(funcSet) if os.path.isdir(os.path.join(funcSet, nome))]
dados = []
for p in pastas:
    partes = p.split(" - ")
    if len(partes) == 3:
        nome, cd_vaga, data_str = partes
    elif len(partes) == 2:
        nome, cd_vaga = partes
        data_str = ""
    else:
        nome, cd_vaga, data_str = p, "", ""

    dados.append({
        "NOME": nome.strip(),
        "CD_VAGA": cd_vaga.strip(),
        "DATA": data_str.strip(),
        "NOME_PASTA": p,
        "MES_ADMISSAO": datetime.now().strftime("%m/%Y")
    })

df_novo = pd.DataFrame(dados)

# --- 4. Junta com dados antigos ---
if not df_principal.empty:
    df_final = pd.concat([df_principal, df_novo]).drop_duplicates(subset=["NOME_PASTA"]).reset_index(drop=True)
else:
    df_final = df_novo

# --- 5. Faz o merge com os CPFs ---
df_final["CD_VAGA"] = df_final["CD_VAGA"].astype(str).str.strip()
df_final = df_final.merge(df_ref, on="CD_VAGA", how="left")

# --- 6. Salva ---
df_final.to_excel(caminhoExcel, index=False)
print("✅ Planilha atualizada com sucesso!")

