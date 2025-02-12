import pandas as pd
import os
import glob
from tqdm import tqdm  # Importando a barra de progresso
import pyarrow.parquet as pq
import pyarrow as pa

# Caminho da pasta onde estão os arquivos CSV
pasta_socios = "arquivos_extraidos/ESTABELE"

# Usar glob para listar todos os arquivos CSV dentro da pasta
arquivos_csv = glob.glob(os.path.join(pasta_socios, "*.csv"))

# Lista para armazenar os DataFrames de cada arquivo
lista_dfs = []


chunk_size = 20000  # 20.000 linhas por vez

# Definir o nome do arquivo Parquet
output_parquet = "estabelecimentos_completo.parquet"

# Preparar o ParquetWriter para salvar os dados progressivamente
with tqdm(total=len(arquivos_csv), desc="Processando arquivos", unit="arquivo") as pbar:
    for arquivo in arquivos_csv:
        print(f"Lendo arquivo {arquivo}")
        
        # Processar o arquivo em chunks
        for chunk in pd.read_csv(arquivo, 
                                 sep=";", 
                                 encoding="latin1",  
                                 dtype=str, 
                                 quotechar='"', 
                                 header=None, 
                                 chunksize=chunk_size):
            
            # Atribuir os nomes das colunas manualmente
            chunk.columns = ['cnpj_basico',
                             'cnpj_ordem',
                             'cnpj_dv',
                             'identificador_matriz_filial',
                             'nome_fantasia',
                             'situacao_cadastral',
                             'data_situacao_cadastral',
                             'motivo_situacao_cadastral',
                             'nome_cidade_exterior',
                             'pais',
                             'data_inicio_atividade',
                             'cnae_fiscal_principal',
                             'cnae_fiscal_secundaria',
                             'tipo_logradouro',
                             'logradouro',
                             'numero',
                             'complemento',
                             'bairro',
                             'cep',
                             'uf',
                             'municipio',
                             'ddd_1',
                             'telefone_1',
                             'ddd_2',
                             'telefone_2',
                             'ddd_fax',
                             'fax',
                             'correio_eletronico',
                             'situacao_especial',
                             'data_situacao_especial']
            
            # Verificar se a coluna 'cnpj_basico' existe, e se não, criar com base no 'cnpj_ordem'
            if 'cnpj_basico' not in chunk.columns:
                chunk['cnpj_basico'] = chunk['cnpj_ordem'].str[:8]  # Criar a coluna com os 8 primeiros caracteres de 'cnpj_ordem'

            # Remover espaços extras das colunas
            chunk = chunk.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            
            # Reordenar o DataFrame (se necessário)
            chunk_reordenado = chunk[['cnpj_basico', 'cnpj_ordem', 'cnpj_dv', 'identificador_matriz_filial', 
                                      'nome_fantasia', 'situacao_cadastral', 'data_situacao_cadastral', 
                                      'motivo_situacao_cadastral', 'nome_cidade_exterior', 'pais', 
                                      'data_inicio_atividade', 'cnae_fiscal_principal', 
                                      'cnae_fiscal_secundaria', 'tipo_logradouro', 'logradouro', 
                                      'numero', 'complemento', 'bairro', 'cep', 'uf', 'municipio', 
                                      'ddd_1', 'telefone_1', 'ddd_2', 'telefone_2', 'ddd_fax', 'fax', 
                                      'correio_eletronico', 'situacao_especial', 'data_situacao_especial']]
            
            # Converter o DataFrame em um Table (para o formato Parquet)
            table = pa.Table.from_pandas(chunk_reordenado)
            
            # Usar ParquetWriter para salvar os dados progressivamente
            if not os.path.exists(output_parquet):  # Se o arquivo não existe, cria o arquivo
                pq.write_table(table, output_parquet, compression='SNAPPY')
            else:  # Caso contrário, abre o arquivo e anexa os dados
                with pq.ParquetWriter(output_parquet, table.schema, compression='SNAPPY') as writer:
                    writer.write_table(table)

        # Atualiza a barra de progresso após processar cada arquivo
        pbar.update(1)

print("Arquivo Parquet salvo com sucesso!")
