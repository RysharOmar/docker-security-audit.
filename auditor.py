import os
import sys

# Ruta del directorio actual
dockerfile_directory = '.'

# Lista para almacenar las violaciones
violations = []

def check_dockerfile(dockerfile_path):
    try:
        with open(dockerfile_path, 'r') as f:
            lines = f.readlines()
            
        for line_num, line in enumerate(lines, 1):
            clean_line = line.strip()
            
            # 1. Verificación de 'latest'
            if clean_line.startswith('FROM'):
                # Falla si usa :latest o si no especifica ninguna etiqueta (que por defecto es latest)
                if ':latest' in clean_line or (':' not in clean_line and ' AS ' not in clean_line.upper()):
                    violations.append(f"[{dockerfile_path}] Línea {line_num}: Evita usar 'latest'. Especifica una versión fija.")

            # 2. Verificación de secretos expuestos
            if 'RUN' in clean_line and 'echo' in clean_line.lower() and ('password' in clean_line.lower() or 'secret' in clean_line.lower()):
                violations.append(f"[{dockerfile_path}] Línea {line_num}: Posible secreto expuesto en el comando RUN.")

            # 3. Verificación de usuario ROOT
            if clean_line.upper().startswith('USER ROOT'):
                violations.append(f"[{dockerfile_path}] Línea {line_num}: El contenedor corre como root. Usa un usuario sin privilegios.")
    except Exception as e:
        print(f"Error al leer el archivo {dockerfile_path}: {e}")

# Contador para saber si analizamos algo
files_analyzed = 0

# Recorrer archivos buscando específicamente DockerfilePass
for root_dir, dirs, files in os.walk(dockerfile_directory):
    for file in files:
        # Esto encontrará 'DockerfilePass' y también 'DockerfilePass.txt' si existiera
        if file == 'DockerfilePass' or file == 'DockerfilePass.txt':
            files_analyzed += 1
            check_dockerfile(os.path.join(root_dir, file))

# Imprimir resultados
print("\n--- Reporte de Auditoría de Seguridad ---")

if files_analyzed == 0:
    print("[ERROR] No se encontró el archivo 'DockerfilePass' para analizar.")
    sys.exit(1)

if violations:
    for v in violations:
        print(f"[ALERTA] {v}")
    print(f"\nSe encontraron {len(violations)} violaciones de seguridad.")
    sys.exit(1)  # Hace que el pipeline de GitHub Actions se detenga (Falle)
else:
    print(f"Auditoría completada exitosamente sobre {files_analyzed} archivo(s).")
    print("No se encontraron violaciones críticas.")
    sys.exit(0)  # El pipeline puede continuar a la construcción de la imagen.
