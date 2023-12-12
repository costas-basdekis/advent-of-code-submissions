#!/usr/bin/env python3
from abc import ABC
from dataclasses import dataclass
import re
from enum import Enum
from functools import cached_property
from itertools import count
from typing import ClassVar, Dict, Generic, Iterable, List, Optional, Tuple, Type, Union, TypeVar

from aox.challenge import Debugger
from utils import BaseChallenge, get_type_argument_class, Cls, Self, PolymorphicParser, cached_classmethod


class Challenge(BaseChallenge):
    def solve(self, _input: str, debugger: Debugger) -> Union[str, int]:
        """
        >>> Challenge().default_solve()
        919383692
        """
        return Network.from_text(_input).get_message_product_after_clicks(1000, debugger=debugger)


@dataclass
class Network:
    template: "NetworkTemplate"
    modules_by_name: Dict[str, "Module"]
    message_queue: List["Message"]
    processed_messages: List["Message"]

    @classmethod
    def from_text(cls, text: str) -> "Network":
        """
        >>> print(Network.from_text('''
        ...     broadcaster -> a, b, c
        ...     %a -> b
        ...     %b -> c
        ...     %c -> inv
        ...     &inv -> a
        ... '''))
        broadcaster
        a: State.Low
        b: State.Low
        c: State.Low
        inv: c: State.Low
        """
        return cls.from_network_template(NetworkTemplate.from_text(text))

    @classmethod
    def from_network_template(cls, network_template: "NetworkTemplate") -> "Network":
        return cls(template=network_template, modules_by_name={
            module_template.module_name: Module.from_module(module_template)
            for module_template in network_template.module_templates_by_name.values()
        }, message_queue=[], processed_messages=[])

    def __str__(self) -> str:
        return "\n".join(map(str, self.modules_by_name.values()))

    def restart(self) -> "Network":
        for module in self.modules_by_name.values():
            module.restart()
        self.message_queue = []
        self.processed_messages = []
        return self

    def clear_processed_messages(self) -> "Network":
        self.processed_messages = []
        return self

    def is_in_default_state(self) -> bool:
        return all(
            module.is_in_default_state()
            for module in self.modules_by_name.values()
        )

    def get_snapshot(self) -> str:
        return "|".join(module.get_snapshot() for module in self.modules_by_name.values())

    def press_button(self) -> "Network":
        self.message_queue.append(Message("button", "broadcaster", State.Low))
        return self

    def get_message_product_after_clicks(self, clicks: int, debugger: Debugger = Debugger(enabled=False)) -> int:
        """
        >>> Network.from_text('''
        ...     broadcaster -> a, b, c
        ...     %a -> b
        ...     %b -> c
        ...     %c -> inv
        ...     &inv -> a
        ... ''').get_message_product_after_clicks(1000)
        32000000
        >>> Network.from_text('''
        ...     broadcaster -> a
        ...     %a -> inv, con
        ...     &inv -> b
        ...     %b -> con
        ...     &con -> output
        ... ''').get_message_product_after_clicks(1000)
        11687500
        """
        cycle = self.find_cycle(max_clicks=clicks, debugger=debugger)
        message_counts_by_snapshot, snapshot_history, _ = cycle
        prefix_count, cycle_length, cycle_count, suffix_count = self.find_cycle_numbers(clicks, cycle=cycle)
        def add_counts(left: Tuple[int, int], right: Tuple[int, int]) -> Tuple[int, int]:
            left_lows, left_highs = left
            right_lows, right_highs = right
            return left_lows + right_lows, left_highs + right_highs
        def sum_counts(counts_list: Iterable[Tuple[int, int]]) -> int:
            total = (0, 0)
            for counts in counts_list:
                total = add_counts(total, counts)
            lows, highs = total
            return lows * highs
        prefix_sum = sum_counts(
            message_counts_by_snapshot[snapshot]
            for snapshot in snapshot_history[:prefix_count]
        )
        cycle_sum = cycle_count * cycle_count * sum_counts(
            message_counts_by_snapshot[snapshot]
            for snapshot in snapshot_history[prefix_count:prefix_count + cycle_count]
        )
        suffix_sum = sum_counts(
            message_counts_by_snapshot[snapshot]
            for snapshot in snapshot_history[prefix_count:prefix_count + suffix_count]
        )
        return prefix_sum + cycle_sum + suffix_sum

    def find_cycle_numbers(self, clicks: int, cycle: Optional[Tuple[Dict[str, Tuple[int, int]], List[str], Optional[int]]] = None) -> Tuple[int, int, int, int]:
        """
        >>> Network.from_text('''
        ...     broadcaster -> a, b, c
        ...     %a -> b
        ...     %b -> c
        ...     %c -> inv
        ...     &inv -> a
        ... ''').find_cycle_numbers(1000)
        (0, 1, 1000, 0)
        >>> Network.from_text('''
        ...     broadcaster -> a
        ...     %a -> inv, con
        ...     &inv -> b
        ...     %b -> con
        ...     &con -> output
        ... ''').find_cycle_numbers(1000)
        (0, 4, 250, 0)
        """
        if cycle is None:
            cycle = self.find_cycle()
        _, snapshot_history, final_index = cycle
        if final_index is not None:
            prefix_count = final_index
            cycle_length = len(snapshot_history) - final_index
            cycle_count = (clicks - prefix_count) // cycle_length
            suffix_count = (clicks - prefix_count) % cycle_length
        else:
            prefix_count = min(len(snapshot_history), clicks)
            cycle_length = 0
            cycle_count = 0
            suffix_count = 0
        return prefix_count, cycle_length, cycle_count, suffix_count

    def find_cycle(self, max_clicks: int = -1, debugger: Debugger = Debugger(enabled=False)) -> Tuple[Dict[str, Tuple[int, int]], List[str], Optional[int]]:
        """
        >>> Network.from_text('''
        ...     broadcaster -> a, b, c
        ...     %a -> b
        ...     %b -> c
        ...     %c -> inv
        ...     &inv -> a
        ... ''').find_cycle()
        ({'broadcaster|a:low|b:low|c:low|inv:c=low': (8, 4)}, ['broadcaster|a:low|b:low|c:low|inv:c=low'], 0)
        >>> Network.from_text('''
        ...     broadcaster -> a
        ...     %a -> inv, con
        ...     &inv -> b
        ...     %b -> con
        ...     &con -> output
        ... ''').find_cycle()
        ({'broadcaster|a:low|inv:a=low|b:low|con:a=low,b=low|output': (4, 4),
            'broadcaster|a:high|inv:a=high|b:high|con:a=high,b=high|output': (4, 2),
            'broadcaster|a:low|inv:a=low|b:high|con:a=low,b=high|output': (5, 3),
            'broadcaster|a:high|inv:a=high|b:low|con:a=high,b=low|output': (4, 2)},
            ['broadcaster|a:low|inv:a=low|b:low|con:a=low,b=low|output',
            'broadcaster|a:high|inv:a=high|b:high|con:a=high,b=high|output',
            'broadcaster|a:low|inv:a=low|b:high|con:a=low,b=high|output',
            'broadcaster|a:high|inv:a=high|b:low|con:a=high,b=low|output'],
            0)
        """
        message_counts_by_snapshot = {}
        snapshot_history = [self.get_snapshot()]
        after_snapshot = self.get_snapshot()
        if max_clicks < 0:
            click_counter = count()
        else:
            click_counter = range(max_clicks + 1)
        for _ in debugger.stepping(click_counter):
            self.clear_processed_messages().press_button().process_queue()
            before_snapshot, after_snapshot = after_snapshot, self.get_snapshot()
            message_counts_by_snapshot[before_snapshot] = self.get_message_counts()
            if after_snapshot in message_counts_by_snapshot:
                break
            snapshot_history.append(after_snapshot)
            if debugger.should_report():
                debugger.default_report_if(f"Seen {len(message_counts_by_snapshot)} snapshots")
        else:
            after_snapshot = ""
        return message_counts_by_snapshot, snapshot_history, snapshot_history.index(after_snapshot) if after_snapshot else None

    def process_queue(self) -> "Network":
        """
        >>> _network = Network.from_text('''
        ...     broadcaster -> a, b, c
        ...     %a -> b
        ...     %b -> c
        ...     %c -> inv
        ...     &inv -> a
        ... ''')
        >>> print(_network.press_button().process_queue())
        broadcaster
        a: State.Low
        b: State.Low
        c: State.Low
        inv: c: State.Low
        >>> print("\\n".join(map(str, _network.processed_messages)))
        button -low-> broadcaster
        broadcaster -low-> a
        broadcaster -low-> b
        broadcaster -low-> c
        a -high-> b
        b -high-> c
        c -high-> inv
        inv -low-> a
        a -low-> b
        b -low-> c
        c -low-> inv
        inv -high-> a
        >>> _network = Network.from_text('''
        ...     broadcaster -> a
        ...     %a -> inv, con
        ...     &inv -> b
        ...     %b -> con
        ...     &con -> output
        ... ''')
        >>> print(_network.press_button().process_queue())
        broadcaster
        a: State.High
        inv: a: State.High
        b: State.High
        con: a: State.High, b: State.High
        output
        >>> _network.get_snapshot()
        'broadcaster|a:high|inv:a=high|b:high|con:a=high,b=high|output'
        >>> print("\\n".join(map(str, _network.processed_messages)))
        button -low-> broadcaster
        broadcaster -low-> a
        a -high-> inv
        a -high-> con
        inv -low-> b
        con -high-> output
        b -high-> con
        con -low-> output
        >>> print(_network.clear_processed_messages().press_button().process_queue())
        broadcaster
        a: State.Low
        inv: a: State.Low
        b: State.High
        con: a: State.Low, b: State.High
        output
        >>> print("\\n".join(map(str, _network.processed_messages)))
        button -low-> broadcaster
        broadcaster -low-> a
        a -low-> inv
        a -low-> con
        inv -high-> b
        con -high-> output
        >>> print(_network.clear_processed_messages().press_button().process_queue())
        broadcaster
        a: State.High
        inv: a: State.High
        b: State.Low
        con: a: State.High, b: State.Low
        output
        >>> print("\\n".join(map(str, _network.processed_messages)))
        button -low-> broadcaster
        broadcaster -low-> a
        a -high-> inv
        a -high-> con
        inv -low-> b
        con -low-> output
        b -low-> con
        con -high-> output
        >>> print(_network.clear_processed_messages().press_button().process_queue())
        broadcaster
        a: State.Low
        inv: a: State.Low
        b: State.Low
        con: a: State.Low, b: State.Low
        output
        >>> _network.get_snapshot()
        'broadcaster|a:low|inv:a=low|b:low|con:a=low,b=low|output'
        >>> print("\\n".join(map(str, _network.processed_messages)))
        button -low-> broadcaster
        broadcaster -low-> a
        a -low-> inv
        a -low-> con
        inv -high-> b
        con -high-> output
        >>> _network.is_in_default_state()
        True
        """
        while self.message_queue:
            self.process_next_message()
        return self

    def process_next_message(self) -> "Network":
        if not self.message_queue:
            return self
        message = self.message_queue.pop(0)
        messages = self.modules_by_name[message.target].receive_message(message)
        self.message_queue.extend(messages)
        self.processed_messages.append(message)
        return self

    def get_message_counts(self) -> Tuple[int, int]:
        """
        >>> Network.from_text('''
        ...     broadcaster -> a, b, c
        ...     %a -> b
        ...     %b -> c
        ...     %c -> inv
        ...     &inv -> a
        ... ''').press_button().process_queue().get_message_counts()
        (8, 4)
        """
        low_counts, high_counts = 0, 0
        for message in self.processed_messages:
            if message.state == State.Low:
                low_counts += 1
            else:
                high_counts += 1
        return low_counts, high_counts


