"""Tkinter tabanlı mantık devresi simülatörü arayüzü."""

from __future__ import annotations

import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox, simpledialog

from .logic import Circuit, GateType


def asset_path(file_name: str) -> Path:
    """Normal çalıştırmada ve PyInstaller EXE içinde asset dosya yolunu döndürür."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "assets" / file_name
    return Path(__file__).resolve().parent / "assets" / file_name


@dataclass
class VisualComponent:
    component_id: str
    kind: str
    x: int
    y: int
    canvas_items: tuple[int, ...]
    value: int = 0
    gate_type: GateType | None = None


class LogicGateSimulator:
    """Canvas üzerinde basit mantık devresi kurmaya yarayan arayüz."""

    GATE_TOOLS = [
        GateType.AND.value,
        GateType.OR.value,
        GateType.NOT.value,
        GateType.BUFFER.value,
        GateType.NAND.value,
        GateType.NOR.value,
        GateType.XOR.value,
        GateType.XNOR.value,
    ]

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Sayısal Tasarım Mantık Devresi Simülatörü")
        self.root.geometry("1050x680")
        self._set_window_icon()

        self.circuit = Circuit()
        self.components: dict[str, VisualComponent] = {}
        self.item_to_component: dict[int, str] = {}
        self.connection_items: list[int] = []
        self.current_tool = "INPUT"
        self.connection_start: str | None = None
        self.counter = 1

        self._build_ui()

    def _set_window_icon(self) -> None:
        """Tkinter penceresi için uygulama ikonunu ayarlar."""
        ico_path = asset_path("app_icon.ico")
        png_path = asset_path("app_icon.png")

        try:
            if ico_path.exists():
                self.root.iconbitmap(str(ico_path))
        except tk.TclError:
            # Bazı platformlarda iconbitmap desteklenmeyebilir.
            pass

        try:
            if png_path.exists():
                self._window_icon = tk.PhotoImage(file=str(png_path))
                self.root.iconphoto(True, self._window_icon)
        except tk.TclError:
            pass

    def _build_ui(self) -> None:
        toolbar = tk.Frame(self.root, relief=tk.RAISED, bd=1)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        for label, tool in [
            ("Input", "INPUT"),
            ("Output", "OUTPUT"),
            ("Connect", "CONNECT"),
        ]:
            tk.Button(toolbar, text=label, command=lambda value=tool: self.set_tool(value)).pack(
                side=tk.LEFT, padx=2, pady=2
            )

        for gate in self.GATE_TOOLS:
            tk.Button(toolbar, text=gate, command=lambda value=gate: self.set_tool(value)).pack(
                side=tk.LEFT, padx=2, pady=2
            )

        tk.Button(toolbar, text="Run", command=self.run_simulation).pack(side=tk.LEFT, padx=10)
        tk.Button(toolbar, text="Reset", command=self.reset_simulation).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Help", command=self.show_help).pack(side=tk.RIGHT, padx=2)

        self.status = tk.Label(self.root, text="Seçili araç: INPUT", anchor="w")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        self.canvas = tk.Canvas(self.root, bg="white", width=1000, height=620)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<Double-Button-1>", self.canvas_double_click)

    def set_tool(self, tool: str) -> None:
        self.current_tool = tool
        self.connection_start = None
        self.status.config(text=f"Seçili araç: {tool}")

    def next_id(self, prefix: str) -> str:
        component_id = f"{prefix}{self.counter}"
        self.counter += 1
        return component_id

    def canvas_click(self, event: tk.Event) -> None:
        clicked_component_id = self.find_component_by_item(event.x, event.y)

        if self.current_tool == "CONNECT":
            self.handle_connection_click(clicked_component_id)
            return

        if self.current_tool == "INPUT":
            self.add_input(event.x, event.y)
        elif self.current_tool == "OUTPUT":
            self.add_output(event.x, event.y)
        elif self.current_tool in self.GATE_TOOLS:
            self.add_gate(self.current_tool, event.x, event.y)

    def canvas_double_click(self, event: tk.Event) -> None:
        component_id = self.find_component_by_item(event.x, event.y)
        if component_id is None:
            return

        component = self.components[component_id]
        if component.kind != "INPUT":
            self.rename_component(component_id)
            return

        component.value = 0 if component.value else 1
        self.circuit.set_input(component_id, component.value)
        self.redraw_component(component)

    def rename_component(self, component_id: str) -> None:
        new_label = simpledialog.askstring("Etiket", "Yeni etiket:", initialvalue=component_id)
        if new_label:
            self.canvas.itemconfig(self.components[component_id].canvas_items[-1], text=new_label)

    def add_input(self, x: int, y: int) -> None:
        component_id = self.next_id("IN")
        rect = self.canvas.create_rectangle(x - 35, y - 22, x + 35, y + 22, fill="#f5f5f5", outline="black")
        text = self.canvas.create_text(x, y, text=f"{component_id}=0", font=("Arial", 10, "bold"))
        component = VisualComponent(component_id, "INPUT", x, y, (rect, text), value=0)
        self.register_component(component)
        self.circuit.add_input(component_id, 0)

    def add_output(self, x: int, y: int) -> None:
        component_id = self.next_id("OUT")
        oval = self.canvas.create_oval(x - 32, y - 22, x + 32, y + 22, fill="#eeeeee", outline="black")
        text = self.canvas.create_text(x, y, text=f"{component_id}=?", font=("Arial", 10, "bold"))
        component = VisualComponent(component_id, "OUTPUT", x, y, (oval, text))
        self.register_component(component)
        self.circuit.add_output(component_id)

    def add_gate(self, gate_name: str, x: int, y: int) -> None:
        gate_type = GateType(gate_name)
        component_id = self.next_id("G")
        body = self.canvas.create_rectangle(x - 45, y - 28, x + 45, y + 28, fill="#dfefff", outline="black", width=2)
        gate_text = self.canvas.create_text(x, y - 7, text=gate_type.value, font=("Arial", 11, "bold"))
        id_text = self.canvas.create_text(x, y + 13, text=component_id, font=("Arial", 9))
        component = VisualComponent(component_id, "GATE", x, y, (body, gate_text, id_text), gate_type=gate_type)
        self.register_component(component)
        self.circuit.add_gate(component_id, gate_type)

    def register_component(self, component: VisualComponent) -> None:
        self.components[component.component_id] = component
        for item in component.canvas_items:
            self.item_to_component[item] = component.component_id

    def find_component_by_item(self, x: int, y: int) -> str | None:
        overlapping = self.canvas.find_overlapping(x, y, x, y)
        for item in reversed(overlapping):
            component_id = self.item_to_component.get(item)
            if component_id:
                return component_id
        return None

    def handle_connection_click(self, component_id: str | None) -> None:
        if component_id is None:
            self.status.config(text="Bağlantı için bir eleman seçmelisin.")
            return

        if self.connection_start is None:
            self.connection_start = component_id
            self.status.config(text=f"Bağlantı başlangıcı: {component_id}. Şimdi hedef elemanı seç.")
            return

        try:
            self.circuit.connect(self.connection_start, component_id)
            self.draw_connection(self.connection_start, component_id)
            self.status.config(text=f"Bağlantı eklendi: {self.connection_start} -> {component_id}")
        except ValueError as exc:
            messagebox.showwarning("Bağlantı hatası", str(exc))
        finally:
            self.connection_start = None

    def draw_connection(self, source_id: str, target_id: str) -> None:
        source = self.components[source_id]
        target = self.components[target_id]
        line = self.canvas.create_line(source.x, source.y, target.x, target.y, arrow=tk.LAST, width=2)
        self.connection_items.append(line)
        self.canvas.tag_lower(line)

    def run_simulation(self) -> None:
        try:
            outputs = self.circuit.evaluate_outputs()
        except (ValueError, KeyError) as exc:
            messagebox.showerror("Simülasyon hatası", str(exc))
            return

        for output_id, value in outputs.items():
            component = self.components[output_id]
            component.value = value
            self.redraw_component(component)
        self.status.config(text="Simülasyon tamamlandı.")

    def redraw_component(self, component: VisualComponent) -> None:
        if component.kind == "INPUT":
            fill = "#b6f2b6" if component.value else "#f5f5f5"
            self.canvas.itemconfig(component.canvas_items[0], fill=fill)
            self.canvas.itemconfig(component.canvas_items[1], text=f"{component.component_id}={component.value}")
        elif component.kind == "OUTPUT":
            fill = "#7CFC00" if component.value else "#eeeeee"
            self.canvas.itemconfig(component.canvas_items[0], fill=fill)
            self.canvas.itemconfig(component.canvas_items[1], text=f"{component.component_id}={component.value}")

    def reset_simulation(self) -> None:
        self.canvas.delete("all")
        self.circuit.clear()
        self.components.clear()
        self.item_to_component.clear()
        self.connection_items.clear()
        self.connection_start = None
        self.counter = 1
        self.status.config(text=f"Seçili araç: {self.current_tool}")

    def show_help(self) -> None:
        messagebox.showinfo(
            "Kullanım",
            "1) Üst menüden eleman veya kapı seç.\n"
            "2) Canvas'a tıklayarak eleman ekle.\n"
            "3) Connect ile önce kaynak, sonra hedef elemanı seç.\n"
            "4) Input elemanına çift tıklayarak 0/1 değerini değiştir.\n"
            "5) Run ile devreyi çalıştır.",
        )


def run_app() -> None:
    root = tk.Tk()
    LogicGateSimulator(root)
    root.mainloop()
