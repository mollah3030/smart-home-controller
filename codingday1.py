import flet as ft
from datetime import datetime


def main(page: ft.Page):
    page.title = "Smart Home Controller"
    page.padding = 20
    page.theme_mode = "light"
    page.window_width = 950
    page.window_height = 700
    page.scroll = ft.ScrollMode.AUTO   # allow page to scroll

    # ------------------------------------------------------------------
    # DEVICE STATE
    # ------------------------------------------------------------------
    light_on = False
    door_locked = True
    thermostat_value = 22
    fan_speed = 0

    # ------------------------------------------------------------------
    # UI ELEMENTS WE UPDATE
    # ------------------------------------------------------------------
    light_status_text = ft.Text()
    door_status_text = ft.Text()
    thermostat_status_text = ft.Text()
    fan_status_text = ft.Text()

    # Summary bar elements
    summary_power_text = ft.Text(weight="bold")
    summary_devices_text = ft.Text(weight="bold")
    summary_last_action_text = ft.Text("Last action: –")

    # ------------------------------------------------------------------
    # LOGS & POWER DATA
    # ------------------------------------------------------------------
    device_logs = {
        "light": [],
        "door": [],
        "thermostat": [],
        "fan": [],
    }

    action_log: list[dict] = []  # {"time","device","action","user"}
    power_data: list[dict] = []  # {"x","y"} samples

    # ------------------------------------------------------------------
    # POWER SIMULATION
    # ------------------------------------------------------------------
    def calc_power() -> int:
        power = 0
        if light_on:
            power += 20
        if not door_locked:
            power += 5
        power += (thermostat_value - 18) * 2
        power += fan_speed * 10
        return max(power, 0)

    def update_summary(time_str: str | None = None,
                       device_id: str | None = None,
                       action: str | None = None) -> None:
        summary_power_text.value = f"{calc_power()} W"

        active_count = 0
        if light_on:
            active_count += 1
        if not door_locked:
            active_count += 1
        if fan_speed > 0:
            active_count += 1

        summary_devices_text.value = f"Active devices: {active_count}"

        if time_str and device_id and action:
            summary_last_action_text.value = (
                f"Last action: {time_str} – {device_id}: {action}"
            )

    def record_action(device_key: str, device_id: str, action: str) -> None:
        time_str = datetime.now().strftime("%H:%M:%S")

        device_logs[device_key].append(f"{time_str} – {action} (User)")

        action_log.append(
            {
                "time": time_str,
                "device": device_id,
                "action": action,
                "user": "User",
            }
        )

        power_data.append(
            {
                "x": len(power_data),
                "y": calc_power(),
            }
        )

        update_summary(time_str, device_id, action)

    # ------------------------------------------------------------------
    # HEADER + SUMMARY BAR
    # ------------------------------------------------------------------
    def header(active_tab: str) -> ft.Row:
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text("Smart Home Controller", size=26, weight="bold"),
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Overview",
                            style=ft.ButtonStyle(
                                color=ft.Colors.BLUE
                                if active_tab == "overview"
                                else ft.Colors.BLACK
                            ),
                            on_click=lambda e: page.go("/"),
                        ),
                        ft.TextButton(
                            "Statistics",
                            style=ft.ButtonStyle(
                                color=ft.Colors.BLUE
                                if active_tab == "stats"
                                else ft.Colors.BLACK
                            ),
                            on_click=lambda e: page.go("/stats"),
                        ),
                    ]
                ),
            ],
        )

    def summary_bar() -> ft.Container:
        power_card = ft.Container(
            padding=10,
            bgcolor="#E3F2FD",
            border_radius=10,
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Text("Power now", size=12, color="#0D47A1"),
                    summary_power_text,
                ],
            ),
        )

        devices_card = ft.Container(
            padding=10,
            bgcolor="#E8F5E9",
            border_radius=10,
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Text("Status", size=12, color="#1B5E20"),
                    summary_devices_text,
                ],
            ),
        )

        last_action_card = ft.Container(
            padding=10,
            bgcolor="#FFFDE7",
            border_radius=10,
            expand=True,
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Text("Activity", size=12, color="#F57F17"),
                    summary_last_action_text,
                ],
            ),
        )

        return ft.Container(
            padding=10,
            bgcolor="#FAFAFA",
            border_radius=10,
            content=ft.Row(
                spacing=10,
                controls=[power_card, devices_card, last_action_card],
            ),
        )

    # ------------------------------------------------------------------
    # ACTION HANDLERS
    # ------------------------------------------------------------------
    def toggle_light(e: ft.ControlEvent) -> None:
        nonlocal light_on
        light_on = not light_on

        record_action("light", "light1", "Turn ON" if light_on else "Turn OFF")

        light_status_text.value = f"Status: {'ON' if light_on else 'OFF'}"
        e.control.text = "Turn OFF" if light_on else "Turn ON"

        page.update()

    def toggle_door(e: ft.ControlEvent) -> None:
        nonlocal door_locked
        door_locked = not door_locked

        record_action("door", "door1", "Unlock" if not door_locked else "Lock")

        door_status_text.value = f"Door: {'LOCKED' if door_locked else 'UNLOCKED'}"
        e.control.text = "Unlock" if door_locked else "Lock"

        page.update()

    def change_temp(e: ft.ControlEvent) -> None:
        nonlocal thermostat_value
        thermostat_value = int(e.control.value)

        record_action("thermostat", "thermo1", f"Set {thermostat_value} °C")

        thermostat_status_text.value = f"Set point: {thermostat_value} °C"
        page.update()

    def change_fan(e: ft.ControlEvent) -> None:
        nonlocal fan_speed
        fan_speed = int(e.control.value)

        record_action("fan", "fan1", f"Speed {fan_speed}")

        fan_status_text.value = f"Fan speed: {fan_speed}"
        page.update()

    # ------------------------------------------------------------------
    # DETAILS VIEWS
    # ------------------------------------------------------------------
    def make_details(
        device_key: str,
        title: str,
        device_id: str,
        device_type: str,
        state: str,
    ) -> ft.View:
        actions_column = ft.Column(
            controls=[ft.Text(x) for x in device_logs[device_key]],
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
            height=250,
        )

        return ft.View(
            route=f"/details/{device_key}",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text("Smart Home Controller", size=26, weight="bold"),
                summary_bar(),
                ft.Container(height=10),
                ft.Container(
                    width=600,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                    padding=20,
                    content=ft.Column(
                        controls=[
                            ft.Text(f"{title} details", size=22, weight="bold"),
                            ft.Text(f"ID: {device_id}"),
                            ft.Text(f"Type: {device_type}"),
                            ft.Text(f"State: {state}", weight="bold"),
                            ft.Container(height=10),
                            ft.Text("Recent actions:", size=20, weight="bold"),
                            actions_column,
                            ft.Container(height=10),
                            ft.TextButton(
                                "Back to overview",
                                on_click=lambda e: page.go("/"),
                            ),
                        ]
                    ),
                ),
            ],
        )

    # ------------------------------------------------------------------
    # ROUTING
    # ------------------------------------------------------------------
    def route_change(route: ft.RouteChangeEvent) -> None:
        page.views.clear()

        light_status_text.value = f"Status: {'ON' if light_on else 'OFF'}"
        door_status_text.value = f"Door: {'LOCKED' if door_locked else 'UNLOCKED'}"
        thermostat_status_text.value = f"Set point: {thermostat_value} °C"
        fan_status_text.value = f"Fan speed: {fan_speed}"

        update_summary()

        if page.route == "/":
            light_card = ft.Container(
                width=360,
                bgcolor="#FFEFC2",
                border_radius=15,
                padding=15,
                content=ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text("💡 Living Room Light", size=18, weight="bold"),
                        light_status_text,
                        ft.Text("Tap the button to toggle the light."),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.TextButton(
                                    "Details",
                                    on_click=lambda e: page.go("/details/light"),
                                ),
                                ft.FilledButton(
                                    "Turn ON" if not light_on else "Turn OFF",
                                    on_click=toggle_light,
                                ),
                            ],
                        ),
                    ],
                ),
            )

            door_card = ft.Container(
                width=360,
                bgcolor="#FBE2D0",
                border_radius=15,
                padding=15,
                content=ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text("🚪 Front Door", size=18, weight="bold"),
                        door_status_text,
                        ft.Text("Lock or unlock the front door."),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                ft.TextButton(
                                    "Details",
                                    on_click=lambda e: page.go("/details/door"),
                                ),
                                ft.FilledButton(
                                    "Unlock" if door_locked else "Lock",
                                    on_click=toggle_door,
                                ),
                            ],
                        ),
                    ],
                ),
            )

            thermostat_card = ft.Container(
                width=360,
                bgcolor="#FFD6E0",
                border_radius=15,
                padding=15,
                content=ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text("🌡️ Thermostat", size=18, weight="bold"),
                        thermostat_status_text,
                        ft.Text("Use slider to change temperature."),
                        ft.Slider(
                            min=15,
                            max=30,
                            value=thermostat_value,
                            on_change=change_temp,
                        ),
                        ft.TextButton(
                            "Details",
                            on_click=lambda e: page.go("/details/thermostat"),
                        ),
                    ],
                ),
            )

            fan_card = ft.Container(
                width=360,
                bgcolor="#D6F5FF",
                border_radius=15,
                padding=15,
                content=ft.Column(
                    spacing=5,
                    controls=[
                        ft.Text("🌀 Ceiling Fan", size=18, weight="bold"),
                        fan_status_text,
                        ft.Text("0 = OFF, 3 = MAX speed."),
                        ft.Slider(
                            min=0,
                            max=3,
                            divisions=3,
                            value=fan_speed,
                            on_change=change_fan,
                        ),
                        ft.TextButton(
                            "Details",
                            on_click=lambda e: page.go("/details/fan"),
                        ),
                    ],
                ),
            )

            main_content = ft.Column(
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    summary_bar(),
                    ft.Container(height=10),
                    ft.Text("On/Off devices", size=20, weight="bold"),
                    ft.Row(controls=[light_card, door_card], spacing=20),
                    ft.Container(height=20),
                    ft.Text("Slider controlled devices", size=20, weight="bold"),
                    ft.Row(controls=[thermostat_card, fan_card], spacing=20),
                ],
            )

            page.views.append(
                ft.View(
                    route="/",
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        header("overview"),
                        main_content,
                    ],
                )
            )

        elif page.route == "/stats":
            if power_data:
                points = [ft.LineChartDataPoint(p["x"], p["y"]) for p in power_data]
                max_x = max(p["x"] for p in power_data)
                max_y = max(p["y"] for p in power_data)
                max_x = max(max_x, 10)
                max_y = max(max_y, 10)
            else:
                points = [ft.LineChartDataPoint(0, 0)]
                max_x = 10
                max_y = 10

            chart = ft.LineChart(
                data_series=[ft.LineChartData(points)],
                min_x=0,
                max_x=max_x,
                min_y=0,
                max_y=max_y,
                border=ft.border.all(1, ft.Colors.GREY_400),
                expand=True,
            )

            stats_table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Time")),
                    ft.DataColumn(ft.Text("Device")),
                    ft.DataColumn(ft.Text("Action")),
                    ft.DataColumn(ft.Text("User")),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(r["time"])),
                            ft.DataCell(ft.Text(r["device"])),
                            ft.DataCell(ft.Text(r["action"])),
                            ft.DataCell(ft.Text(r["user"])),
                        ]
                    )
                    for r in action_log
                ],
            )

            table_wrapper = ft.Container(
                height=250,
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(1, ft.Colors.GREY_300),
                padding=10,
                content=ft.Column(
                    controls=[stats_table],
                    scroll=ft.ScrollMode.AUTO,
                ),
            )

            stats_content = ft.Column(
                spacing=10,
                scroll=ft.ScrollMode.AUTO,
                controls=[
                    summary_bar(),
                    ft.Text(
                        "Power consumption (simulated)",
                        size=20,
                        weight="bold",
                    ),
                    ft.Container(
                        height=260,
                        padding=10,
                        bgcolor=ft.Colors.WHITE,
                        border=ft.border.all(1, ft.Colors.GREY_300),
                        content=chart,
                    ),
                    ft.Text("Action log", size=20, weight="bold"),
                    table_wrapper,
                ],
            )

            page.views.append(
                ft.View(
                    route="/stats",
                    scroll=ft.ScrollMode.AUTO,
                    controls=[
                        header("stats"),
                        stats_content,
                    ],
                )
            )

        elif page.route == "/details/light":
            page.views.append(
                make_details(
                    "light",
                    "Living Room Light",
                    "light1",
                    "light",
                    "ON" if light_on else "OFF",
                )
            )

        elif page.route == "/details/door":
            page.views.append(
                make_details(
                    "door",
                    "Front Door",
                    "door1",
                    "door",
                    "LOCKED" if door_locked else "UNLOCKED",
                )
            )

        elif page.route == "/details/thermostat":
            page.views.append(
                make_details(
                    "thermostat",
                    "Thermostat",
                    "thermo1",
                    "thermostat",
                    f"{thermostat_value}°C",
                )
            )

        elif page.route == "/details/fan":
            page.views.append(
                make_details(
                    "fan",
                    "Ceiling Fan",
                    "fan1",
                    "fan",
                    f"Speed {fan_speed}",
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go("/")


ft.app(target=main, view=ft.AppView.WEB_BROWSER)
