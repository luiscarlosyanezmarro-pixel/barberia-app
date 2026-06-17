import flet as ft
from datetime import datetime

class PurchasesScreen:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.dialog = None
        self.editing_id = None
        self.edit_material_dropdown = None
        self.edit_quantity_field = None
        self.edit_supplier_field = None
        self.edit_total_price = None
        self.materials = None
    
    def build(self):
        self.materials = self.db.fetch_all("SELECT id, name, price FROM materials")
        
        material_options = []
        for m in self.materials:
            material_id = m[0]
            material_name = m[1] if m[1] else "Sin nombre"
            try:
                price = float(m[2]) if m[2] else 0
                material_options.append(ft.dropdown.Option(key=str(material_id), text=f"{material_name} - ${price:,.2f}"))
            except (ValueError, TypeError):
                material_options.append(ft.dropdown.Option(key=str(material_id), text=f"{material_name} - Precio no definido"))
        
        material_dropdown = ft.Dropdown(label="Material", options=material_options, width=300)
        quantity_field = ft.TextField(label="Cantidad", width=150, input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$"), max_length=5)
        supplier_field = ft.TextField(label="Proveedor", width=250)
        
        def register_purchase(e):
            if material_dropdown.value and quantity_field.value:
                try:
                    selected_material = next(m for m in self.materials if str(m[0]) == material_dropdown.value)
                    quantity = int(quantity_field.value)
                    price = float(selected_material[2]) if selected_material[2] else 0
                    total_price = price * quantity
                    
                    print(f"Registrando compra - Material ID: {selected_material[0]}, Cantidad: {quantity}, Total: {total_price}, Proveedor: {supplier_field.value}")
                    
                    self.db.execute_query("""INSERT INTO purchases (material_id, quantity, total_price, supplier) VALUES (%s, %s, %s, %s)""", 
                                         (selected_material[0], quantity, total_price, supplier_field.value))
                    
                    material_dropdown.value = None
                    quantity_field.value = ""
                    supplier_field.value = ""
                    self.refresh_table()
                    self.page.update()
                    self.show_snack_bar("Compra registrada exitosamente", ft.Colors.GREEN)
                except Exception as ex:
                    print(f"Error al registrar compra: {ex}")
                    import traceback
                    traceback.print_exc()
                    self.show_snack_bar(f"Error: {str(ex)}", ft.Colors.RED)
        
        register_button = ft.ElevatedButton("Registrar Compra", icon=ft.Icons.SHOPPING_CART, on_click=register_purchase,
                                            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_700))
        
        self.purchases_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Material")), ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Precio Unitario")), ft.DataColumn(ft.Text("Total")), ft.DataColumn(ft.Text("Proveedor")),
                ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Acciones")),
            ], rows=[], width=1400
        )
        
        main_column = ft.Column([
            ft.Text("Registrar Compra de Materiales", size=30, weight=ft.FontWeight.BOLD), ft.Container(height=20),
            ft.Card(content=ft.Container(content=ft.Column([
                ft.Text("Nueva Compra", size=18, weight=ft.FontWeight.BOLD), ft.Container(height=10),
                ft.Row([material_dropdown, quantity_field, supplier_field, register_button], wrap=True, spacing=10),
            ], spacing=10), padding=20), elevation=3),
            ft.Container(height=30), ft.Text("Historial de Compras", size=20, weight=ft.FontWeight.BOLD), ft.Container(height=10),
            ft.Container(content=self.purchases_table, height=400)
        ], scroll=ft.ScrollMode.AUTO)
        
        content = ft.Container(content=main_column, padding=20, expand=True)
        self.refresh_table()
        return content
    
    def show_snack_bar(self, message, color):
        self.page.snack_bar = ft.SnackBar(content=ft.Text(message), bgcolor=color, duration=3000)
        self.page.snack_bar.open = True
        self.page.update()
    
    def close_dialog(self, e=None):
        if self.dialog:
            self.dialog.open = False
            self.page.update()
            import time, threading
            def remove_dialog():
                time.sleep(0.1)
                if self.dialog in self.page.overlay:
                    self.page.overlay.remove(self.dialog)
                self.page.update()
            threading.Thread(target=remove_dialog, daemon=True).start()
            self.dialog = None
            self.editing_id = None
    
    def open_edit_dialog(self, purchase_id):
        print(f"Editando compra ID: {purchase_id}")
        
        purchase = self.db.fetch_one("SELECT * FROM purchases WHERE id = %s", (purchase_id,))
        
        print(f"Resultado de la consulta (raw): {purchase}")
        
        if purchase:
            self.editing_id = purchase_id
            
            # Estructura: purchase[0]=id, purchase[1]=material_id, purchase[2]=quantity
            # purchase[3]=total_price, purchase[4]=purchase_date, purchase[5]=supplier, purchase[6]=user_id
            
            material_id = purchase[1]
            current_quantity = purchase[2]
            current_total_price = purchase[3]
            current_supplier = purchase[5] if purchase[5] else ""
            
            print(f"Datos extraídos - Material ID: {material_id}, Cantidad: {current_quantity}, Total: {current_total_price}, Proveedor: {current_supplier}")
            
            material_info = self.db.fetch_one("SELECT name, price FROM materials WHERE id = %s", (material_id,))
            
            if material_info:
                material_name = material_info[0]
                unit_price = float(material_info[1]) if material_info[1] else 0
                print(f"Material encontrado: {material_name}, Precio unitario: {unit_price}")
            else:
                material_name = "Desconocido"
                unit_price = 0
            
            try:
                total_price_float = float(current_total_price) if current_total_price else 0
            except (ValueError, TypeError):
                print(f"Error al convertir precio total: {current_total_price}")
                total_price_float = 0
            
            material_options = []
            for m in self.materials:
                mid = m[0]
                mname = m[1] if m[1] else "Sin nombre"
                try:
                    mprice = float(m[2]) if m[2] else 0
                    material_options.append(ft.dropdown.Option(key=str(mid), text=f"{mname} - ${mprice:,.2f}"))
                except:
                    material_options.append(ft.dropdown.Option(key=str(mid), text=f"{mname} - Precio no definido"))
            
            self.edit_material_dropdown = ft.Dropdown(label="Material", options=material_options, value=str(material_id), width=300)
            self.edit_quantity_field = ft.TextField(label="Cantidad", value=str(current_quantity) if current_quantity else "0", width=150,
                                                    input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$"), max_length=5)
            self.edit_supplier_field = ft.TextField(label="Proveedor", value=current_supplier, width=250)
            self.edit_total_price = ft.TextField(label="Precio Total", value=f"${total_price_float:,.2f}", width=150, read_only=True)
            self._show_edit_dialog(unit_price)
        else:
            self.show_snack_bar(f"Error: Compra ID {purchase_id} no encontrada", ft.Colors.RED)
    
    def _show_edit_dialog(self, unit_price):
        price_info = ft.Text(f"Precio Unitario: ${unit_price:,.2f}", size=14, color=ft.Colors.BLUE_GREY_700, weight=ft.FontWeight.BOLD)
        
        def update_total(e):
            try:
                quantity = int(self.edit_quantity_field.value) if self.edit_quantity_field.value else 0
                self.edit_total_price.value = f"${quantity * unit_price:,.2f}"
                self.page.update()
            except: 
                pass
        
        self.edit_quantity_field.on_change = update_total
        
        dialog_content = ft.Column([
            ft.Text("Editar Compra", size=20, weight=ft.FontWeight.BOLD), 
            ft.Container(height=10),
            self.edit_material_dropdown, 
            self.edit_quantity_field, 
            price_info, 
            self.edit_total_price, 
            self.edit_supplier_field,
        ], spacing=10, width=400, height=400, scroll=ft.ScrollMode.AUTO)
        
        def on_cancel(e): 
            self.close_dialog()
        
        def on_save(e): 
            self.update_purchase(unit_price)
        
        self.dialog = ft.AlertDialog(
            content=dialog_content, 
            actions=[
                ft.TextButton("Cancelar", on_click=on_cancel),
                ft.ElevatedButton("Guardar", on_click=on_save, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
            ], 
            actions_alignment=ft.MainAxisAlignment.END, 
            on_dismiss=lambda e: self.close_dialog()
        )
        
        self.page.overlay.append(self.dialog)
        self.page.update()
        self.dialog.open = True
        self.page.update()
    
    def update_purchase(self, old_unit_price):
        if not self.edit_material_dropdown.value or not self.edit_quantity_field.value:
            self.show_snack_bar("Complete los campos", ft.Colors.RED)
            return
        try:
            new_material_id = int(self.edit_material_dropdown.value)
            new_quantity = int(self.edit_quantity_field.value)
            new_total_price = new_quantity * old_unit_price
            
            old_purchase = self.db.fetch_one("SELECT material_id, quantity FROM purchases WHERE id = %s", (self.editing_id,))
            if old_purchase:
                old_material_id, old_quantity = old_purchase
                
                if old_material_id != new_material_id:
                    self.db.execute_query("UPDATE materials SET stock = stock - %s WHERE id = %s", (old_quantity, old_material_id))
                    self.db.execute_query("UPDATE materials SET stock = stock + %s WHERE id = %s", (new_quantity, new_material_id))
                else:
                    diff = new_quantity - old_quantity
                    if diff != 0:
                        self.db.execute_query("UPDATE materials SET stock = stock + %s WHERE id = %s", (diff, new_material_id))
                
                self.db.execute_query("""UPDATE purchases SET material_id = %s, quantity = %s, total_price = %s, supplier = %s WHERE id = %s""",
                                     (new_material_id, new_quantity, new_total_price, self.edit_supplier_field.value, self.editing_id))
                self.close_dialog()
                self.refresh_table()
                self.show_snack_bar("Compra actualizada exitosamente", ft.Colors.GREEN)
            else:
                self.show_snack_bar("Error: Compra original no encontrada", ft.Colors.RED)
        except Exception as ex:
            print(f"Error al actualizar: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", ft.Colors.RED)
    
    def delete_purchase(self, purchase_id):
        try:
            purchase = self.db.fetch_one("SELECT material_id, quantity FROM purchases WHERE id = %s", (purchase_id,))
            if purchase:
                material_id, quantity = purchase
                self.db.execute_query("UPDATE materials SET stock = stock - %s WHERE id = %s", (quantity, material_id))
                self.db.execute_query("DELETE FROM purchases WHERE id = %s", (purchase_id,))
                self.refresh_table()
                self.show_snack_bar("Compra eliminada exitosamente", ft.Colors.GREEN)
        except Exception as ex:
            print(f"Error al eliminar: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", ft.Colors.RED)
    
    def refresh_table(self):
        try:
            purchases = self.db.fetch_all("""
                SELECT p.id, m.name, m.price, p.quantity, p.total_price, p.supplier, p.purchase_date
                FROM purchases p 
                JOIN materials m ON p.material_id = m.id 
                ORDER BY p.purchase_date DESC 
                LIMIT 50
            """)
            
            self.purchases_table.rows = []
            
            if not purchases or len(purchases) == 0:
                self.purchases_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("-")) for _ in range(8)]))
            else:
                for p in purchases:
                    if len(p) < 7:
                        print(f"Error: Tupla con {len(p)} elementos: {p}")
                        continue
                    
                    pid = p[0]
                    mat_name = p[1] if p[1] else "N/A"
                    mat_price = p[2] if p[2] else 0
                    qty = p[3] if p[3] else 0
                    total = p[4] if p[4] else 0
                    supplier = p[5] if p[5] else "N/A"
                    date_str = p[6] if p[6] else ""
                    
                    try:
                        unit_price_text = f"${float(mat_price):,.2f}"
                    except (ValueError, TypeError):
                        unit_price_text = "$0.00"
                    
                    try:
                        total_text = f"${float(total):,.2f}"
                    except (ValueError, TypeError):
                        total_text = "$0.00"
                    
                    date_str = str(date_str).split(" ")[0] if date_str else ""
                    
                    def edit_callback(e, pid=pid):
                        self.open_edit_dialog(pid)
                    
                    def delete_callback(e, pid=pid):
                        self.delete_purchase(pid)
                    
                    actions_row = ft.Row([
                        ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE, on_click=edit_callback),
                        ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=delete_callback),
                    ], spacing=5)
                    
                    self.purchases_table.rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(pid))),
                        ft.DataCell(ft.Text(mat_name)),
                        ft.DataCell(ft.Text(str(qty))),
                        ft.DataCell(ft.Text(unit_price_text)),
                        ft.DataCell(ft.Text(total_text)),
                        ft.DataCell(ft.Text(supplier)),
                        ft.DataCell(ft.Text(date_str)),
                        ft.DataCell(actions_row),
                    ]))
            self.page.update()
        except Exception as e:
            print(f"Error en refresh_table: {e}")
            import traceback
            traceback.print_exc()