import json
import os

def update_manifest():
    # Rutas relativas
    base_dir = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(base_dir, 'secrets.json')
    skill_json_path = os.path.join(base_dir, 'skill-package', 'skill.json')

    # Verificar secrets.json
    if not os.path.exists(secrets_path):
        print("❌ Error: No se encontró secrets.json")
        return

    # Leer secretos
    with open(secrets_path, 'r') as f:
        secrets = json.load(f)
    
    arn = secrets.get('lambda', {}).get('arn')
    if not arn:
        print("❌ Error: No se encontró lambda.arn en secrets.json")
        return

    # Leer skill.json
    with open(skill_json_path, 'r') as f:
        skill_data = json.load(f)

    # Actualizar URI
    current_uri = skill_data['manifest']['apis']['custom']['endpoint']['uri']
    print(f"ℹ️  URI actual: {current_uri}")
    
    skill_data['manifest']['apis']['custom']['endpoint']['uri'] = arn
    
    # Guardar
    with open(skill_json_path, 'w') as f:
        json.dump(skill_data, f, indent=2)
        
    print(f"✅ skill.json actualizado correctamente con el ARN: {arn}")
    print("⚠️  IMPORTANTE: No hagas 'git commit' de skill.json con el ARN real si vas a publicar este código.")

if __name__ == '__main__':
    update_manifest()
