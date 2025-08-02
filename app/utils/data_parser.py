def parse_customer_data(data: list) -> dict:
     """
     Convierte los datos del cliente de la respuesta del servicio de RUC
     a un diccionario compatible con el modelo Customer.
     """
     if not data or not isinstance(data, list) or not data[0]:
         return {}

     source = data[0]

     # Mapeo de los campos del servicio a los campos del modelo Customer
     customer_dict = {
         'business_name': source.get('apenomdenunciado'),
         'address': source.get('direstablecimiento'),
         'province': source.get('desprovincia'),
         'city': source.get('desdistrito'),
         'country': source.get('desdepartamento'),
         # El document_number (RUC) no viene en este payload,
         # se debe añadir desde la variable que ya se tiene en el servicio.
     }
     return customer_dict