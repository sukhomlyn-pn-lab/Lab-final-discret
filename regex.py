from __future__ import annotations
from abc import ABC, abstractmethod


class State(ABC):

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def check_self(self, char: str) -> bool:
        """
        function checks whether occured character is handled by current state
        """
        pass

    def check_next(self, next_char: str) -> State | Exception:
        for state in self.next_states:
            if state.check_self(next_char):
                return state
        raise NotImplementedError("rejected string")


class StartState(State):

    next_states: list[State] = []

    def __init__(self):
        self.next_states = []
        super().__init__()

    def check_self(self, char):
        return False


class TerminationState(State):

    next_states: list[State] = []

    def __init__(self):
        self.next_states = []

    def check_self(self, char: str) -> bool:
        return False


class DotState(State):
    """
    state for . character (any character accepted)
    """

    next_states: list[State] = []

    def __init__(self):
        self.next_states = []
        super().__init__()

    def check_self(self, char: str):
        return len(char) == 1


class AsciiState(State):
    """
    state for alphabet letters or numbers
    """

    next_states: list[State] = []
    curr_sym = ""

    def __init__(self, symbol: str) -> None:
        self.next_states = []
        self.curr_sym = symbol

    def check_self(self, curr_char: str) -> bool:
        return curr_char == self.curr_sym


class StarState(State):

    next_states: list[State] = []

    def __init__(self, checking_state: State):
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class PlusState(State):

    next_states: list[State] = []

    def __init__(self, checking_state: State):
        self.next_states = []
        self.checking_state = checking_state

    def check_self(self, char):
        return self.checking_state.check_self(char)


class RegexFSM:

    curr_state: State = StartState()

    def __init__(self, regex_expr: str) -> None:
        self.curr_state = StartState()
        grandparent = None
        prev_state = self.curr_state
        tmp_next_state = self.curr_state

        for char in regex_expr:
            if char == '*':
                new_state = StarState(tmp_next_state)
                new_state.next_states.append(new_state)
                if grandparent is not None and tmp_next_state in grandparent.next_states:
                    grandparent.next_states[grandparent.next_states.index(tmp_next_state)] = new_state
                prev_state = new_state

            elif char == '+':
                star = StarState(tmp_next_state)
                star.next_states.append(star)

                plus = PlusState(tmp_next_state)
                plus.next_states.append(star)

                if grandparent is not None and tmp_next_state in grandparent.next_states:
                    grandparent.next_states[grandparent.next_states.index(tmp_next_state)] = plus

                prev_state = star
                grandparent = star

            else:
                new_state = self.__init_next_state(char, prev_state, tmp_next_state)
                grandparent = prev_state
                prev_state.next_states.append(new_state)
                tmp_next_state = new_state
                prev_state = new_state

        prev_state.next_states.append(TerminationState())

    def __init_next_state(
        self, next_token: str, prev_state: State, tmp_next_state: State
    ) -> State:
        match next_token:
            case t if t == ".":
                return DotState()
            case t if t == "*":
                return StarState(tmp_next_state)
            case t if t == "+":
                return PlusState(tmp_next_state)
            case t if t.isascii():
                return AsciiState(next_token)
            case _:
                raise AttributeError("Character is not supported")

    def check_string(self, input_string: str) -> bool:
        current_states = set()
        stack = list(self.curr_state.next_states)
        visited = set()
        while stack:
            s = stack.pop()
            if id(s) in visited:
                continue
            visited.add(id(s))
            current_states.add(s)
            if isinstance(s, StarState):
                for nxt in s.next_states:
                    if nxt is not s:
                        stack.append(nxt)

        for char in input_string:
            next_states = set()
            for state in current_states:
                if state.check_self(char):
                    for nxt in state.next_states:
                        next_states.add(nxt)
                        if isinstance(nxt, StarState):
                            for nxt2 in nxt.next_states:
                                if nxt2 is not nxt:
                                    next_states.add(nxt2)
            if not next_states:
                return False
            current_states = next_states

        return any(isinstance(s, TerminationState) for s in current_states)


if __name__ == "__main__":
    regex_pattern = "a*4.+hi"
    regex_compiled = RegexFSM(regex_pattern)

    print(regex_compiled.check_string("aaaaaa4uhi"))  # True
    print(regex_compiled.check_string("4uhi"))        # True
    print(regex_compiled.check_string("meow"))        # False
    print(regex_compiled.check_string("aaa4ubfcdgjschhi")) # True
    print(regex_compiled.check_string("4ubfcdgjschi")) #True