@dataclass
class Message:
    source: str
    target: str
    state: "State"

    def __str__(self) -> str:
        return f"{self.source} -{self.state.value}-> {self.target}"


@dataclass
class NetworkTemplate:
    module_templates_by_name: Dict[str, "ModuleTemplate"]

    @classmethod
    def from_text(cls, text: str) -> "NetworkTemplate":
        module_templates_by_name: Dict[str, ModuleTemplate] = {
            module_template.module_name: module_template
            for module_template in map(ModuleTemplate.parse, map(str.strip, text.strip().splitlines()))
        }
        input_names_by_name: Dict[str, List[str]] = {
            module_template_name: []
            for module_template_name in module_templates_by_name
        }
        for module_template in list(module_templates_by_name.values()):
            for output_name in module_template.output_names:
                if output_name not in input_names_by_name:
                    new_module_template = CopierModuleTemplate.from_name(output_name)
                    module_templates_by_name[output_name] = new_module_template
                    input_names_by_name[output_name] = []
                input_names_by_name[output_name].append(module_template.module_name)
        for name, input_names in input_names_by_name.items():
            module_templates_by_name[name] = module_templates_by_name[name].set_input_names(input_names)
        return cls(module_templates_by_name=module_templates_by_name)

    def create(self) -> "Network":
        return Network.from_network_template(self)


