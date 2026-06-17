import flet as ft
import os
from database import Database
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.inventory_screen import InventoryScreen
from screens.services_screen import ServicesScreen
from screens.sales_screen import SalesScreen
from screens.purchases_screen import PurchasesScreen
from screens.appointments_screen import AppointmentsScreen
from components.sidebar import Sidebar

class BarberiaApp:
    def __init__(self):
        self.db = Database()
        self.current_user = None
        self.current_screen = "dashboard"
        self.page = None
        self.main_container = None
        self.content_area = None
    
    def main(self, page: ft.Page):
        self.page = page
        page.title = "Barbería App"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window.width = 1280
        page.window.height = 800
        page.window.resizable = True
        page.window.min_width = 1024
        page.window.min_height = 600
        page.scroll = ft.ScrollMode.AUTO
        
        login_screen = LoginScreen(page, self.db, self.on_login_success)
        login_screen.build()
    
    def on_login_success(self, user):
        self.current_user = user
        self.page.clean()
        
        self.main_container = ft.Row(
            expand=True,
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START
        )
        
        self.sidebar = Sidebar(self.page, self.navigate_to)
        
        self.content_area = ft.Container(
            expand=True,
            padding=20,
            bgcolor=ft.Colors.GREY_50
        )
        
        self.main_container.controls = [self.sidebar, self.content_area]
        self.page.add(self.main_container)
        
        self.navigate_to("dashboard")
    
    def navigate_to(self, route):
        if route == "logout":
            self.current_user = None
            login_screen = LoginScreen(self.page, self.db, self.on_login_success)
            login_screen.build()
            return
        
        self.current_screen = route
        
        if route == "dashboard":
            screen = DashboardScreen(self.page, self.db)
        elif route == "inventory":
            screen = InventoryScreen(self.page, self.db)
        elif route == "services":
            screen = ServicesScreen(self.page, self.db)
        elif route == "sales":
            screen = SalesScreen(self.page, self.db)
        elif route == "purchases":
            screen = PurchasesScreen(self.page, self.db)
        elif route == "appointments":
            screen = AppointmentsScreen(self.page, self.db)
        else:
            return
        
        try:
            content = screen.build()
            self.content_area.content = content
            self.content_area.update()
        except Exception as e:
            print(f"Error al cargar pantalla {route}: {e}")
            import traceback
            traceback.print_exc()
            self.content_area.content = ft.Text(f"Error: {str(e)}", color=ft.Colors.RED)
            self.content_area.update()

if __name__ == "__main__":
    # Obtener el puerto desde variable de entorno (Railway asigna el puerto)
    port = int(os.getenv('PORT', 8080))
    print(f"Iniciando aplicación en el puerto: {port}")
    
    # En Railway, usamos el puerto asignado
    ft.app(target=BarberiaApp().main, port=port, view=ft.AppView.WEB_BROWSER)