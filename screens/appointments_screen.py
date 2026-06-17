import flet as ft
from datetime import datetime, timedelta

class AppointmentsScreen:
    def __init__(self, page, db):
        self.page = page
        self.db = db
        self.dialog = None
        self.editing_id = None
        
        self.appointment_date_picker = ft.DatePicker(
            on_change=self.on_date_change,
            first_date=datetime.now(),
            last_date=datetime.now() + timedelta(days=90)
        )
        self.filter_date_picker = ft.DatePicker(on_change=self.filter_by_date)
        self.edit_date_picker = ft.DatePicker(on_change=self.on_edit_date_change)
        
        self.page.overlay.append(self.appointment_date_picker)
        self.page.overlay.append(self.filter_date_picker)
        self.page.overlay.append(self.edit_date_picker)
        
        self.client_name_field = None
        self.client_phone_field = None
        self.service_dropdown = None
        self.appointment_time_dropdown = None
        self.barber_name_field = None
        self.date_text = None
        
        self.edit_client_name = None
        self.edit_client_phone = None
        self.edit_service_dropdown = None
        self.edit_date_text = None
        self.edit_time_dropdown = None
        self.edit_barber_name = None
        self.edit_status_dropdown = None
        
        self.services = None
        self.time_options = None
    
    def on_date_change(self, e):
        if self.appointment_date_picker.value:
            self.date_text.value = self.appointment_date_picker.value.strftime("%Y-%m-%d")
            self.page.update()
    
    def on_edit_date_change(self, e):
        if self.edit_date_picker.value:
            self.edit_date_text.value = self.edit_date_picker.value.strftime("%Y-%m-%d")
            self.page.update()
    
    def filter_by_date(self, e):
        if self.filter_date_picker.value:
            self.refresh_table(filter_date=self.filter_date_picker.value.strftime("%Y-%m-%d"))
    
    def build(self):
        self.client_name_field = ft.TextField(label="Nombre del Cliente", width=300)
        self.client_phone_field = ft.TextField(label="Teléfono", width=200)
        
        self.services = self.db.fetch_all("SELECT id, name, duration FROM services WHERE active = 1")
        service_options = [ft.dropdown.Option(key=str(s[0]), text=s[1]) for s in self.services]
        self.service_dropdown = ft.Dropdown(label="Servicio", options=service_options, width=250)
        
        self.time_options = []
        for hour in range(9, 20):
            for minute in [0, 30]:
                self.time_options.append(ft.dropdown.Option(f"{hour:02d}:{minute:02d}", f"{hour:02d}:{minute:02d}"))
        
        self.appointment_time_dropdown = ft.Dropdown(label="Hora", options=self.time_options, width=150)
        self.barber_name_field = ft.TextField(label="Barbero", width=200, value="Carlos")
        self.date_text = ft.Text("No seleccionada", size=14, color=ft.Colors.BLUE)
        
        date_button = ft.ElevatedButton("Seleccionar Fecha", icon=ft.Icons.CALENDAR_MONTH,
                                        on_click=lambda e: self.open_date_picker(self.appointment_date_picker), width=200)
        schedule_button = ft.ElevatedButton("Agendar Cita", icon=ft.Icons.CALENDAR_MONTH, on_click=self.schedule_appointment,
                                            style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_700))
        
        self.appointments_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Cliente")), ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Servicio")), ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Hora")),
                ft.DataColumn(ft.Text("Barbero")), ft.DataColumn(ft.Text("Estado")), ft.DataColumn(ft.Text("Acciones")),
            ], rows=[], width=1300
        )
        
        filter_date_button = ft.ElevatedButton("Filtrar por Fecha", icon=ft.Icons.FILTER_ALT,
                                               on_click=lambda e: self.open_date_picker(self.filter_date_picker))
        show_all_button = ft.ElevatedButton("Mostrar Todos", icon=ft.Icons.LIST_ALT, on_click=lambda e: self.refresh_table())
        filters_row = ft.Row([ft.Text("Filtrar:", size=16, weight=ft.FontWeight.BOLD), filter_date_button, show_all_button], spacing=10)
        
        form_card = ft.Card(content=ft.Container(content=ft.Column([
            ft.Text("Agendar Nueva Cita", size=18, weight=ft.FontWeight.BOLD), ft.Container(height=10),
            ft.Row([self.client_name_field, self.client_phone_field, self.service_dropdown], wrap=True, spacing=10),
            ft.Row([date_button, ft.Text("Fecha seleccionada: ", size=14), self.date_text, self.appointment_time_dropdown,
                    self.barber_name_field, schedule_button], wrap=True, spacing=10),
        ], spacing=10), padding=20), elevation=3)
        
        table_container = ft.Container(content=self.appointments_table, height=400, border_radius=10, bgcolor=ft.Colors.WHITE, padding=10)
        main_column = ft.Column([ft.Text("Gestión de Citas", size=30, weight=ft.FontWeight.BOLD), ft.Container(height=20),
                                 form_card, ft.Container(height=20), filters_row, ft.Container(height=10), table_container], scroll=ft.ScrollMode.AUTO)
        content = ft.Container(content=main_column, padding=20, expand=True)
        self.refresh_table()
        return content
    
    def open_date_picker(self, picker):
        picker.open = True
        self.page.update()
    
    def schedule_appointment(self, e):
        if not self.client_name_field.value:
            self.show_snack_bar("Ingrese nombre del cliente", ft.Colors.RED)
            return
        if not self.service_dropdown.value:
            self.show_snack_bar("Seleccione un servicio", ft.Colors.RED)
            return
        if self.date_text.value == "No seleccionada":
            self.show_snack_bar("Seleccione una fecha", ft.Colors.RED)
            return
        if not self.appointment_time_dropdown.value:
            self.show_snack_bar("Seleccione una hora", ft.Colors.RED)
            return
        try:
            self.db.execute_query("""INSERT INTO appointments (client_name, client_phone, service_id, 
                                        appointment_date, appointment_time, barber_name, status)
                                    VALUES (%s, %s, %s, %s, %s, %s, 'pendiente')""",
                                 (self.client_name_field.value, self.client_phone_field.value, int(self.service_dropdown.value),
                                  self.date_text.value, self.appointment_time_dropdown.value, self.barber_name_field.value))
            self.client_name_field.value = ""; self.client_phone_field.value = ""; self.service_dropdown.value = None
            self.date_text.value = "No seleccionada"; self.appointment_time_dropdown.value = None; self.barber_name_field.value = "Carlos"
            self.refresh_table()
            self.show_snack_bar("Cita agendada exitosamente", ft.Colors.GREEN)
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", ft.Colors.RED)
    
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
    
    def open_edit_dialog(self, appointment_id):
        print(f"Abriendo diálogo para EDITAR cita ID: {appointment_id}")
        appointment = self.db.fetch_one("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
        if appointment:
            self.editing_id = appointment_id
            client_name = appointment[1] if appointment[1] else ""
            client_phone = appointment[2] if appointment[2] else ""
            service_id = appointment[3]
            appointment_date = appointment[4] if appointment[4] else ""
            appointment_time_raw = appointment[5] if appointment[5] else ""
            if hasattr(appointment_time_raw, 'strftime'):
                appointment_time = appointment_time_raw.strftime("%H:%M")
            else:
                appointment_time = str(appointment_time_raw) if appointment_time_raw else ""
                if len(appointment_time) > 5:
                    appointment_time = appointment_time[:5]
            barber_name = appointment[6] if appointment[6] else ""
            status = appointment[7] if appointment[7] else "pendiente"
            
            self.edit_client_name = ft.TextField(label="Nombre del Cliente", value=client_name, width=300)
            self.edit_client_phone = ft.TextField(label="Teléfono", value=client_phone, width=200)
            service_options = [ft.dropdown.Option(key=str(s[0]), text=s[1]) for s in self.services]
            self.edit_service_dropdown = ft.Dropdown(label="Servicio", options=service_options, value=str(service_id), width=250)
            self.edit_date_text = ft.Text(appointment_date if appointment_date else "No seleccionada", size=14, color=ft.Colors.BLUE)
            edit_date_button = ft.ElevatedButton("Seleccionar Fecha", icon=ft.Icons.CALENDAR_MONTH,
                                                 on_click=lambda e: self.open_date_picker(self.edit_date_picker), width=200)
            self.edit_time_dropdown = ft.Dropdown(label="Hora", options=self.time_options, value=appointment_time if appointment_time else None, width=150)
            self.edit_barber_name = ft.TextField(label="Barbero", value=barber_name, width=200)
            self.edit_status_dropdown = ft.Dropdown(label="Estado", options=[
                ft.dropdown.Option("pendiente", "Pendiente"), ft.dropdown.Option("confirmada", "Confirmada"),
                ft.dropdown.Option("cancelada", "Cancelada"), ft.dropdown.Option("completada", "Completada"),
            ], value=status, width=150)
            self._show_edit_dialog(edit_date_button)
        else:
            self.show_snack_bar(f"Error: Cita ID {appointment_id} no encontrada", ft.Colors.RED)
    
    def _show_edit_dialog(self, edit_date_button):
        dialog_content = ft.Column([
            ft.Text("Editar Cita", size=20, weight=ft.FontWeight.BOLD), ft.Container(height=10),
            self.edit_client_name, self.edit_client_phone, self.edit_service_dropdown,
            ft.Row([edit_date_button, self.edit_date_text], spacing=10), self.edit_time_dropdown,
            self.edit_barber_name, self.edit_status_dropdown,
        ], spacing=10, width=400, height=450, scroll=ft.ScrollMode.AUTO)
        def on_cancel(e): self.close_dialog()
        def on_save(e): self.update_appointment()
        self.dialog = ft.AlertDialog(content=dialog_content, actions=[
            ft.TextButton("Cancelar", on_click=on_cancel),
            ft.ElevatedButton("Guardar", on_click=on_save, bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE)
        ], actions_alignment=ft.MainAxisAlignment.END, on_dismiss=lambda e: self.close_dialog())
        self.page.overlay.append(self.dialog)
        self.page.update()
        self.dialog.open = True
        self.page.update()
    
    def update_appointment(self):
        if not self.edit_client_name.value:
            self.show_snack_bar("Ingrese el nombre del cliente", ft.Colors.RED); return
        if not self.edit_service_dropdown.value:
            self.show_snack_bar("Seleccione un servicio", ft.Colors.RED); return
        if self.edit_date_text.value == "No seleccionada":
            self.show_snack_bar("Seleccione una fecha", ft.Colors.RED); return
        if not self.edit_time_dropdown.value:
            self.show_snack_bar("Seleccione una hora", ft.Colors.RED); return
        try:
            self.db.execute_query("""UPDATE appointments SET client_name = %s, client_phone = %s, service_id = %s,
                    appointment_date = %s, appointment_time = %s, barber_name = %s, status = %s WHERE id = %s""",
                (self.edit_client_name.value, self.edit_client_phone.value, int(self.edit_service_dropdown.value),
                 self.edit_date_text.value, self.edit_time_dropdown.value, self.edit_barber_name.value,
                 self.edit_status_dropdown.value, self.editing_id))
            self.close_dialog(); self.refresh_table(); self.show_snack_bar("Cita actualizada", ft.Colors.GREEN)
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", ft.Colors.RED)
    
    def delete_appointment(self, appointment_id):
        try:
            self.db.execute_query("DELETE FROM appointments WHERE id = %s", (appointment_id,))
            self.refresh_table()
            self.show_snack_bar("Cita eliminada", ft.Colors.GREEN)
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", ft.Colors.RED)
    
    def refresh_table(self, filter_date=None):
        try:
            if filter_date:
                appointments = self.db.fetch_all("""
                    SELECT a.id, a.client_name, a.client_phone, s.name, a.appointment_date, a.appointment_time, a.barber_name, a.status
                    FROM appointments a JOIN services s ON a.service_id = s.id WHERE a.appointment_date = %s
                    ORDER BY a.appointment_date DESC, a.appointment_time ASC
                """, (filter_date,))
            else:
                appointments = self.db.fetch_all("""
                    SELECT a.id, a.client_name, a.client_phone, s.name, a.appointment_date, a.appointment_time, a.barber_name, a.status
                    FROM appointments a JOIN services s ON a.service_id = s.id ORDER BY a.appointment_date DESC, a.appointment_time ASC LIMIT 50
                """)
            self.appointments_table.rows = []
            if not appointments:
                self.appointments_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("")) for _ in range(9)]))
            else:
                for app in appointments:
                    app_id, status = app[0], app[7]
                    status_color = ft.Colors.GREEN if status == "confirmada" else ft.Colors.ORANGE if status == "pendiente" else ft.Colors.RED
                    app_time = app[5]
                    if hasattr(app_time, 'strftime'):
                        app_time = app_time.strftime("%H:%M")
                    elif len(str(app_time)) > 5:
                        app_time = str(app_time)[:5]
                    def confirm(e, aid=app_id): self.update_appointment_status(aid, "confirmada")
                    def cancel(e, aid=app_id): self.update_appointment_status(aid, "cancelada")
                    def complete(e, aid=app_id): self.update_appointment_status(aid, "completada")
                    def edit(e, aid=app_id): self.open_edit_dialog(aid)
                    def delete(e, aid=app_id): self.delete_appointment(aid)
                    actions_row = ft.Row([
                        ft.IconButton(ft.Icons.EDIT, icon_color=ft.Colors.BLUE, on_click=edit),
                        ft.IconButton(ft.Icons.DELETE, icon_color=ft.Colors.RED, on_click=delete),
                        ft.IconButton(ft.Icons.CHECK_CIRCLE, icon_color=ft.Colors.GREEN, on_click=confirm),
                        ft.IconButton(ft.Icons.CLOSE, icon_color=ft.Colors.RED, on_click=cancel),
                        ft.IconButton(ft.Icons.DONE, icon_color=ft.Colors.BLUE, on_click=complete),
                    ], spacing=5)
                    self.appointments_table.rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(str(app_id))), ft.DataCell(ft.Text(app[1] or "")), ft.DataCell(ft.Text(app[2] or "")),
                        ft.DataCell(ft.Text(app[3] or "")), ft.DataCell(ft.Text(str(app[4]) if app[4] else "")), ft.DataCell(ft.Text(str(app_time))),
                        ft.DataCell(ft.Text(app[6] or "")), ft.DataCell(ft.Container(content=ft.Text(status, size=12, color=ft.Colors.WHITE),
                            bgcolor=status_color, padding=5, border_radius=5, width=80, alignment=ft.Alignment.CENTER)), ft.DataCell(actions_row),
                    ]))
            self.page.update()
        except Exception as e:
            print(f"Error: {e}")
    
    def update_appointment_status(self, appointment_id, status):
        try:
            self.db.execute_query("UPDATE appointments SET status = %s WHERE id = %s", (status, appointment_id))
            self.refresh_table()
            self.show_snack_bar(f"Cita {status}", ft.Colors.GREEN)
        except Exception as ex:
            self.show_snack_bar(f"Error: {str(ex)}", ft.Colors.RED)