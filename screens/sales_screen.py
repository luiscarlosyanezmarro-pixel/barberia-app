import flet as ft
from datetime import datetime
import re

class SalesScreen:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.dialog = None
        self.editing_id = None
        self.edit_service_dropdown = None
        self.edit_client_name = None
        self.edit_client_phone = None
        self.edit_payment_method = None
        self.edit_barber_name = None
        self.edit_price = None
        self.services = None
    
    def build(self):
        self.services = self.db.fetch_all("SELECT id, name, price FROM services WHERE active = 1")
        
        service_options = []
        for s in self.services:
            service_id = s[0]
            service_name = s[1] if s[1] else "Sin nombre"
            try:
                price = float(s[2]) if s[2] else 0
                service_options.append(ft.dropdown.Option(key=str(service_id), text=f"{service_name} - ${price:,.2f}"))
            except (ValueError, TypeError):
                service_options.append(ft.dropdown.Option(key=str(service_id), text=f"{service_name} - Precio no definido"))
        
        service_dropdown = ft.Dropdown(label="Servicio", options=service_options, width=300)
        client_name = ft.TextField(label="Nombre del Cliente", width=250)
        client_phone = ft.TextField(label="Teléfono", width=200)
        payment_method = ft.Dropdown(
            label="Método de Pago",
            options=[
                ft.dropdown.Option("efectivo", "Efectivo"),
                ft.dropdown.Option("tarjeta", "Tarjeta"),
                ft.dropdown.Option("transferencia", "Transferencia"),
            ],
            width=200
        )
        barber_name = ft.TextField(label="Barbero", width=200)
        
        def register_sale(e):
            if service_dropdown.value and client_name.value:
                try:
                    selected_service = next(s for s in self.services if str(s[0]) == service_dropdown.value)
                    price = float(selected_service[2]) if selected_service[2] else 0
                    
                    self.db.execute_query("""
                        INSERT INTO sales (service_id, client_name, client_phone, price, 
                                         payment_method, barber_name)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (selected_service[0], client_name.value, client_phone.value,
                          price, payment_method.value, barber_name.value))
                    
                    service_dropdown.value = None
                    client_name.value = ""
                    client_phone.value = ""
                    barber_name.value = ""
                    
                    self.refresh_table()
                    self.page.update()
                    self.show_snack_bar("Venta registrada exitosamente", ft.Colors.GREEN)
                    
                except Exception as ex:
                    print(f"Error al registrar venta: {ex}")
                    self.show_snack_bar(f"Error: {str(ex)}", ft.Colors.RED)
        
        register_button = ft.ElevatedButton(
            "Registrar Venta", icon=ft.Icons.SHOPPING_CART, on_click=register_sale,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700)
        )
        
        self.sales_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Cliente", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Teléfono", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Servicio", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Precio", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Método Pago", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Barbero", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("Acciones", weight=ft.FontWeight.BOLD)),
            ], rows=[], width=1400
        )
        
        main_column = ft.Column([
            ft.Text("Registrar Venta", size=30, weight=ft.FontWeight.BOLD), ft.Container(height=20),
            ft.Card(content=ft.Container(content=ft.Column([
                ft.Text("Nueva Venta", size=18, weight=ft.FontWeight.BOLD), ft.Container(height=10),
                ft.Row([service_dropdown, client_name, client_phone, payment_method, barber_name, register_button], wrap=True, spacing=10),
            ], spacing=10), padding=20), elevation=3),
            ft.Container(height=30),
            ft.Text("Ventas Registradas", size=20, weight=ft.FontWeight.BOLD), ft.Container(height=10),
            ft.Container(content=self.sales_table, height=400)
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
    
    def open_edit_dialog(self, sale_id):
        print(f"Abriendo diálogo para EDITAR venta ID: {sale_id}")
        
        result = self.db.fetch_one("SELECT * FROM sales WHERE id = %s", (sale_id,))
        
        print(f"Resultado de la consulta (raw): {result}")
        
        if result:
            self.editing_id = sale_id
            
            # Estructura de la tupla de sales (desde database.py):
            # result[0] = id, result[1] = service_id, result[2] = client_name
            # result[3] = client_phone, result[4] = price, result[5] = sale_date
            # result[6] = payment_method, result[7] = barber_name, result[8] = user_id
            
            service_id = result[1]
            client_name = result[2] if result[2] else ""
            client_phone = result[3] if result[3] else ""
            price = result[4] if result[4] else 0
            payment_method = result[6] if result[6] else "efectivo"
            barber_name = result[7] if result[7] else ""
            
            print(f"Datos cargados - Cliente: {client_name}, Servicio ID: {service_id}, Precio: {price}")
            
            self.edit_client_name = ft.TextField(label="Nombre del Cliente", value=client_name, width=300)
            self.edit_client_phone = ft.TextField(label="Teléfono", value=client_phone, width=200)
            
            service_options = []
            for s in self.services:
                sid = s[0]
                sname = s[1] if s[1] else "Sin nombre"
                try:
                    sprice = float(s[2]) if s[2] else 0
                    service_options.append(ft.dropdown.Option(key=str(sid), text=f"{sname} - ${sprice:,.2f}"))
                except (ValueError, TypeError):
                    service_options.append(ft.dropdown.Option(key=str(sid), text=f"{sname} - Precio no definido"))
            
            self.edit_service_dropdown = ft.Dropdown(label="Servicio", options=service_options, value=str(service_id), width=300)
            self.edit_price = ft.TextField(label="Precio", value=str(price), width=150,
                                          input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*\.?[0-9]*$"), max_length=10)
            self.edit_payment_method = ft.Dropdown(label="Método de Pago", options=[
                ft.dropdown.Option("efectivo", "Efectivo"),
                ft.dropdown.Option("tarjeta", "Tarjeta"),
                ft.dropdown.Option("transferencia", "Transferencia"),
            ], value=payment_method, width=200)
            self.edit_barber_name = ft.TextField(label="Barbero", value=barber_name, width=200)
            
            self._show_edit_dialog()
        else:
            self.show_snack_bar(f"Error: Venta ID {sale_id} no encontrada", ft.Colors.RED)
    
    def _show_edit_dialog(self):
        dialog_content = ft.Column([
            ft.Text("Editar Venta", size=20, weight=ft.FontWeight.BOLD), ft.Container(height=10),
            self.edit_client_name, self.edit_client_phone, self.edit_service_dropdown,
            self.edit_price, self.edit_payment_method, self.edit_barber_name
        ], spacing=10, width=400, height=450, scroll=ft.ScrollMode.AUTO)
        
        def on_cancel(e): self.close_dialog()
        def on_save(e): self.update_sale()
        
        self.dialog = ft.AlertDialog(content=dialog_content, actions=[
            ft.TextButton("Cancelar", on_click=on_cancel),
            ft.ElevatedButton("Guardar", on_click=on_save, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
        ], actions_alignment=ft.MainAxisAlignment.END, on_dismiss=lambda e: self.close_dialog())
        
        self.page.overlay.append(self.dialog)
        self.page.update()
        self.dialog.open = True
        self.page.update()
    
    def update_sale(self):
        if not self.edit_client_name.value:
            self.show_snack_bar("Por favor ingrese el nombre del cliente", ft.Colors.RED)
            return
        if not self.edit_service_dropdown.value:
            self.show_snack_bar("Por favor seleccione un servicio", ft.Colors.RED)
            return
        try:
            price = float(self.edit_price.value) if self.edit_price.value else 0
            self.db.execute_query("""UPDATE sales SET service_id = %s, client_name = %s, client_phone = %s, 
                    price = %s, payment_method = %s, barber_name = %s WHERE id = %s""",
                (int(self.edit_service_dropdown.value), self.edit_client_name.value,
                 self.edit_client_phone.value, price, self.edit_payment_method.value,
                 self.edit_barber_name.value, self.editing_id))
            self.close_dialog()
            self.refresh_table()
            self.show_snack_bar("Venta actualizada exitosamente", ft.Colors.GREEN)
        except Exception as ex:
            print(f"Error al actualizar: {ex}")
            self.show_snack_bar(f"Error: {str(ex)}", ft.Colors.RED)
    
    def delete_sale(self, sale_id):
        try:
            self.db.execute_query("DELETE FROM sales WHERE id = %s", (sale_id,))
            self.refresh_table()
            self.show_snack_bar("Venta eliminada exitosamente", ft.Colors.GREEN)
        except Exception as ex:
            print(f"Error al eliminar: {ex}")
            self.show_snack_bar(f"Error al eliminar: {str(ex)}", ft.Colors.RED)
    
    def refresh_table(self):
        try:
            sales = self.db.fetch_all("""
                SELECT s.id, ser.name, s.client_name, s.client_phone, s.price, 
                       s.payment_method, s.barber_name, s.sale_date
                FROM sales s 
                JOIN services ser ON s.service_id = ser.id 
                ORDER BY s.id ASC
            """)
            
            self.sales_table.rows = []
            
            if not sales or len(sales) == 0:
                self.sales_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("-")) for _ in range(9)]))
            else:
                for sale in sales:
                    # Índices: sale[0]=ID, sale[1]=Servicio, sale[2]=Cliente, sale[3]=Teléfono
                    # sale[4]=Precio, sale[5]=Fecha, sale[6]=Método Pago, sale[7]=Barbero
                    
                    sale_id = sale[0]
                    service_name = sale[1] if sale[1] else "N/A"
                    client_name = sale[2] if sale[2] else "N/A"
                    client_phone = sale[3] if sale[3] else "N/A"
                    payment_method = sale[6] if sale[6] else "N/A"
                    barber_name = sale[7] if sale[7] else "N/A"
                    sale_date = str(sale[5]).split(" ")[0] if sale[5] else ""
                    
                    try:
                        price = float(sale[4]) if sale[4] else 0
                        price_text = f"${price:,.2f}"
                    except:
                        price_text = "$0.00"
                    
                    def delete_sale(e, sid=sale_id): 
                        self.delete_sale(sid)
                    
                    def edit_sale(e, sid=sale_id): 
                        self.open_edit_dialog(sid)
                    
                    actions_row = ft.Row([
                        ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE, on_click=edit_sale),
                        ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=delete_sale),
                    ], spacing=5)
                    
                    self.sales_table.rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(sale_id))),          # ID
                        ft.DataCell(ft.Text(client_name)),           # Cliente
                        ft.DataCell(ft.Text(client_phone)),          # Teléfono
                        ft.DataCell(ft.Text(service_name)),          # Servicio
                        ft.DataCell(ft.Text(price_text)),            # Precio
                        ft.DataCell(ft.Text(payment_method)),        # Método Pago
                        ft.DataCell(ft.Text(barber_name)),           # Barbero
                        ft.DataCell(ft.Text(sale_date)),             # Fecha
                        ft.DataCell(actions_row),                    # Acciones
                    ]))
            self.page.update()
        except Exception as e:
            print(f"Error al refrescar ventas: {e}")
            import traceback
            traceback.print_exc()