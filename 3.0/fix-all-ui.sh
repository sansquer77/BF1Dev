#!/bin/bash
# fix-all-ui.sh - Corrige todos os arquivos de UI automaticamente

echo "🔧 Iniciando correção de todos os arquivos de UI..."

cd "$(dirname "$0")" || exit

# Array com todos os arquivos a corrigir
files=(
    "ui/gestao_pilotos.py"
    "ui/gestao_provas.py"
    "ui/gestao_apostas.py"
    "ui/gestao_resultados.py"
    "ui/usuarios.py"
    "ui/backup.py"
)

# Fazer backup antes
backup_dir="ui_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"
cp ui/*.py "$backup_dir/" 2>/dev/null
echo "✅ Backup criado em: $backup_dir"

# Corrigir cada arquivo
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        # Remover conn.close()
        sed -i '' '/^\s*conn\.close()/d' "$file"
        
        # Adicionar 'with' ao padrão "conn = db_connect()"
        sed -i '' 's/conn = db_connect()/with db_connect() as conn:/' "$file"
        
        echo "✅ Corrigido: $file"
    else
        echo "⚠️  Arquivo não encontrado: $file"
    fi
done

echo ""
echo "🎉 Correção concluída!"
echo "Para testar: streamlit run main.py"
