# TCC - LUME Skin

Projeto Django para o TCC — LUME Skin com conexao com o banco de dados mysql

## como executar (desenvolvimento)

1. crie e ative um ambiente virtual
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
2. Instale dependências (crie `requirements.txt` se necessário):
```powershell
pip install -r requirements.txt
```
3. Rode migrações e inicie o servidor:
```powershell
python manage.py migrate
python manage.py runserver
```

## Observações
- O banco SQLite `db.sqlite3` está incluído no repositório por padrão; remova-o do controle de versão se preferir não publicá-lo.
- Para gerar `requirements.txt` a partir do ambiente atual:
```powershell
pip freeze > requirements.txt
```
## altere a senha do banco de dados em settings.py
