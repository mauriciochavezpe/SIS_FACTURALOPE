from app import db
from app.models.entities.MasterData import MasterData
class CatalogManager:
    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CatalogManager, cls).__new__(cls)
        return cls._instance

    def _load_catalog(self, catalog_code):
        """Carga un catálogo completo desde la BD y lo guarda en caché."""
        try:
            print(f"--- Loading catalog: {catalog_code} from DB ---")
            entries = db.session.query(MasterData).filter_by(catalog_code=catalog_code).all()
            self._cache[catalog_code] = {entry.value: entry.id for entry in entries}
        except Exception as e:
            print(f"Error loading catalog {catalog_code}: {e}")
            self._cache[catalog_code] = {}

    def get_id(self, catalog_code, value):
        """Obtiene el ID para un valor específico de un catálogo."""
        if catalog_code not in self._cache:
            self._load_catalog(catalog_code)
        
        return self._cache.get(catalog_code, {}).get(value)

# Instancia única para ser usada en toda la aplicación
catalog_manager = CatalogManager()
