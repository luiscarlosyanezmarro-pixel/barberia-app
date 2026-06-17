import flet as ft
import re
from datetime import datetime

class DashboardScreen:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.cards_row = None
        self.sales_table = None
        self.status_text = None
    
    def build(self):
        self.cards_row = ft.Row(spacing=20, alignment=ft.MainAxisAlignment.CENTER)
        self.sales_table = ft.Container()
        self.status_text = ft.Text("", size=12, color=ft.Colors.GREY)
        
        refresh_button = ft.ElevatedButton(
            "Actualizar Datos", icon=ft.Icons.REFRESH, on_click=self.refresh_dashboard,
            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_700)
        )
        
        main_column = ft.Column([
            ft.Row([ft.Text("Dashboard", size=30, weight=ft.FontWeight.BOLD), refresh_button],
                   alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=20),
            self.cards_row,
            ft.Container(height=30),
            ft.Text("Ventas Recientes", size=20, weight=ft.FontWeight.BOLD),
            ft.Container(height=10),
            self.sales_table,
            ft.Container(height=10),
            self.status_text,
        ], scroll=ft.ScrollMode.AUTO)
        
        content = ft.Container(content=main_column, padding=20, expand=True)
        self.refresh_dashboard()
        return content
    
    def refresh_dashboard(self, e=None):
        try:
            self.status_text.value = "Actualizando datos..."
            self.status_text.color = ft.Colors.BLUE
            self.page.update()
            self.update_cards()
            self.update_recent_sales()
            self.status_text.value = "Datos actualizados correctamente"
            self.status_text.color = ft.Colors.GREEN
            self.page.update()
            
            import threading, time
            def clear_status():
                time.sleep(3)
                if self.status_text:
                    self.status_text.value = ""
                    self.page.update()
            threading.Thread(target=clear_status, daemon=True).start()
        except Exception as e:
            print(f"Error en dashboard: {e}")
            self.status_text.value = f"Error: {str(e)}"
            self.status_text.color = ft.Colors.RED
            self.page.update()
    
    def update_cards(self):
        try:
            print("=== Actualizando cards del dashboard ===")
            
            today = datetime.now().strftime("%Y-%m-%d")
            print(f"Fecha actual desde la app: {today}")
            
            stats = self.db.api.get_dashboard_stats()
            total_services = stats.get("total_services", 0)
            total_sales_today = self.db.api.get_sales_by_date(today)
            appointments = self.db.api.get_appointments(filter_date=today)
            total_appointments = len(appointments) if appointments else 0
            low_stock = stats.get("low_stock", 0)
            
            print(f"Servicios activos: {total_services}")
            print(f"Ventas hoy (monto total): ${total_sales_today}")
            print(f"Citas hoy: {total_appointments}")
            print(f"Stock bajo: {low_stock}")
            
            self.cards_row.controls = [
                self._create_card("Servicios Activos", str(total_services), ft.Icons.CUT, ft.Colors.BLUE),
                self._create_card("Ventas Hoy", f"${total_sales_today:,.2f}", ft.Icons.ATTACH_MONEY, ft.Colors.GREEN),
                self._create_card("Citas Hoy", str(total_appointments), ft.Icons.CALENDAR_TODAY, ft.Colors.ORANGE),
                self._create_card("Stock Bajo", str(low_stock), ft.Icons.WARNING, ft.Colors.RED),
            ]
            self.page.update()
            print("=== Cards actualizadas correctamente ===")
            
        except Exception as e:
            print(f"Error en update_cards: {e}")
            import traceback
            traceback.print_exc()
            self.cards_row.controls = [ft.Text(f"Error: {str(e)}", color=ft.Colors.RED)]
            self.page.update()
    
    def update_recent_sales(self):
        try:
            recent_sales = self.db.fetch_all("""
                SELECT s.client_name, ser.name, s.price, s.sale_date, 
                       s.client_phone, s.payment_method, s.barber_name, s.id
                FROM sales s
                JOIN services ser ON s.service_id = ser.id
                ORDER BY s.sale_date DESC
                LIMIT 5
            """)
            
            if recent_sales and len(recent_sales) > 0:
                table = ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Cliente", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Servicio", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Precio", weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Fecha", weight=ft.FontWeight.BOLD)),
                    ],
                    rows=[],
                    width=900,
                    heading_row_color=ft.Colors.GREY_100,
                )
                
                for sale in recent_sales:
                    client_name = sale[2] if len(sale) > 2 and sale[2] else "N/A"
                    service_name = sale[1] if len(sale) > 1 and sale[1] else "N/A"
                    sale_date = str(sale[5]).split(" ")[0] if len(sale) > 5 and sale[5] else ""
                    
                    try:
                        price = float(sale[4]) if len(sale) > 4 and sale[4] else 0
                        price_text = f"${price:,.2f}"
                    except (ValueError, TypeError):
                        price_text = "$0.00"
                    
                    table.rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(client_name)),
                        ft.DataCell(ft.Text(service_name)),
                        ft.DataCell(ft.Text(price_text)),
                        ft.DataCell(ft.Text(sale_date)),
                    ]))
                
                self.sales_table.content = table
            else:
                self.sales_table.content = ft.Container(
                    content=ft.Text("No hay ventas recientes", size=14, color=ft.Colors.GREY),
                    padding=20, alignment=ft.Alignment.CENTER
                )
            self.page.update()
        except Exception as e:
            print(f"Error en ventas recientes: {e}")
    
    def _create_card(self, title, value, icon, color):
        return ft.Container(
            content=ft.Column([
                ft.Icon(icon, size=40, color=color),
                ft.Text(title, size=14, color=ft.Colors.GREY_700, text_align=ft.TextAlign.CENTER),
                ft.Text(str(value), size=28, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            width=220, padding=20, bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=10, color=ft.Colors.GREY_300),
            ink=True,
        )