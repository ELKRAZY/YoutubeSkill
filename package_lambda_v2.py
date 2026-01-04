import shutil
import os
import zipfile

def package_lambda():
    output_filename = 'lambda_function.zip'
    pkg_dir = 'lambda_pkg'
    src_dir = 'lambda'
    secrets_file = 'secrets.json'
    
    # Eliminar zip anterior
    if os.path.exists(output_filename):
        os.remove(output_filename)
        print(f"Eliminado {output_filename} anterior.")

    print(f"Creando {output_filename}...")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Añadir dependencias (lambda_pkg)
        if os.path.exists(pkg_dir):
            for root, dirs, files in os.walk(pkg_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, pkg_dir)
                    zf.write(file_path, arcname)
            print(f"Dependencias añadidas de {pkg_dir}")
        
        # 2. Añadir código fuente (lambda)
        if os.path.exists(src_dir):
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    if file == "test_search.py": continue # No incluir tests
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, src_dir)
                    zf.write(file_path, arcname)
            print(f"Código fuente añadido de {src_dir}")

        # 3. Añadir secrets.json
        if os.path.exists(secrets_file):
            zf.write(secrets_file, 'secrets.json')
            print(f"Añadido {secrets_file}")
            
    print(f"[OK] Paquete creado: {output_filename}")
    print(f"Tamaño: {os.path.getsize(output_filename) / 1024 / 1024:.2f} MB")

if __name__ == '__main__':
    package_lambda()
