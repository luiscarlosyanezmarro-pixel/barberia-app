import hashlib
import os
from api_client import APIClient
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

class Database:
    """Fachada que usa la API en lugar de conexión directa a MySQL"""
    
    def __init__(self):
        # URL de la API en Railway (producción)
        RAILWAY_API_URL = "https://web-production-65934.up.railway.app"
        LOCAL_API_URL = "http://127.0.0.1:8000"
        
        # Intentar obtener desde variable de entorno
        env_url = os.getenv('API_URL', '')
        if env_url:
            api_url = env_url
            print(f"Database usando variable de entorno: {api_url}")
        else:
            # Por defecto usar Railway (producción)
            api_url = RAILWAY_API_URL
            print(f"Database usando URL por defecto: {api_url}")
        
        self.api = APIClient(base_url=api_url)
        self._current_user = None
        print(f"Base de datos conectada a través de API en: {api_url}")
    
    def connect(self):
        pass
    
    def create_tables(self):
        pass
    
    def create_default_user(self):
        pass
    
    def verify_user(self, username: str, password: str) -> Optional[tuple]:
        try:
            result = self.api.login(username, password)
            if result.get("success"):
                user = result.get("user")
                return (user["id"], user["username"], "", user["name"], user["role"])
            return None
        except Exception as e:
            print(f"Error en verify_user: {e}")
            return None
    
    def fetch_all(self, query: str, params: tuple = None) -> List[tuple]:
        query_lower = query.lower().strip()
        
        # MATERIALES
        if "from materials" in query_lower and "select" in query_lower:
            materials = self.api.get_materials()
            
            if "where id =" in query_lower and params:
                try:
                    material_id = int(params[0])
                except (ValueError, TypeError):
                    print(f"Error: No se pudo convertir {params[0]} a entero")
                    return []
                
                for m in materials:
                    if m["id"] == material_id:
                        if "name, price" in query_lower:
                            return [(m["name"], m["price"])]
                        return [(
                            m["id"], m["name"], m.get("description", ""),
                            m["stock"], m["min_stock"], m.get("unit", "unidad"),
                            m["price"], m.get("supplier", "")
                        )]
                return []
            
            if "id, name, price" in query_lower:
                return [(m["id"], m["name"], m["price"]) for m in materials]
            
            return [(
                m["id"], m["name"], m.get("description", ""),
                m["stock"], m["min_stock"], m.get("unit", "unidad"),
                m["price"], m.get("supplier", "")
            ) for m in materials]
        
        # SERVICIOS
        if "from services" in query_lower and "select" in query_lower:
            services = self.api.get_services()
            
            if "where id =" in query_lower and params:
                try:
                    service_id = int(params[0])
                except (ValueError, TypeError):
                    print(f"Error: No se pudo convertir {params[0]} a entero")
                    return []
                
                for s in services:
                    if s["id"] == service_id:
                        return [(s["id"], s["name"], s.get("description", ""),
                                 s["price"], s.get("duration", 30), s.get("active", 1))]
                return []
            
            if "id, name, price" in query_lower:
                return [(s["id"], s["name"], s["price"]) for s in services]
            
            return [(s["id"], s["name"], s.get("description", ""),
                     s["price"], s.get("duration", 30), s.get("active", 1)) for s in services]
        
        # VENTAS
        if "from sales" in query_lower and "select" in query_lower:
            if "where id =" in query_lower and params:
                try:
                    sale_id = int(params[0])
                except (ValueError, TypeError):
                    print(f"Error: No se pudo convertir {params[0]} a entero")
                    return []
                
                sale = self.api.get_sale_by_id(sale_id)
                if sale:
                    return [(
                        sale["id"], sale["service_id"], sale["client_name"],
                        sale.get("client_phone", ""), sale["price"],
                        sale.get("sale_date", ""), sale.get("payment_method", ""),
                        sale.get("barber_name", ""), sale.get("user_id", "")
                    )]
                return []
            
            sales = self.api.get_sales()
            return [(
                s["id"], s["service_id"], s["client_name"],
                s.get("client_phone", ""), s["price"],
                s.get("sale_date", ""), s.get("payment_method", ""),
                s.get("barber_name", ""), s.get("user_id", "")
            ) for s in sales]
        
        # ============================================================
        # COMPRAS - CORREGIDO
        # ============================================================
        if "from purchases" in query_lower and "select" in query_lower:
            # Detectar si es una consulta para una compra específica (fetch_one)
            if "where id =" in query_lower and params:
                try:
                    purchase_id = int(params[0])
                except (ValueError, TypeError):
                    print(f"Error: No se pudo convertir {params[0]} a entero")
                    return []
                
                print(f"DEBUG DB: Buscando compra por ID: {purchase_id}")
                purchase = self.api.get_purchase_by_id(purchase_id)
                if purchase:
                    print(f"DEBUG DB: Compra encontrada")
                    # Devolver los datos en el orden CORRECTO para SELECT *
                    # Estructura de la tabla purchases:
                    # id, material_id, quantity, total_price, purchase_date, supplier, user_id
                    return [(
                        purchase.get("id", 0),          # 0: id
                        purchase.get("material_id", 0),  # 1: material_id
                        purchase.get("quantity", 0),     # 2: quantity
                        purchase.get("total_price", 0),  # 3: total_price
                        purchase.get("purchase_date", ""), # 4: purchase_date
                        purchase.get("supplier", ""),    # 5: supplier
                        purchase.get("user_id", 0)       # 6: user_id
                    )]
                print(f"DEBUG DB: Compra ID {purchase_id} NO encontrada")
                return []
            
            # Consulta para todas las compras (con JOIN para mostrar)
            purchases = self.api.get_purchases()
            result = []
            for p in purchases:
                result.append((
                    p.get("id", 0),
                    p.get("material_name", "N/A"),
                    p.get("material_price", 0),
                    p.get("quantity", 0),
                    p.get("total_price", 0),
                    p.get("supplier", ""),
                    p.get("purchase_date", "")
                ))
            return result
        
        # CITAS
        if "from appointments" in query_lower and "select" in query_lower:
            if "where id =" in query_lower and params:
                try:
                    appointment_id = int(params[0])
                except (ValueError, TypeError):
                    print(f"Error: No se pudo convertir {params[0]} a entero")
                    return []
                
                appointment = self.api.get_appointment_by_id(appointment_id)
                if appointment:
                    return [(
                        appointment["id"], 
                        appointment["client_name"], 
                        appointment.get("client_phone", ""),
                        appointment.get("service_id", 0),
                        appointment.get("appointment_date", ""),
                        appointment.get("appointment_time", ""),
                        appointment.get("barber_name", ""),
                        appointment.get("status", "pendiente")
                    )]
                return []
            
            if "appointment_date = %s" in query_lower and params:
                appointments = self.api.get_appointments(filter_date=params[0])
            else:
                appointments = self.api.get_appointments()
            
            return [(
                a["id"], a["client_name"], a.get("client_phone", ""),
                a.get("service_id", 0), a.get("appointment_date", ""),
                a.get("appointment_time", ""), a.get("barber_name", ""),
                a.get("status", "pendiente")
            ) for a in appointments]
        
        # DASHBOARD
        if "count(*) from services" in query_lower and "where active = 1" in query_lower:
            stats = self.api.get_dashboard_stats()
            return [(stats.get("total_services", 0),)]
        
        if "coalesce(sum(price), 0) from sales" in query_lower and "date(sale_date) = %s" in query_lower and params:
            target_date = params[0]
            total = self.api.get_sales_by_date(target_date)
            print(f"DEBUG: Ventas del día {target_date}: ${total}")
            return [(total,)]
        
        if "coalesce(sum(price), 0) from sales" in query_lower and "curdate()" in query_lower:
            stats = self.api.get_dashboard_stats()
            return [(float(stats.get("sales_today", 0.0)),)]
        
        if "count(*) from appointments" in query_lower and "date(appointment_date) = %s" in query_lower and params:
            target_date = params[0]
            appointments = self.api.get_appointments(filter_date=target_date)
            return [(len(appointments),)]
        
        if "count(*) from appointments" in query_lower and "curdate()" in query_lower:
            stats = self.api.get_dashboard_stats()
            return [(stats.get("appointments_today", 0),)]
        
        if "stock <= min_stock" in query_lower:
            stats = self.api.get_dashboard_stats()
            return [(stats.get("low_stock", 0),)]
        
        if "s.client_name, ser.name, s.price, s.sale_date" in query_lower:
            recent_sales = self.api.get_recent_sales(limit=5)
            return [(s["client_name"], s["service_name"], s["price"], s["sale_date"]) for s in recent_sales]
        
        print(f"Consulta no mapeada: {query}")
        return []
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[tuple]:
        results = self.fetch_all(query, params)
        if results and len(results) > 0:
            return results[0]
        return None
    
    def execute_query(self, query: str, params: tuple = None) -> Any:
        query_lower = query.lower().strip()
        
        # MATERIALES
        if "insert into materials" in query_lower:
            material = {
                "name": params[0],
                "description": params[1],
                "stock": params[2],
                "min_stock": params[3],
                "unit": params[4],
                "price": params[5],
                "supplier": params[6]
            }
            return self.api.create_material(material)
        
        if "update materials" in query_lower and "where id = %s" in query_lower and "set name" in query_lower:
            material_id = params[-1]
            material = {
                "name": params[0],
                "description": params[1],
                "stock": params[2],
                "min_stock": params[3],
                "unit": params[4],
                "price": params[5],
                "supplier": params[6]
            }
            return self.api.update_material(material_id, material)
        
        if "delete from materials" in query_lower:
            return self.api.delete_material(params[0])
        
        if "update materials set stock = stock" in query_lower:
            return {"message": "Stock actualizado en la compra"}
        
        # SERVICIOS
        if "insert into services" in query_lower:
            service = {
                "name": params[0],
                "description": params[1],
                "price": params[2],
                "duration": params[3]
            }
            return self.api.create_service(service)
        
        if "update services" in query_lower and "where id = %s" in query_lower:
            service_id = params[-1]
            service = {
                "name": params[0],
                "description": params[1],
                "price": params[2],
                "duration": params[3]
            }
            return self.api.update_service(service_id, service)
        
        if "update services set active = 0" in query_lower:
            return self.api.delete_service(params[0])
        
        # VENTAS
        if "insert into sales" in query_lower:
            sale = {
                "service_id": params[0],
                "client_name": params[1],
                "client_phone": params[2],
                "price": params[3],
                "payment_method": params[4],
                "barber_name": params[5]
            }
            return self.api.create_sale(sale)
        
        if "update sales" in query_lower and "where id = %s" in query_lower:
            sale_id = params[-1]
            sale = {
                "service_id": params[0],
                "client_name": params[1],
                "client_phone": params[2],
                "price": params[3],
                "payment_method": params[4],
                "barber_name": params[5]
            }
            return self.api.update_sale(sale_id, sale)
        
        if "delete from sales" in query_lower:
            return self.api.delete_sale(params[0])
        
        # COMPRAS
        if "insert into purchases" in query_lower:
            purchase = {
                "material_id": params[0],
                "quantity": params[1],
                "total_price": params[2],
                "supplier": params[3]
            }
            result = self.api.create_purchase(purchase)
            print(f"Compra registrada, resultado: {result}")
            return result
        
        if "update purchases" in query_lower and "where id = %s" in query_lower:
            purchase_id = params[-1]
            purchase = {
                "material_id": params[0],
                "quantity": params[1],
                "total_price": params[2],
                "supplier": params[3]
            }
            return self.api.update_purchase(purchase_id, purchase)
        
        if "delete from purchases" in query_lower:
            return self.api.delete_purchase(params[0])
        
        # CITAS
        if "insert into appointments" in query_lower:
            appointment = {
                "client_name": params[0],
                "client_phone": params[1],
                "service_id": params[2],
                "appointment_date": params[3],
                "appointment_time": params[4],
                "barber_name": params[5],
                "status": params[6] if len(params) > 6 else "pendiente"
            }
            return self.api.create_appointment(appointment)
        
        if "update appointments" in query_lower and "where id = %s" in query_lower:
            appointment_id = params[-1]
            appointment = {
                "client_name": params[0],
                "client_phone": params[1],
                "service_id": params[2],
                "appointment_date": params[3],
                "appointment_time": params[4],
                "barber_name": params[5],
                "status": params[6]
            }
            return self.api.update_appointment(appointment_id, appointment)
        
        if "delete from appointments" in query_lower:
            return self.api.delete_appointment(params[0])
        
        if "update appointments set status" in query_lower:
            status = params[0]
            appointment_id = params[1]
            return self.api.update_appointment_status(appointment_id, status)
        
        print(f"Query no implementada: {query}")
        return None
    
    def close(self):
        if hasattr(self, 'api'):
            self.api.close()