from app import db
import os
import pandas as pd
from app.models.entities.MasterData import MasterData
def cargarBatch():
    ruta_archivo = os.path.join('assets', 'data.xlsx')
    print("Iniciando carga batch...")

    if not os.path.exists(ruta_archivo):
        print(f"Archivo no encontrado:{ruta_archivo}")
        return False
    
    try:
        df = pd.read_excel(ruta_archivo)
        # Validamos si ya hay datos
        existe_data = db.session.query(MasterData).first() is not None
        if existe_data:
            print("La tabla MasterData ya contiene registros. Omitiendo carga inicial.")
            return False
        
        master_data_batch =[]
        
        for _, row in df.iterrows():
            master_data = MasterData(
                code_table=row['code_table'],
                description_table=row['description_table'],
                data_value=row['data_value'],
                description_value=row['description_value'],
                ip=row.get('ip',''),
                createdBy=row.get('createdBy',''),
                modifiedBy=row.get('modifiedBy',''),
                id_status=row.get('id_status', 23)
            )
            master_data_batch.append(master_data)
        
        # Inserción por lotes
        db.session.bulk_save_objects(master_data_batch)
        db.session.commit()
        
        print(f"Carga inicial de MasterData completada. {len(master_data_batch)} registros insertados.")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error en carga inicial de MasterData: {str(e)}")
        return False
        