class State(Enum):
    Low = "low"
    High = "high"

    @classmethod
    @cached_classmethod
    def get_opposite_map(cls) -> Dict["State", "State"]:
        return {
            State.Low: State.High,
            State.High: State.Low,
        }

    @cached_property
    def opposite(self) -> "State":
        return self.get_opposite_map()[self]


@dataclass
class ModuleTemplate(PolymorphicParser, ABC, root=True):
    module_name: str
    input_names: List[str]
    output_names: List[str]

    re_parse: ClassVar[re.Pattern] = re.compile(r"^(\w+) -> ([\w, ]+)$")

    @classmethod
    def try_parse_generic(cls: Cls["ModuleTemplate"], prefix: str, text: str) -> Optional[Tuple[str, List[str]]]:
        text = text.strip()
        if not text.startswith(prefix):
            return None
        match = cls.re_parse.match(text[len(prefix):])
        if not match:
            raise Exception(f"Could not parse {text} for {cls.__name__}")
        name, output_names_str = match.groups()
        return name, output_names_str.split(", ")

    def set_input_names(self: Self["ModuleTemplate"], input_names: List[str]) -> Self["ModuleTemplate"]:
        raise NotImplementedError()


@ModuleTemplate.register
@dataclass
class FlipFlopModuleTemplate(ModuleTemplate):
    name = "flip-flop"

    @classmethod
    def try_parse(cls, text: str) -> Optional["FlipFlopModuleTemplate"]:
        """
        >>> FlipFlopModuleTemplate.try_parse("%d -> a, b, c")
        FlipFlopModuleTemplate(module_name='d', input_names=[], output_names=['a', 'b', 'c'])
        """
        result = cls.try_parse_generic("%", text)
        if not result:
            return None
        name, output_names = result
        return cls(module_name=name, input_names=[], output_names=output_names)

    def set_input_names(self, input_names: List[str]) -> "FlipFlopModuleTemplate":
        cls = type(self)
        return cls(module_name=self.module_name, input_names=input_names, output_names=self.output_names)


