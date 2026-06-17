import flet as ft

class ServicesScreen:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.dialog = None
        self.editing_id = None
        self.name_field = None
        self.description_field = None
        self.price_field = None
        self.duration_field = None
    
    def build(self):
        self.name_field = ft.TextField(label="Nombre del Servicio", width=300)
        self.description_field = ft.TextField(label="Descripción", multiline=True, width=300)
        
        self.price_field = ft.TextField(
            label="Precio", 
            width=150, 
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$"),
            max_length=10
        )
        self.duration_field = ft.TextField(
            label="Duración (minutos)", 
            width=150, 
            value="30",
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$"),
            max_length=3
        )
        
        self.services_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Duración")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
            width=900
        )
        
        add_button = ft.ElevatedButton(
            "Agregar Servicio", 
            icon=ft.Icons.ADD_CIRCLE,
            on_click=self.open_add_dialog,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_GREY_700,
            )
        )
        
        main_column = ft.Column([
            ft.Row([ft.Text("Servicios de Barbería", size=30, weight=ft.FontWeight.BOLD), add_button],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=20),
            ft.Container(
                content=self.services_table,
                height=400
            )
        ], scroll=ft.ScrollMode.AUTO)
        
        content = ft.Container(
            content=main_column,
            padding=20,
            expand=True
        )
        
        self.refresh_table()
        return content
    
    def save_service(self, e):
        if not self.name_field.value:
            self.show_snack_bar("Por favor ingrese el nombre del servicio", ft.Colors.RED)
            return
        
        if not self.price_field.value:
            self.show_snack_bar("Por favor ingrese el precio", ft.Colors.RED)
            return
        
        try:
            price = float(self.price_field.value)
            duration = int(self.duration_field.value) if self.duration_field.value else 30
            
            if self.editing_id:
                self.db.execute_query("""
                    UPDATE services 
                    SET name = %s, description = %s, price = %s, duration = %s
                    WHERE id = %s
                """, (self.name_field.value, self.description_field.value, price, duration, self.editing_id))
                self.show_snack_bar("Servicio actualizado exitosamente", ft.Colors.GREEN)
            else:
                self.db.execute_query("""
                    INSERT INTO services (name, description, price, duration, active)
                    VALUES (%s, %s, %s, %s, 1)
                """, (self.name_field.value, self.description_field.value, price, duration))
                self.show_snack_bar("Servicio agregado exitosamente", ft.Colors.GREEN)
            
            self.close_dialog()
            self.clear_fields()
            self.refresh_table()
            
        except Exception as ex:
            print(f"Error al guardar: {ex}")
            import traceback
            traceback.print_exc()
            self.show_snack_bar(f"Error: {str(ex)}", ft.Colors.RED)
    
    def clear_fields(self):
        self.name_field.value = ""
        self.description_field.value = ""
        self.price_field.value = ""
        self.duration_field.value = "30"
        self.editing_id = None
    
    def show_snack_bar(self, message, color):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
            duration=3000
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def close_dialog(self, e=None):
        if self.dialog:
            self.dialog.open = False
            self.page.update()
            
            def remove_dialog():
                import time
                time.sleep(0.1)
                if self.dialog in self.page.overlay:
                    self.page.overlay.remove(self.dialog)
                self.page.update()
            
            import threading
            threading.Thread(target=remove_dialog, daemon=True).start()
            
            self.dialog = None
            self.clear_fields()
    
    def open_add_dialog(self, e):
        self.clear_fields()
        self._show_dialog("Agregar Servicio")
    
    def open_edit_dialog(self, service_id):
        service = self.db.fetch_one("SELECT * FROM services WHERE id = %s", (service_id,))
        
        if service:
            self.editing_id = service_id
            self.name_field.value = service[1] or ""
            self.description_field.value = service[2] or ""
            self.price_field.value = str(service[3]) if service[3] else "0"
            self.duration_field.value = str(service[4]) if service[4] else "30"
            
            self._show_dialog("Editar Servicio")
        else:
            self.show_snack_bar("Error: Servicio no encontrado", ft.Colors.RED)
    
    def _show_dialog(self, title):
        dialog_content = ft.Column([
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            self.name_field,
            self.description_field,
            self.price_field,
            self.duration_field
        ], spacing=10, width=350, height=350, scroll=ft.ScrollMode.AUTO)
        
        def on_cancel(e):
            self.close_dialog()
        
        def on_save(e):
            self.save_service(e)
        
        self.dialog = ft.AlertDialog(
            content=dialog_content,
            actions=[
                ft.TextButton("Cancelar", on_click=on_cancel),
                ft.ElevatedButton("Guardar", on_click=on_save, 
                                bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            on_dismiss=lambda e: self.close_dialog(),
        )
        
        self.page.overlay.append(self.dialog)
        self.page.update()
        self.dialog.open = True
        self.page.update()
    
    def refresh_table(self):
        try:
            services = self.db.fetch_all("SELECT * FROM services WHERE active = 1 ORDER BY name")
            self.services_table.rows = []
            
            if not services or len(services) == 0:
                self.services_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("No hay servicios registrados")),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("-")),
                    ])
                )
            else:
                for service in services:
                    service_id = service[0]
                    
                    def delete_service(e, sid=service_id):
                        try:
                            self.db.execute_query("UPDATE services SET active = 0 WHERE id = %s", (sid,))
                            self.refresh_table()
                            self.show_snack_bar("Servicio eliminado exitosamente", ft.Colors.GREEN)
                        except Exception as ex:
                            self.show_snack_bar(f"Error al eliminar: {str(ex)}", ft.Colors.RED)
                    
                    def edit_service(e, sid=service_id):
                        self.open_edit_dialog(sid)
                    
                    try:
                        price = float(service[3]) if service[3] else 0
                        price_text = f"${price:,.2f}"
                    except (ValueError, TypeError):
                        price_text = "$0.00"
                    
                    actions_row = ft.Row([
                        ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE, 
                                    tooltip="Editar", on_click=edit_service, icon_size=20),
                        ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, 
                                    tooltip="Eliminar", on_click=delete_service, icon_size=20),
                    ], spacing=5)
                    
                    self.services_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(service[0]))),
                            ft.DataCell(ft.Text(service[1] or "")),
                            ft.DataCell(ft.Text(service[2] or "")),
                            ft.DataCell(ft.Text(price_text)),
                            ft.DataCell(ft.Text(f"{service[4]} min")),
                            ft.DataCell(actions_row),
                        ])
                    )
            self.page.update()
        except Exception as e:
            print(f"Error al refrescar servicios: {e}")
            import traceback
            traceback.print_exc()