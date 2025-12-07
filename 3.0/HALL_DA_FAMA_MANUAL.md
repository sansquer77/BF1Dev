# Hall da Fama - Adição de Resultados Históricos

## Visão Geral

O módulo Hall da Fama agora permite que usuários com perfil **Master** adicionem, editem e deletem resultados históricos de classificações de participantes em diferentes temporadas.

## Funcionalidades Adicionadas

### 1. Adicionar Resultado Manual (➕ Adicionar Resultado Manual)

Permite adicionar um único resultado histórico manualmente:

- **Selecione o Participante**: Dropdown com lista de usuários registrados
- **Ano/Temporada**: Número do ano ou identificador da temporada (1990-presente)
- **Posição**: Ranking do participante naquela temporada (1-100)

**Como usar:**
1. Expanda a seção "➕ Adicionar Resultado Manual"
2. Selecione o participante, ano e posição
3. Clique em "✅ Adicionar Resultado"
4. O sistema valida se já existe um registro para esse participante nessa temporada

**Validações:**
- Usuário deve estar cadastrado
- Não permite duplicatas (mesmo usuário + mesma temporada)
- Posição entre 1 e 100

### 2. Gerenciar Registros (✏️ Editar/Deletar Registros)

Exibe todos os registros existentes em formato de tabela com opção de deletar:

- Lista todos os registros com: Nome do participante, Posição, Temporada
- Botão 🗑️ para deletar cada registro
- Atualização em tempo real após exclusão

**Como usar:**
1. Expanda a seção "✏️ Editar/Deletar Registros"
2. Visualize a lista completa de registros
3. Clique em "🗑️ Deletar" ao lado do registro desejado
4. A página atualiza automaticamente

### 3. Importação em Lote (📥 Importação em Lote)

Importa 20 anos de dados fictícios (2005-2024):

- Dados já vêm pré-configurados no código
- Barra de progresso durante a importação
- Validações automáticas de duplicatas
- Relatório final com quantidade importada/ignorada

**Como usar:**
1. Expanda a seção "📥 Importar 20 anos de resultados"
2. Clique em "🔄 Importar Dados Históricos (2005-2024)"
3. Acompanhe a barra de progresso
4. Veja o relatório de sucesso

---

## API de Serviço (`hall_da_fama_service.py`)

Disponível uma camada de serviço completa com funções reutilizáveis:

### `adicionar_resultado_historico(usuario_id, posicao, temporada)`
Adiciona um novo resultado histórico.

**Parâmetros:**
- `usuario_id` (int): ID do usuário
- `posicao` (int): Posição (1-1000)
- `temporada` (str): Ano ou ID da temporada

**Retorno:**
```python
{
    "success": bool,
    "message": str,
    "id": int  # ID do novo registro (se sucesso)
}
```

**Exemplo:**
```python
from services.hall_da_fama_service import adicionar_resultado_historico

resultado = adicionar_resultado_historico(
    usuario_id=5,
    posicao=3,
    temporada="2023"
)

if resultado["success"]:
    print(f"Registro adicionado com ID {resultado['id']}")
else:
    print(f"Erro: {resultado['message']}")
```

---

### `editar_resultado_historico(registro_id, posicao=None, temporada=None)`
Edita um resultado histórico existente.

**Parâmetros:**
- `registro_id` (int): ID do registro a editar
- `posicao` (int, opcional): Nova posição
- `temporada` (str, opcional): Nova temporada

**Retorno:**
```python
{
    "success": bool,
    "message": str
}
```

**Exemplo:**
```python
resultado = editar_resultado_historico(
    registro_id=42,
    posicao=5,
    temporada="2024"
)
```

---

### `deletar_resultado_historico(registro_id)`
Deleta um resultado histórico.

**Parâmetros:**
- `registro_id` (int): ID do registro a deletar

**Retorno:**
```python
{
    "success": bool,
    "message": str
}
```

**Exemplo:**
```python
resultado = deletar_resultado_historico(registro_id=42)
```

---

### `importar_resultados_em_lote(dados)`
Importa múltiplos resultados em uma transação.

**Parâmetros:**
- `dados` (list): Lista de dicts com `usuario_id`, `posicao`, `temporada`

**Retorno:**
```python
{
    "success": bool,
    "imported": int,
    "skipped": int,
    "errors": list,
    "message": str
}
```

**Exemplo:**
```python
dados = [
    {"usuario_id": 1, "posicao": 1, "temporada": "2023"},
    {"usuario_id": 2, "posicao": 2, "temporada": "2023"},
    {"usuario_id": 3, "posicao": 3, "temporada": "2023"},
]

resultado = importar_resultados_em_lote(dados)
print(f"Importados: {resultado['imported']}, Ignorados: {resultado['skipped']}")
```

---

### `obter_historico_usuario(usuario_id)`
Retorna histórico completo de um usuário.

**Retorno:** Lista de tuplas (id, posicao, temporada, data_atualizacao)

---

### `obter_historico_temporada(temporada)`
Retorna todos os resultados de uma temporada.

**Retorno:** Lista de tuplas (usuario_id, nome, posicao)

---

### `listar_todas_temporadas()`
Retorna lista de todas as temporadas registradas.

**Retorno:** Lista de strings (anos/IDs)

---

## Estrutura de Dados

A tabela `posicoes_participantes` possui os seguintes campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | INTEGER PRIMARY KEY | Identificador único |
| `usuario_id` | INTEGER | Referência para `usuarios.id` |
| `posicao` | INTEGER | Ranking/Posição (1, 2, 3, ...) |
| `temporada` | TEXT | Ano ou ID da temporada (ex: "2023") |
| `data_atualizacao` | DATETIME | Timestamp da criação/atualização |

**Constraint:** `UNIQUE(usuario_id, temporada)` - Não permite duplicatas

---

## Exemplos de Uso Prático

### Cenário 1: Adicionar resultado de um campeonato anterior
```python
# Um Master quer registrar que João ficou em 2º lugar em 2022
resultado = adicionar_resultado_historico(
    usuario_id=7,  # ID do João
    posicao=2,
    temporada="2022"
)
```

### Cenário 2: Corrigir posição errada
```python
# Corrigir registro que estava errado
editar_resultado_historico(
    registro_id=15,
    posicao=1  # Mudou de 3º para 1º
)
```

### Cenário 3: Importar histórico de temporada anterior
```python
# Importar resultados de 2020 de forma programática
dados_2020 = [
    {"usuario_id": 1, "posicao": 1, "temporada": "2020"},
    {"usuario_id": 2, "posicao": 2, "temporada": "2020"},
    # ... mais registros
]
importar_resultados_em_lote(dados_2020)
```

---

## Observações

- **Acesso:** Apenas usuários com perfil `master` podem acessar as funções de administração
- **Validação:** Sistema valida automaticamente duplicatas e usuários inexistentes
- **Logging:** Todas as operações são registradas no logger `services.hall_da_fama`
- **Transações:** Importações em lote usam transação única para consistência
- **Performance:** Índices otimizados em `usuario_id` e `temporada` para consultas rápidas