@ModuleTemplate.register
@dataclass
class ConjunctionModuleTemplate(ModuleTemplate):
    name = "conjunction"

    @classmethod
    def try_parse(cls, text: str) -> Optional["ConjunctionModuleTemplate"]:
        """
        >>> ConjunctionModuleTemplate.try_parse("&d -> a, b, c")
        ConjunctionModuleTemplate(module_name='d', input_names=[], output_names=['a', 'b', 'c'])
        """
        result = cls.try_parse_generic("&", text)
        if not result:
            return None
        name, output_names = result
        return cls(module_name=name, input_names=[], output_names=output_names)

    def set_input_names(self, input_names: List[str]) -> "ConjunctionModuleTemplate":
        cls = type(self)
        return cls(module_name=self.module_name, input_names=input_names, output_names=self.output_names)


@ModuleTemplate.register
@dataclass
class CopierModuleTemplate(ModuleTemplate):
    name = "copier"

    @classmethod
    def try_parse(cls, text: str) -> Optional["CopierModuleTemplate"]:
        """
        >>> CopierModuleTemplate.try_parse("broadcaster -> a, b, c")
        CopierModuleTemplate(module_name='broadcaster', input_names=[], output_names=['a', 'b', 'c'])
        """
        result = cls.try_parse_generic("", text)
        if not result:
            return None
        name, output_names = result
        return cls(module_name=name, input_names=[], output_names=output_names)

    @classmethod
    def from_name(cls, module_name: str) -> "CopierModuleTemplate":
        return cls(module_name=module_name, input_names=[], output_names=[])

    def set_input_names(self, input_names: List[str]) -> "CopierModuleTemplate":
        cls = type(self)
        return cls(module_name=self.module_name, input_names=input_names, output_names=self.output_names)


