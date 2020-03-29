from copy import copy

from hdlConvertor.hdlAst._expr import HdlBuiltinFn
from hdlConvertor.hdlAst._statements import HdlStmWait, HdlStmBlock
from hdlConvertor.to.hdlUtils import Indent, iter_with_last
from hdlConvertor.to.verilog.expr import ToVerilog2005Expr


class ToVerilog2005Stm(ToVerilog2005Expr):
    ASSIGN_OPS = {
        HdlBuiltinFn.ASSIGN: '=',
        HdlBuiltinFn.PLUS_ASSIGN: '+=',
        HdlBuiltinFn.MINUS_ASSIGN: '-=',
        HdlBuiltinFn.MUL_ASSIGN: '*=',
        HdlBuiltinFn.DIV_ASSIGN: '/=',
        HdlBuiltinFn.MOD_ASSIGN: '%=',
        HdlBuiltinFn.AND_ASSIGN: '&=',
        HdlBuiltinFn.OR_ASSIGN: '|=',
        HdlBuiltinFn.XOR_ASSIGN: '^=',
        HdlBuiltinFn.SHIFT_LEFT_ASSIGN: '<<=',
        HdlBuiltinFn.SHIFT_RIGHT_ASSIGN: '>>=',
        HdlBuiltinFn.ARITH_SHIFT_LEFT_ASSIGN: '<<<=',
        HdlBuiltinFn.ARITH_SHIFT_RIGHT_ASSIGN: '>>>=',
    }

    def print_HdlStmProcess(self, proc, is_top=False):
        """
        :type proc: HdlStmProcess
        """
        sens = proc.sensitivity
        body = proc.body
        w = self.out.write
        skip_body = False
        if sens is None:
            if isinstance(body, HdlStmWait):
                skip_body = True
                wait = body
            elif (isinstance(body, HdlStmBlock)
                    and body.body
                    and isinstance(body.body[0], HdlStmWait)):
                wait = body.body[0]
                body = copy(body)
                body.body = body.body[1:]
            else:
                wait = None

            if wait is not None:
                if is_top:
                    w("always ")
                w("#")
                assert len(wait.val) == 1
                self.print_iHdlExpr(wait.val[0])
            else:
                assert is_top
                w("initial")
        else:
            if is_top:
                w("always ")
            w("@(")
            for last, item in iter_with_last(sens):
                self.print_iHdlExpr(item)
                if not last:
                    w(", ")
            w(")")

        # to prevent useless newline for empty always/time waits
        if skip_body:
            return True
        else:
            return self.print_iHdlStatement_in_statement(body)

    def print_iHdlStatement_in_statement(self, stm):
        """
        Print statement which is body of other statement
        e.g. body of process, branch of if-then-else or case of case stememnt
        """
        w = self.out.write
        if isinstance(stm, HdlStmBlock):
            if len(stm.body) == 1:
                stm = stm.body[0]
            else:
                w(" ")
                return self.print_HdlStmBlock(stm)

        w("\n")
        with Indent(self.out):
            return self.print_iHdlStatement(stm)

    def print_HdlStmBlock(self, stm):
        """
        :type stm: HdlStmBlock
        """
        w = self.out.write

        w("begin\n")
        with Indent(self.out):
            for s in stm.body:
                need_semi = self.print_iHdlStatement(s)
                if need_semi:
                    w(";\n")
                else:
                    w("\n")
        w("end")
        return False

    def print_HdlStmIf(self, stm):
        """
        :type stm: HdlStmIf
        """
        w = self.out.write
        c = stm.cond
        ifTrue = stm.if_true
        ifFalse = stm.if_false

        w("if (")
        self.print_iHdlExpr(c)
        w(")")
        need_semi = self.print_iHdlStatement_in_statement(ifTrue)

        for cond, stms in stm.elifs:
            if need_semi:
                w(";\n")
            else:
                w(" ")
            w("else if (")
            self.print_iHdlExpr(cond)
            w(")")
            need_semi = self.print_iHdlStatement_in_statement(stms)

        if ifFalse is not None:
            if need_semi:
                w(";\n")
            else:
                w(" ")
            w("else")
            need_semi = self.print_iHdlStatement_in_statement(ifFalse)
        if need_semi:
            w(";")

    def print_HdlStmAssign(self, a, is_top=False):
        """
        :type a: HdlStmAssign
        :return: True if requires ;\n after end
        """
        s = a.src
        d = a.dst
        w = self.out.write
        if is_top:
            w("assign ")
            self.print_iHdlExpr(d)
            w(" = ")
        else:
            self.print_iHdlExpr(d)
            if a.is_blocking:
                w(" = ")
            else:
                w(" <= ")

        if a.time_delay is not None:
            w("#")
            self.print_iHdlExpr(a.time_delay)
            w(" ")
        if a.event_delay is not None:
            w("@")
            if len(a.event_delay) > 1:
                w("(")
            for is_last, e in iter_with_last(a.event_delay):
                self.print_iHdlExpr(e)
                if not is_last:
                    w(", ")
            if len(a.event_delay) > 1:
                w(")")
            w(" ")

        self.print_iHdlExpr(s)
        return True

    def print_HdlStmCase(self, cstm):
        """
        :type cstm: HdlStmCase

        :return: True if requires ;\n after end
        """
        w = self.out.write
        w("case(")
        self.print_iHdlExpr(cstm.switch_on)
        w(")\n")
        with Indent(self.out):
            cases = cstm.cases
            for k, stms in cases:
                self.print_iHdlExpr(k)
                w(":")
                need_semi = self.print_iHdlStatement_in_statement(stms)
                if need_semi:
                    w(";\n")
                else:
                    w("\n")
            defal = cstm.default
            if defal is not None:
                w("default:")
                need_semi = self.print_iHdlStatement_in_statement(defal)
                if need_semi:
                    w(";\n")
                else:
                    w("\n")
        w("endcase")
        return False

    def print_HdlStmWait(self, o):
        """
        :type o: HdlStmWait

        :return: True if requires ;\n after end
        """
        self.print_doc(o)
        w = self.out.write
        w("#")
        assert len(o.val) == 1
        self.print_iHdlExpr(o.val[0])
        return True

    def print_HdlStmFor(self, o):
        """
        :type o: HdlStmFor

        :return: True if requires ;\n after end
        """
        w = self.out.write
        w("for (")
        if isinstance(o.init, HdlStmBlock):
            init_stms = o.init.body
        else:
            init_stms = [o.init, ]

        for is_last, stm in iter_with_last(init_stms):
            self.print_iHdlStatement(stm)
            if not is_last:
                w(", ")
        w("; ")
        self.print_iHdlExpr(o.cond)
        w("; ")
        if isinstance(o.init, HdlStmBlock):
            step_stms = o.step.body
        else:
            step_stms = [o.step, ]

        for is_last, stm in iter_with_last(step_stms):
            self.print_iHdlStatement(stm)
            if not is_last:
                w(", ")
        w(")")
        return self.print_iHdlStatement_in_statement(o.body)

    def print_HdlStmForIn(self, o):
        """
        :type o: HdlStmForIn
        :return: True if requires ;\n after end
        """
        raise NotImplementedError()

    def print_HdlStmWhile(self, o):
        """
        :type o: HdlStmWhile
        :return: True if requires ;\n after end
        """
        w = self.out.write
        w("while (")
        self.print_iHdlExpr(o.cond)
        w(") ")
        return self.print_HdlStmBlock(o.body, True)