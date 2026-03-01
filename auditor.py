import os

# Ruta del directorio
dockerfile_directory = '.'

# Lista para almacenar las violaciones
violations = []

def check_dockerfile(dockerfile_path):
    with open(dockerfile_path, 'r') as f:
        lines = f.readlines()
        
    for line_num, line in enumerate(lines, 1):
        clean_line = line.strip()
        
        # 1. Verificación de 'latest' (Mejorada)
        if clean_line.startswith('FROM'):
            if ':latest' in clean_line or (':' not in clean_line and 'as' not in clean_line.lower()):
                violations.append(f"[{dockerfile_path}] Línea {line_num}: Evita usar 'latest'. Especifica una versión fija.")

        # 2. Verificación de secretos expuestos
        if 'echo' in clean_line and ('password' in clean_line.lower() or 'secret' in clean_line.lower()):
            violations.append(f"[{dockerfile_path}] Línea {line_num}: Posible secreto expuesto en el comando RUN.")

        # 3. Verificación de usuario ROOT
        if clean_line.startswith('USER root'):
            violations.append(f"[{dockerfile_path}] Línea {line_num}: El contenedor corre como root. Usa un usuario sin privilegios.")

# Recorrer archivos (buscando Dockerfile o Dockerfile.txt)
for root, dirs, files in os.walk(dockerfile_directory):
    for file in files:
        if file.startswith('DockerfileSeguro'):
            check_dockerfile(os.path.join(root, file))

# Imprimir resultados
print("\n--- Reporte de Auditoría ---")
if violations:
    for v in violations:
        print(f"[ALERTA] {v}")
else:
    print("No se encontraron violaciones críticas.")
