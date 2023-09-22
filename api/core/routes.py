from flask import Flask, Blueprint, render_template, request, jsonify, redirect, url_for
from api.core.enums.http_status import  HttpStatus
from api.core.response.types import PayloadResponse
from api.core.utils import TksRequest
import json, sqlite3, requests
import numpy as np
from datetime import datetime
import pandas as pd


bp = Blueprint('core',__name__)
bp_v1 = Blueprint('status',__name__)


# Endpoint inicial mostrando membros da equipe
@bp.route('/')
def hello():
    return render_template('index.html')


# Endpoint de Configuracao
@bp.route('/configurations', methods = ['GET'])
def config():
    conn = sqlite3.connect('api/core/db/data.db')
    cursor = conn.cursor()
    
    get_df = TksRequest()
    df = get_df.get_data_response()
    colunas = ', '.join(df.columns)
    tabela = "configurations"

    sql = f'CREATE TABLE IF NOT EXISTS {tabela} (id INTEGER PRIMARY KEY AUTOINCREMENT, {colunas})'
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Configuração realizada com sucesso'})


# Endpoint de ingestao de dados para o banco
@bp.route('/ingest', methods=['POST'])
def ingest():
    get_df = TksRequest()
    df = get_df.get_data_response()
    colunas = ', '.join(df.columns)
    tabela = "configurations"
    values = df.values.tolist()
    placeholders = ', '.join(['?'] * len(df.columns))

    conn = sqlite3.connect('api/core/db/data.db')
    cursor = conn.cursor()
    sql = f'INSERT INTO {tabela} ({colunas}) VALUES ({placeholders})'
    values = [tuple(x) for x in df.values.tolist()]
    cursor.execute(f"DELETE FROM {tabela}")
    cursor.executemany(sql, values)
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'message': 'Insercao de dados realizada com sucesso'})


# Endpoint para gerar payload
@bp.route('/gerar_payload', methods=['POST'])
def gerar_payload():
    data = request.get_json()
    selected_fields = data.get('fields', [])
    num_rows = data.get('num_rows', 10)
    return redirect(url_for('core.read_data', selected_fields=selected_fields, num_rows=num_rows))


# Endpoint para leitura dos dados
@bp.route('/read', methods=['GET'])
def read_data():
    conn = sqlite3.connect('api/core/db/data.db')
    cursor = conn.cursor()

    selected_fields = request.args.getlist('fields')
    num_rows = int(request.args.get('num_rows', 10)) 

    tabela = 'configurations'  
    campos = ', '.join(selected_fields) if selected_fields else '*'

    consulta_sql = f'SELECT {campos} FROM {tabela} LIMIT {num_rows};'
    cursor.execute(consulta_sql)
    data = cursor.fetchall()
    cursor.close()
    conn.close()   

    return jsonify({'data': data})

