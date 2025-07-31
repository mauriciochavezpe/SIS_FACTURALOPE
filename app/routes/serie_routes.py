from flask_restx import Namespace, Resource, fields
from app.services.serie_services import get_all_series, create_serie, update_serie, delete_serie, get_last_number

serie_blueprint = Namespace('series', description='Serie operations')

serie_model = serie_blueprint.model('SerieModel', {
    'tipo_comprobante': fields.String(required=True, description='The document type'),
    'serie': fields.String(required=True, description='The serie'),
    'ultimo_correlativo': fields.Integer(description='The last correlative')
})

@serie_blueprint.route('/')
class SerieList(Resource):
    def get(self):
        series, status = get_all_series()
        return series, status

    @serie_blueprint.expect(serie_model)
    def post(self):
        serie, status = create_serie()
        return serie, status

@serie_blueprint.route('/<int:id>')
class Serie(Resource):
    @serie_blueprint.expect(serie_model)
    def put(self, id):
        serie, status = update_serie(id)
        return serie, status

    def delete(self, id):
        result, status = delete_serie(id)
        return result, status

@serie_blueprint.route('/last_number/<string:tipo_comprobante>/<string:serie>')
class SerieLastNumber(Resource):
    def get(self, tipo_comprobante, serie):
        result = get_last_number(tipo_comprobante, serie)
        return result, 200
