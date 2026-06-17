import flet as ft

class Sidebar(ft.Container):
    def __init__(self, page, on_navigate):
        super().__init__()
        self._page = page
        self.on_navigate = on_navigate
        
        self.content = ft.Column([
            ft.Container(height=20),
            ft.Text("Barbería App", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Divider(color=ft.Colors.GREY_700),
            ft.Container(height=10),
            self._create_nav_item("Dashboard", ft.Icons.DASHBOARD, "dashboard"),
            self._create_nav_item("Inventario", ft.Icons.INVENTORY, "inventory"),
            self._create_nav_item("Servicios", ft.Icons.CUT, "services"),
            self._create_nav_item("Ventas", ft.Icons.SHOPPING_CART, "sales"),
            self._create_nav_item("Compras", ft.Icons.SHOPPING_BAG, "purchases"),
            self._create_nav_item("Citas", ft.Icons.CALENDAR_MONTH, "appointments"),
            ft.Container(expand=True),
            ft.Divider(color=ft.Colors.GREY_700),
            self._create_nav_item("Cerrar Sesión", ft.Icons.EXIT_TO_APP, "logout"),
        ], spacing=5, expand=True)
        
        self.width = 260
        self.bgcolor = ft.Colors.BLUE_GREY_900
        self.padding = 15
    
    def _create_nav_item(self, title, icon, route):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=20, color=ft.Colors.WHITE),
                ft.Text(title, size=14, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500),
            ]),
            on_click=lambda e: self.on_navigate(route),
            padding=12,
            border_radius=8,
            ink=True,
            ink_color=ft.Colors.WHITE24,
        )