ModuleTemplateT = TypeVar("ModuleTemplateT", bound=ModuleTemplate)


@dataclass
class Module(Generic[ModuleTemplateT], ABC):
    template: ModuleTemplateT

    module_classes_by_template_class: ClassVar[Dict[Type[ModuleTemplate], Type["Module"]]] = {}

    @classmethod
    def register(cls, module_class: Type["Module"]) -> Type["Module"]:
        module_template_class = get_type_argument_class(module_class, ModuleTemplateT)
        cls.module_classes_by_template_class[module_template_class] = module_class
        return module_class

    @classmethod
    def from_module(cls, module_template: ModuleTemplateT) -> "Module":
        return cls.module_classes_by_template_class[type(module_template)].initialise(module_template)

    @classmethod
    def initialise(cls, module_template: ModuleTemplateT) -> "Module":
        raise NotImplementedError()

    def receive_message(self, message: Message) -> List[Message]:
        raise NotImplementedError()

    def broadcast_message(self, state: State) -> List[Message]:
        return [
            Message(source=self.template.module_name, target=output_name, state=state)
            for output_name in self.template.output_names
        ]

    def restart(self):
        raise NotImplementedError()

    def is_in_default_state(self) -> bool:
        raise NotImplementedError()

    def get_snapshot(self) -> str:
        raise NotImplementedError()


@Module.register
@dataclass
class CopierModule(Module[CopierModuleTemplate]):
    @classmethod
    def initialise(cls, module_template: ModuleTemplate) -> "CopierModule":
        return cls(template=module_template)

    def __str__(self) -> str:
        return f"{self.template.module_name}"

    def receive_message(self, message: Message) -> List[Message]:
        return self.broadcast_message(message.state)

    def restart(self):
        pass

    def is_in_default_state(self) -> bool:
        return True

    def get_snapshot(self) -> str:
        return f"{self.template.module_name}"


@Module.register
@dataclass
class FlipFlopModule(Module[FlipFlopModuleTemplate]):
    state: State

    @classmethod
    def initialise(cls, module_template: ModuleTemplate) -> "FlipFlopModule":
        return cls(template=module_template, state=State.Low)

    def __str__(self) -> str:
        return f"{self.template.module_name}: {self.state}"

    def receive_message(self, message: Message) -> List[Message]:
        if message.state == State.High:
            return []
        self.state = self.state.opposite
        return self.broadcast_message(self.state)

    def restart(self):
        self.state = State.Low

    def is_in_default_state(self) -> bool:
        return self.state == State.Low

    def get_snapshot(self) -> str:
        return f"{self.template.module_name}:{self.state.value}"


@Module.register
@dataclass
class ConjunctionModule(Module[ConjunctionModuleTemplate]):
    inputs_state: Dict[str, State]

    @classmethod
    def initialise(cls, module_template: ModuleTemplate) -> "ConjunctionModule":
        return cls(template=module_template, inputs_state={
            input_name: State.Low
            for input_name in module_template.input_names
        })

    def __str__(self) -> str:
        return f"{self.template.module_name}: {', '.join(f'{input_name}: {state}' for input_name, state in sorted(self.inputs_state.items()))}"

    def receive_message(self, message: Message) -> List[Message]:
        self.inputs_state[message.source] = message.state
        all_high = all(
            state == State.High
            for state in self.inputs_state.values()
        )
        return self.broadcast_message(State.Low if all_high else State.High)

    def restart(self):
        self.inputs_state.update({
            input_name: State.Low
            for input_name in self.inputs_state
        })

    def is_in_default_state(self) -> bool:
        return all(
            state == State.Low
            for state in self.inputs_state.values()
        )

    def get_snapshot(self) -> str:
        return (
            f"{self.template.module_name}:"
            f"{','.join(f'{input_name}={state.value}' for input_name, state in self.inputs_state.items())}"
        )


Challenge.main()
challenge = Challenge()
