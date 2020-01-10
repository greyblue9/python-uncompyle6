#  Copyright (c) 2020 Rocky Bernstein

def testtrue(self, lhs, n, rule, ast, tokens, first, last):
    # FIXME: make this work for all versions
    if self.version < 3.7:
        return False
    if rule == ("testtrue", ("expr", "jmp_true")):
        pjit = tokens[min(last-1, n-2)]
        # If we have a backwards (looping) jump then this is
        # really a testfalse
        return (pjit == "POP_JUMP_IF_TRUE" and
                tokens[first].off2int() > pjit.attr)
    return False