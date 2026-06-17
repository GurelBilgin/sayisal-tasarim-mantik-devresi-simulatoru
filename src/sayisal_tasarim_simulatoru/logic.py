"""Mantık kapıları ve devre hesaplama motoru.

Bu modül GUI'den bağımsızdır. Bu sayede mantık kapıları ve bağlantılı devreler
birim testlerle kolayca doğrulanabilir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from functools import reduce
from operator import xor
from typing import Dict, Iterable, List, Tuple


class GateType(StrEnum):
    """Desteklenen mantık kapısı türleri."""

    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    BUFFER = "BUFFER"
    NAND = "NAND"
    NOR = "NOR"
    XOR = "XOR"
    XNOR = "XNOR"


Signal = int
ComponentId = str
Connection = Tuple[ComponentId, ComponentId]


def _normalize_inputs(inputs: Iterable[int | bool]) -> List[int]:
    values = [1 if bool(value) else 0 for value in inputs]
    if not values:
        raise ValueError("En az bir giriş değeri verilmelidir.")
    return values


def evaluate_gate(gate_type: GateType | str, inputs: Iterable[int | bool]) -> int:
    """Verilen mantık kapısının çıkış değerini hesaplar.

    Parameters
    ----------
    gate_type:
        Mantık kapısı türü.
    inputs:
        0/1 veya bool değerlerinden oluşan giriş listesi.

    Returns
    -------
    int
        Hesaplanan çıkış değeri. Sonuç her zaman 0 veya 1'dir.
    """

    gate = GateType(str(gate_type).upper())
    values = _normalize_inputs(inputs)

    if gate in {GateType.NOT, GateType.BUFFER} and len(values) != 1:
        raise ValueError(f"{gate.value} kapısı tam olarak 1 giriş almalıdır.")

    if gate == GateType.AND:
        return int(all(values))
    if gate == GateType.OR:
        return int(any(values))
    if gate == GateType.NOT:
        return int(not values[0])
    if gate == GateType.BUFFER:
        return int(values[0])
    if gate == GateType.NAND:
        return int(not all(values))
    if gate == GateType.NOR:
        return int(not any(values))
    if gate == GateType.XOR:
        return int(reduce(xor, values, 0))
    if gate == GateType.XNOR:
        return int(not reduce(xor, values, 0))

    raise ValueError(f"Desteklenmeyen kapı türü: {gate_type}")


@dataclass(slots=True)
class LogicGate:
    """Devre içinde kullanılabilecek mantık kapısı."""

    gate_type: GateType | str
    component_id: str
    label: str = ""

    def __post_init__(self) -> None:
        self.gate_type = GateType(str(self.gate_type).upper())
        if not self.label:
            self.label = self.gate_type.value

    def evaluate(self, inputs: Iterable[int | bool]) -> int:
        return evaluate_gate(self.gate_type, inputs)


@dataclass
class Circuit:
    """Basit yönlü bağlantılardan oluşan mantık devresi."""

    inputs: Dict[ComponentId, int] = field(default_factory=dict)
    gates: Dict[ComponentId, LogicGate] = field(default_factory=dict)
    outputs: Dict[ComponentId, ComponentId | None] = field(default_factory=dict)
    connections: List[Connection] = field(default_factory=list)

    def add_input(self, component_id: ComponentId, value: int | bool = 0) -> None:
        self.inputs[component_id] = 1 if bool(value) else 0

    def set_input(self, component_id: ComponentId, value: int | bool) -> None:
        if component_id not in self.inputs:
            raise KeyError(f"Giriş elemanı bulunamadı: {component_id}")
        self.inputs[component_id] = 1 if bool(value) else 0

    def add_gate(self, component_id: ComponentId, gate_type: GateType | str) -> None:
        self.gates[component_id] = LogicGate(gate_type, component_id)

    def add_output(self, component_id: ComponentId) -> None:
        self.outputs[component_id] = None

    def connect(self, source_id: ComponentId, target_id: ComponentId) -> None:
        if source_id == target_id:
            raise ValueError("Bir eleman kendisine bağlanamaz.")
        self.connections.append((source_id, target_id))
        if target_id in self.outputs:
            self.outputs[target_id] = source_id

    def incoming_sources(self, target_id: ComponentId) -> List[ComponentId]:
        return [source for source, target in self.connections if target == target_id]

    def evaluate_component(self, component_id: ComponentId, cache: Dict[ComponentId, int] | None = None) -> int:
        if cache is None:
            cache = {}

        if component_id in cache:
            return cache[component_id]

        if component_id in self.inputs:
            cache[component_id] = self.inputs[component_id]
            return cache[component_id]

        if component_id in self.gates:
            sources = self.incoming_sources(component_id)
            if not sources:
                raise ValueError(f"{component_id} kapısına giriş bağlantısı yapılmamış.")
            source_values = [self.evaluate_component(source, cache) for source in sources]
            cache[component_id] = self.gates[component_id].evaluate(source_values)
            return cache[component_id]

        if component_id in self.outputs:
            source = self.outputs[component_id]
            if source is None:
                sources = self.incoming_sources(component_id)
                if not sources:
                    raise ValueError(f"{component_id} çıkışına bağlantı yapılmamış.")
                source = sources[-1]
            cache[component_id] = self.evaluate_component(source, cache)
            return cache[component_id]

        raise KeyError(f"Devre elemanı bulunamadı: {component_id}")

    def evaluate_outputs(self) -> Dict[ComponentId, int]:
        cache: Dict[ComponentId, int] = {}
        return {output_id: self.evaluate_component(output_id, cache) for output_id in self.outputs}

    def clear(self) -> None:
        self.inputs.clear()
        self.gates.clear()
        self.outputs.clear()
        self.connections.clear()
