import pandas as pd
from sqlalchemy import create_engine
import logging

class DatabaseLoader:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.engine = None
        if self.config.get('features', {}).get('enable_db_load', False):
             db_config = self.config.get('database', {})
             conn_str = db_config.get('connection_string')
             if conn_str:
                 self.engine = create_engine(conn_str)

    def load_data(self, df: pd.DataFrame, table_name: str):
        if not self.config.get('features', {}).get('enable_db_load', False):
            self.logger.info("Database loading is disabled via feature flag.")
            return

        if self.engine is None:
            self.logger.error("Database engine not initialized. Check connection string.")
            return

        self.logger.info(f"Loading {len(df)} records into table {table_name}...")
        try:
            # Check if using Oracle to apply optimizations
            if self.engine.dialect.name == 'oracle':
                self.logger.info("Using Oracle optimized loading (fast_executemany).")
                df.to_sql(
                    table_name, 
                    self.engine, 
                    if_exists='append', 
                    index=False,
                    method=self._oracle_bulk_insert
                )
            else:
                df.to_sql(table_name, self.engine, if_exists='append', index=False)
            
            self.logger.info("Data loaded successfully.")
        except Exception as e:
            self.logger.error(f"Failed to load data to database: {e}")
            raise

    def _oracle_bulk_insert(self, table, conn, keys, data_iter):
        import oracledb
        dbapi_conn = conn.connection
        cursor = dbapi_conn.cursor()
        
        sql = f"INSERT INTO {table.name} ({', '.join(keys)}) VALUES ({', '.join([':' + str(i+1) for i in range(len(keys))])})"
        
        # Enable fast_executemany for performance
        if hasattr(cursor, 'fast_executemany'):
             cursor.fast_executemany = True
        
        data = list(data_iter)
        cursor.executemany(sql, data)
        cursor.close()
