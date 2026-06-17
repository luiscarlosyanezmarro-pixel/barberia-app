import flet as ft

class InventoryScreen:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.dialog = None
        self.editing_id = None
        self.name_field = None
        self.description_field = None
        self.stock_field = None
        self.min_stock_field = None
        self.unit_field = None
        self.price_field = None
        self.supplier_field = None
    
    def build(self):
        self.name_field = ft.TextField(label="Nombre", width=300)
        self.description_field = ft.TextField(label="Descripción", multiline=True, width=300)
        
        self.stock_field = ft.TextField(
            label="Stock", 
            width=150, 
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$"),
            max_length=10
        )
        self.min_stock_field = ft.TextField(
            label="Stock Mínimo", 
            width=150, 
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$"),
            max_length=10,
            value="5"
        )
        self.unit_field = ft.TextField(label="Unidad", width=150, value="unidad")
        self.price_field = ft.TextField(
            label="Precio", 
            width=150, 
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$"),
            max_length=10
        )
        self.supplier_field = ft.TextField(label="Proveedor", width=300)
        
        self.materials_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("Stock Mínimo")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Proveedor")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=[],
            width=1000
        )
        
        add_button = ft.ElevatedButton(
            "Agregar Material",
            icon=ft.Icons.ADD_CIRCLE,
            on_click=self.open_add_dialog,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_GREY_700,
            )
        )
        
        main_column = ft.Column([
            ft.Row([ft.Text("Inventario", size=30, weight=ft.FontWeight.BOLD), add_button],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=20),
            ft.Container(
                content=self.materials_table,
                height=500
            )
        ], scroll=ft.ScrollMode.AUTO)
        
        content = ft.Container(
            content=main_column,
            padding=20,
            expand=True
        )
        
        self.refresh_table()
        return content
    
    def save_material(self, e):
        if not self.name_field.value:
            self.show_snack_bar("Por favor ingrese el nombre del material", ft.Colors.RED)
            return
        
        try:
            stock = int(self.stock_field.value) if self.stock_field.value else 0
            min_stock = int(self.min_stock_field.value) if self.min_stock_field.value else 5
            price = float(self.price_field.value) if self.price_field.value else 0
            
            if self.editing_id:
                self.db.execute_query("""
                    UPDATE materials 
                    SET name = %s, description = %s, stock = %s, min_stock = %s, 
                        unit = %s, price = %s, supplier = %s
                    WHERE id = %s
                """, (self.name_field.value, self.description_field.value, stock, min_stock,
                      self.unit_field.value, price, self.supplier_field.value, self.editing_id))
                self.show_snack_bar("Material actualizado exitosamente", ft.Colors.GREEN)
            else:
                self.db.execute_query("""
                    INSERT INTO materials (name, description, stock, min_stock, unit, price, supplier)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (self.name_field.value, self.description_field.value, stock, min_stock,
                      self.unit_field.value, price, self.supplier_field.value))
                self.show_snack_bar("Material agregado exitosamente", ft.Colors.GREEN)
            
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
        self.stock_field.value = ""
        self.min_stock_field.value = "5"
        self.unit_field.value = "unidad"
        self.price_field.value = ""
        self.supplier_field.value = ""
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
        self._show_dialog("Agregar Material")
    
    def open_edit_dialog(self, material_id):
        material = self.db.fetch_one("SELECT * FROM materials WHERE id = %s", (material_id,))
        
        if material:
            self.editing_id = material_id
            self.name_field.value = material[1] or ""
            self.description_field.value = material[2] or ""
            self.stock_field.value = str(material[3]) if material[3] else "0"
            self.min_stock_field.value = str(material[4]) if material[4] else "5"
            self.unit_field.value = material[5] or "unidad"
            self.price_field.value = str(material[6]) if material[6] else "0"
            self.supplier_field.value = material[7] or ""
            
            self._show_dialog("Editar Material")
        else:
            self.show_snack_bar(f"Error: Material ID {material_id} no encontrado", ft.Colors.RED)
    
    def _show_dialog(self, title):
        dialog_content = ft.Column([
            ft.Text(title, size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            self.name_field, 
            self.description_field, 
            self.stock_field, 
            self.min_stock_field,
            self.unit_field, 
            self.price_field, 
            self.supplier_field
        ], spacing=10, width=350, height=450, scroll=ft.ScrollMode.AUTO)
        
        def on_cancel(e):
            self.close_dialog()
        
        def on_save(e):
            self.save_material(e)
        
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
            materials = self.db.fetch_all("SELECT * FROM materials ORDER BY name")
            self.materials_table.rows = []
            
            if not materials or len(materials) == 0:
                self.materials_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("No hay materiales registrados")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text("")),
                    ])
                )
            else:
                for material in materials:
                    material_id = material[0]
                    
                    def delete_material(e, mid=material_id):
                        try:
                            self.db.execute_query("DELETE FROM materials WHERE id = %s", (mid,))
                            self.refresh_table()
                            self.show_snack_bar("Material eliminado exitosamente", ft.Colors.GREEN)
                        except Exception as ex:
                            self.show_snack_bar(f"Error al eliminar: {str(ex)}", ft.Colors.RED)
                    
                    def edit_material(e, mid=material_id):
                        self.open_edit_dialog(mid)
                    
                    try:
                        price = float(material[6]) if material[6] else 0
                        price_text = f"${price:,.2f}"
                    except (ValueError, TypeError):
                        price_text = "$0.00"
                    
                    actions_row = ft.Row([
                        ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE, 
                                    tooltip="Editar", on_click=edit_material, icon_size=20),
                        ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, 
                                    tooltip="Eliminar", on_click=delete_material, icon_size=20),
                    ], spacing=5)
                    
                    self.materials_table.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(str(material[0]))),
                            ft.DataCell(ft.Text(material[1] or "")),
                            ft.DataCell(ft.Text(f"{material[3]} {material[5] if material[5] else ''}")),
                            ft.DataCell(ft.Text(str(material[4]))),
                            ft.DataCell(ft.Text(price_text)),
                            ft.DataCell(ft.Text(material[7] or "")),
                            ft.DataCell(actions_row),
                        ])
                    )
            self.page.update()
        except Exception as e:
            print(f"Error al refrescar tabla: {e}")
            import traceback
            traceback.print_exc()