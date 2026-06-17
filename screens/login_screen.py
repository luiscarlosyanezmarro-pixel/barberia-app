import flet as ft
import hashlib

class LoginScreen:
    def __init__(self, page, db, on_login_success):
        self.page = page
        self.db = db
        self.on_login_success = on_login_success
    
    def build(self):
        self.page.title = "Login - Barbería App"
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.bgcolor = ft.Colors.BLUE_GREY_50
        
        title = ft.Text("Barbería App", size=42, weight=ft.FontWeight.BOLD, 
                       color=ft.Colors.BLUE_GREY_800)
        subtitle = ft.Text("Sistema de Administración", size=18, 
                          color=ft.Colors.BLUE_GREY_600)
        
        username_field = ft.TextField(
            label="Usuario",
            width=350,
            prefix_icon=ft.Icons.PERSON,
            border_radius=10,
            bgcolor=ft.Colors.WHITE
        )
        
        password_field = ft.TextField(
            label="Contraseña",
            width=350,
            password=True,
            can_reveal_password=True,
            prefix_icon=ft.Icons.LOCK,
            border_radius=10,
            bgcolor=ft.Colors.WHITE
        )
        
        error_text = ft.Text("", color=ft.Colors.RED, size=14)
        info_text = ft.Text("", color=ft.Colors.BLUE, size=12)
        info_text.value = "Credenciales de prueba: admin / admin123"
        
        def login_click(e):
            username = username_field.value
            password = password_field.value
            
            if not username or not password:
                error_text.value = "Por favor ingrese usuario y contraseña"
                self.page.update()
                return
            
            user = self.db.verify_user(username, password)
            
            if user:
                error_text.value = ""
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Bienvenido {user[3]}!"),
                    bgcolor=ft.Colors.GREEN
                )
                self.page.snack_bar.open = True
                self.page.update()
                self.on_login_success(user)
            else:
                error_text.value = "Usuario o contraseña incorrectos"
                self.page.update()
        
        def reset_default_user(e):
            try:
                self.db.execute_query("DELETE FROM users WHERE username = 'admin'")
                self.db.create_default_user()
                info_text.value = "Usuario admin restablecido. Use: admin / admin123"
                info_text.color = ft.Colors.GREEN
                username_field.value = "admin"
                password_field.value = "admin123"
                self.page.update()
            except Exception as ex:
                error_text.value = f"Error al resetear: {str(ex)}"
                self.page.update()
        
        login_button = ft.ElevatedButton(
            "Iniciar Sesión",
            on_click=login_click,
            width=350,
            height=45,
            icon=ft.Icons.LOGIN,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_GREY_700,
                shape=ft.RoundedRectangleBorder(radius=10),
            )
        )
        
        reset_button = ft.TextButton(
            "Restablecer usuario admin",
            on_click=reset_default_user,
            style=ft.ButtonStyle(color=ft.Colors.BLUE_GREY_600)
        )
        
        login_card = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.CUT, size=80, color=ft.Colors.BLUE_GREY_700),
                title,
                subtitle,
                ft.Container(height=30),
                username_field,
                password_field,
                login_button,
                error_text,
                info_text,
                reset_button,
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15),
            width=450,
            padding=40,
            bgcolor=ft.Colors.WHITE,
            border_radius=20,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.GREY_300
            )
        )
        
        self.page.controls.clear()
        self.page.add(
            ft.Container(
                content=login_card,
                alignment=ft.Alignment.CENTER,
                expand=True
            )
        )