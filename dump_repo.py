import os

# O que NÃO queremos que a IA leia (lixo, binários, dependências)
EXCLUDE_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'env', 'node_modules', '.pytest_cache'}
# O que é útil para a arquitetura
ALLOWED_EXT = {'.py', '.md', '.sql', '.toml', '.yaml', '.txt'}

with open("klipper_context.txt", "w", encoding="utf-8") as outfile:
    for root, dirs, files in os.walk("."):
        # Modifica a lista de diretórios in-place para pular os excluídos
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if any(file.endswith(ext) for ext in ALLOWED_EXT):
                filepath = os.path.join(root, file)

                # Ignora o próprio script de dump e o arquivo de saída
                if file in ["dump_repo.py", "klipper_context.txt"]:
                    continue

                # Cria um separador claro para a IA entender onde começa e termina cada módulo
                outfile.write(f"\n\n{'='*60}\n")
                outfile.write(f"FILE: {filepath}\n")
                outfile.write(f"{'='*60}\n\n")

                try:
                    with open(filepath, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"// Erro ao ler arquivo: {e}\n")

print("Dump concluído! Arquivo 'klipper_context.txt' gerado com sucesso.")
