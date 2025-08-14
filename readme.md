# Activities

*Los modelos son: Customers, Products, Categories, Invoices, InvoiceItems,Storage,User, masterData...*

### Activity: 25/04
- created crud for Product
- created crud for Category
- created crud for Invoice
- created crud for InvoiceItem
- created crud for Storage
- created crud for MasterData

## Con graphql
- create report sell daily
- create report sell monthly
- create report product with amount sales
- create report product with amount 


- python -m venv venv
- .venv\Scripts\activate
- pip install -r requirements.txt


### test
- pytest tests/ -v
- pytest tests/unit/services/test_product_service.py -v


- https://cpe.sunat.gob.pe/sites/default/files/inline-files/servicios%20web%20disponibles%20%281%29.pdf



| Código | Significado                         | Acción sugerida                 |
| ------ | ----------------------------------- | ------------------------------- |
| `0`    | **Aceptado**                        | OK – comprobante aceptado.      |
| `98`   | **Aceptado con observaciones**      | Revisión necesaria.             |
| `99`   | **Rechazado**                       | Debes corregir el comprobante.  |
| `9999` | **Error en el sistema de SUNAT**    | Reintentar o contactar a SUNAT. |
| `0011` | **RUC del emisor no está habido**   | Verifica estado del RUC.        |
| `0128` | **El comprobante ya fue informado** | Ya registrado, no reenviar.     |
| `0149` | **Serie y número ya informados**    | Duplicado, cambiar correlativo. |



Catalogos [https://www.sunat.gob.pe/legislacion/superin/2015/anexoI-274-2015.pdf]

## pendiente 1.1
- agregar dinamismo a los items y products 

## pendiente 1.2
- ver lo de NC y ND para mañana jueves y viernes
- hacer pruebas en prd con los usuarios y conexiones
- avanzar con el front
- hacer pruebas de estres



## APUNTES
 - HACEMOS MATCH : flask db stamp head
// MANUAL https://cpe.sunat.gob.pe/sites/default/files/inline-files/Manual-de-Consulta-Integrada-de-Comprobante-de-Pago-por-ServicioWEB_v2.pdf


## apuntes tech 
en dict se accede mediante la llave. eg. invoice['serie']
en obj que es para los modelos SQLAlchemy se accede mediante el atributo. eg. invoice.serie

| Acceso              | Si clave no existe   | Permite valor por defecto |
| ------------------- | -------------------- | ------------------------- |
| `dict["clave"]`     | ❌ Lanza `KeyError` | ❌ No                   |
| `dict.get("clave")` | ✅ Devuelve `None`  | ✅ Sí                   |
| `dict.clave`        | ✅ Devuelve `Valor` | ✅ Sí                   |
