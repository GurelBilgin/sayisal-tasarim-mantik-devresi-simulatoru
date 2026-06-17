import unittest

from sayisal_tasarim_simulatoru.logic import Circuit, GateType, LogicGate, evaluate_gate


class TestLogicGates(unittest.TestCase):
    def test_and_gate(self):
        self.assertEqual(evaluate_gate(GateType.AND, [1, 1]), 1)
        self.assertEqual(evaluate_gate(GateType.AND, [1, 0]), 0)
        self.assertEqual(evaluate_gate(GateType.AND, [1, 1, 1]), 1)

    def test_or_gate(self):
        self.assertEqual(evaluate_gate(GateType.OR, [0, 0]), 0)
        self.assertEqual(evaluate_gate(GateType.OR, [0, 1]), 1)

    def test_not_gate(self):
        self.assertEqual(evaluate_gate(GateType.NOT, [0]), 1)
        self.assertEqual(evaluate_gate(GateType.NOT, [1]), 0)

    def test_buffer_gate(self):
        self.assertEqual(evaluate_gate(GateType.BUFFER, [0]), 0)
        self.assertEqual(evaluate_gate(GateType.BUFFER, [1]), 1)

    def test_nand_and_nor_gate(self):
        self.assertEqual(evaluate_gate(GateType.NAND, [1, 1]), 0)
        self.assertEqual(evaluate_gate(GateType.NAND, [1, 0]), 1)
        self.assertEqual(evaluate_gate(GateType.NOR, [0, 0]), 1)
        self.assertEqual(evaluate_gate(GateType.NOR, [1, 0]), 0)

    def test_xor_and_xnor_gate(self):
        self.assertEqual(evaluate_gate(GateType.XOR, [0, 0]), 0)
        self.assertEqual(evaluate_gate(GateType.XOR, [1, 0]), 1)
        self.assertEqual(evaluate_gate(GateType.XOR, [1, 1]), 0)
        self.assertEqual(evaluate_gate(GateType.XNOR, [1, 1]), 1)
        self.assertEqual(evaluate_gate(GateType.XNOR, [1, 0]), 0)

    def test_not_gate_requires_single_input(self):
        with self.assertRaises(ValueError):
            evaluate_gate(GateType.NOT, [1, 0])

    def test_logic_gate_class(self):
        gate = LogicGate("AND", "G1")
        self.assertEqual(gate.evaluate([1, 1]), 1)
        self.assertEqual(gate.evaluate([0, 1]), 0)


class TestCircuit(unittest.TestCase):
    def test_simple_and_circuit(self):
        circuit = Circuit()
        circuit.add_input("A", 1)
        circuit.add_input("B", 1)
        circuit.add_gate("G1", GateType.AND)
        circuit.add_output("OUT")
        circuit.connect("A", "G1")
        circuit.connect("B", "G1")
        circuit.connect("G1", "OUT")

        self.assertEqual(circuit.evaluate_outputs(), {"OUT": 1})

        circuit.set_input("B", 0)
        self.assertEqual(circuit.evaluate_outputs(), {"OUT": 0})

    def test_nested_circuit(self):
        circuit = Circuit()
        circuit.add_input("A", 1)
        circuit.add_input("B", 0)
        circuit.add_gate("N1", GateType.NOT)
        circuit.add_gate("AND1", GateType.AND)
        circuit.add_output("OUT")

        circuit.connect("B", "N1")
        circuit.connect("A", "AND1")
        circuit.connect("N1", "AND1")
        circuit.connect("AND1", "OUT")

        self.assertEqual(circuit.evaluate_outputs(), {"OUT": 1})

    def test_missing_connection_raises_error(self):
        circuit = Circuit()
        circuit.add_gate("G1", GateType.AND)
        circuit.add_output("OUT")
        circuit.connect("G1", "OUT")

        with self.assertRaises(ValueError):
            circuit.evaluate_outputs()


if __name__ == "__main__":
    unittest.main()
