import os
import shutil

# Caminho da pasta principal (ajuste esse caminho!)
caminhoFA = r"C:\Users\nmeli\OneDrive\Área de Trabalho\funcionariosAbril"

# Percorre todas as pastas de funcionários
for funcionario in os.listdir(caminhoFA): #está fazendo uma lista dos funcionarios na pasta. os.listdir faz uma lista
    caminhoFuncionario = os.path.join(caminhoFA, funcionario) #está fazendo o caminho de cada pasta de funcionario
    
    # Garante que é uma pasta (não um arquivo solto)
    if os.path.isdir(caminhoFuncionario):
        print(f"📂 Organizando arquivos de: {funcionario}")
        
        # Percorre todas as subpastas dentro da pasta do funcionário
        for raiz, _, arquivos in os.walk(caminhoFuncionario):#os.walk percorre toda a pasta do funcionario
            for arquivo in arquivos:
                origem = os.path.join(raiz, arquivo)
                destino = os.path.join(caminhoFuncionario, arquivo)
                
                # Evita mover se já estiver na pasta principal
                if raiz != caminhoFuncionario:
                    try:
                        # Se já existir um arquivo com o mesmo nome, renomeia
                        if os.path.exists(destino):
                            nome, ext = os.path.splitext(arquivo)
                            novo_nome = f"{nome}_duplicado{ext}"
                            destino = os.path.join(caminhoFuncionario, novo_nome)
                        
                        shutil.move(origem, destino)
                    except Exception as e:
                        print(f"⚠️ Erro ao mover {arquivo}: {e}")

        print(f"✅ Concluído: {funcionario}\n")

print("🏁 Todos os arquivos foram organizados!")
