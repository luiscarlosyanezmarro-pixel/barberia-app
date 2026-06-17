import httpx
import os
from typing import Dict, Any, List, Optional

class APIClient:
    """Cliente para comunicarse con la API de Barbería"""
    
    def __init__(self, base_url: str = None):
        # URL de la API en Railway (producción)
        RAILWAY_API_URL = "https://web-production-65934.up.railway.app"
        LOCAL_API_URL = "http://127.0.0.1:8000"
        
        # En Railway, usar la variable de entorno API_URL
        # En local, usar LOCAL_API_URL
        if base_url is None:
            # Intentar obtener desde variable de entorno
            env_url = os.getenv('API_URL', '')
            if env_url:
                self.base_url = env_url
                print(f"API Client usando variable de entorno: {self.base_url}")
            else:
                # En producción (Railway), usar la URL de Railway
                # En desarrollo local, usar localhost
                # Por defecto usar Railway (producción)
                self.base_url = RAILWAY_API_URL
                print(f"API Client usando URL por defecto: {self.base_url}")
        else:
            self.base_url = base_url
        
        self.client = httpx.Client(timeout=30.0)
        print(f"API Client conectando a: {self.base_url}")
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            if method == "GET":
                response = self.client.get(url)
            elif method == "POST":
                response = self.client.post(url, json=data)
            elif method == "PUT":
                response = self.client.put(url, json=data)
            elif method == "DELETE":
                response = self.client.delete(url)
            else:
                raise ValueError(f"Método no soportado: {method}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise Exception("Credenciales incorrectas")
            else:
                raise Exception(f"Error {response.status_code}: {response.text}")
        except Exception as e:
            print(f"Error en API {method} {endpoint}: {e}")
            raise
    
    def login(self, username: str, password: str) -> Dict:
        return self._request("POST", "/api/login", {"username": username, "password": password})
    
    def get_materials(self) -> List[Dict]:
        return self._request("GET", "/api/materials")
    
    def get_material_by_id(self, material_id: int) -> Optional[Dict]:
        try:
            return self._request("GET", f"/api/materials/{material_id}")
        except:
            return None
    
    def create_material(self, material: Dict) -> Dict:
        return self._request("POST", "/api/materials", material)
    
    def update_material(self, material_id: int, material: Dict) -> Dict:
        return self._request("PUT", f"/api/materials/{material_id}", material)
    
    def delete_material(self, material_id: int) -> Dict:
        return self._request("DELETE", f"/api/materials/{material_id}")
    
    def get_services(self) -> List[Dict]:
        return self._request("GET", "/api/services")
    
    def get_service_by_id(self, service_id: int) -> Optional[Dict]:
        try:
            return self._request("GET", f"/api/services/{service_id}")
        except:
            return None
    
    def create_service(self, service: Dict) -> Dict:
        return self._request("POST", "/api/services", service)
    
    def update_service(self, service_id: int, service: Dict) -> Dict:
        return self._request("PUT", f"/api/services/{service_id}", service)
    
    def delete_service(self, service_id: int) -> Dict:
        return self._request("DELETE", f"/api/services/{service_id}")
    
    def get_sales(self) -> List[Dict]:
        return self._request("GET", "/api/sales")
    
    def get_sale_by_id(self, sale_id: int) -> Optional[Dict]:
        try:
            return self._request("GET", f"/api/sales/{sale_id}")
        except:
            return None
    
    def create_sale(self, sale: Dict) -> Dict:
        return self._request("POST", "/api/sales", sale)
    
    def update_sale(self, sale_id: int, sale: Dict) -> Dict:
        return self._request("PUT", f"/api/sales/{sale_id}", sale)
    
    def delete_sale(self, sale_id: int) -> Dict:
        return self._request("DELETE", f"/api/sales/{sale_id}")
    
    def get_purchases(self) -> List[Dict]:
        return self._request("GET", "/api/purchases")
    
    def get_purchase_by_id(self, purchase_id: int) -> Optional[Dict]:
        try:
            return self._request("GET", f"/api/purchases/{purchase_id}")
        except:
            return None
    
    def create_purchase(self, purchase: Dict) -> Dict:
        return self._request("POST", "/api/purchases", purchase)
    
    def update_purchase(self, purchase_id: int, purchase: Dict) -> Dict:
        return self._request("PUT", f"/api/purchases/{purchase_id}", purchase)
    
    def delete_purchase(self, purchase_id: int) -> Dict:
        return self._request("DELETE", f"/api/purchases/{purchase_id}")
    
    def get_appointments(self, filter_date: str = None) -> List[Dict]:
        if filter_date:
            return self._request("GET", f"/api/appointments?filter_date={filter_date}")
        return self._request("GET", "/api/appointments")
    
    def get_appointment_by_id(self, appointment_id: int) -> Optional[Dict]:
        try:
            return self._request("GET", f"/api/appointments/{appointment_id}")
        except:
            return None
    
    def create_appointment(self, appointment: Dict) -> Dict:
        return self._request("POST", "/api/appointments", appointment)
    
    def update_appointment(self, appointment_id: int, appointment: Dict) -> Dict:
        return self._request("PUT", f"/api/appointments/{appointment_id}", appointment)
    
    def delete_appointment(self, appointment_id: int) -> Dict:
        return self._request("DELETE", f"/api/appointments/{appointment_id}")
    
    def update_appointment_status(self, appointment_id: int, status: str) -> Dict:
        return self._request("PUT", f"/api/appointments/{appointment_id}/status", {"status": status})
    
    def get_dashboard_stats(self) -> Dict:
        return self._request("GET", "/api/dashboard/stats")
    
    def get_sales_by_date(self, date: str) -> float:
        try:
            result = self._request("GET", f"/api/sales/by-date?date={date}")
            return float(result.get("total", 0.0))
        except:
            return 0.0
    
    def get_recent_sales(self, limit: int = 5) -> List[Dict]:
        return self._request("GET", f"/api/dashboard/recent-sales?limit={limit}")
    
    def close(self):
        self.client.close()