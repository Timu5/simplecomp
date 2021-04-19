from llvmlite import ir
from antlr4 import *
from CalcLexer import CalcLexer
from CalcVisitor import CalcVisitor
from CalcParser import CalcParser
from random import randint


class Codegen(CalcVisitor):

    def __init__(self):
        self.builder = None
        self.module = None
        self.printf = None
        self.locals = {}

    def root(self, node):
        self.module = ir.Module()

        func_type = ir.FunctionType(ir.IntType(32), [], False)
        base_func = ir.Function(self.module, func_type, name="main")
        block = base_func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

        voidptr_ty = ir.IntType(8).as_pointer()
        printf_ty = ir.FunctionType(ir.IntType(32), [voidptr_ty], var_arg=True)
        printf = ir.Function(self.module, printf_ty, name="printf")
        self.printf = printf

        self.visit(node)

        self.builder.ret(ir.Constant(ir.IntType(32), 0))

        return self.module

    def visitNumber(self, ctx: CalcParser.NumberContext):
        return ir.Constant(ir.IntType(32), int(ctx.getText()))

    def visitFloat(self, ctx: CalcParser.FloatContext):
        return ir.Constant(ir.DoubleType(), float(ctx.getText()))

    def visitVar(self, ctx: CalcParser.VarContext):
        name = ctx.getText()
        if not name in self.locals:
            raise Exception("missing variable")
        var = self.locals[name]
        return self.builder.load(var)

    def visitBinary(self, ctx: CalcParser.BinaryContext):
        op = ctx.op.type
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)

        if left.type != right.type:
            if isinstance(left.type, ir.IntType) and isinstance(right.type, ir.DoubleType):
                left = self.builder.uitofp(left, ir.DoubleType())
            elif isinstance(right.type, ir.IntType) and isinstance(left.type, ir.DoubleType):
                right = self.builder.uitofp(right, ir.DoubleType())
            else:
                raise Exception("wrong type to promote!")

        if isinstance(left.type, ir.IntType):
            if op == CalcLexer.PLUS:
                return self.builder.add(left, right)
            elif op == CalcLexer.MINUS:
                return self.builder.sub(left, right)

        elif isinstance(left.type, ir.DoubleType):
            if op == CalcLexer.PLUS:
                return self.builder.fadd(left, right)
            elif op == CalcLexer.MINUS:
                return self.builder.fsub(left, right)

        raise Exception("unsuported types in binary")

    def visitDeclaration(self, ctx: CalcParser.DeclarationContext):
        value = self.visit(ctx.value)
        decltype = ir.IntType(32)
        if ctx.vartype.text == "double":
            decltype = ir.DoubleType()

        if value.type != decltype:
            raise Exception("cannot assign difrent types")

        ptr = self.builder.alloca(value.type)
        self.builder.store(value, ptr)
        self.locals[ctx.name.text] = ptr

    def visitPrintvar(self, ctx: CalcParser.PrintvarContext):
        name = ctx.name.text
        if not name in self.locals:
            raise Exception("missing variable")

        value = self.locals[name]

        voidptr_ty = ir.IntType(8).as_pointer()
        fmt = "%i \n\0"
        if isinstance(value.type.pointee, ir.DoubleType):
            fmt = "%f \n\0"
        c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                            bytearray(fmt.encode("utf8")))
        global_fmt = ir.GlobalVariable(
            self.module, c_fmt.type, name="fstr"+str(randint(0, 100000)))
        global_fmt.linkage = 'internal'
        global_fmt.global_constant = True
        global_fmt.initializer = c_fmt
        fmt_arg = self.builder.bitcast(global_fmt, voidptr_ty)

        self.builder.call(self.printf, [fmt_arg, self.builder.load(value)])

        return self.visitChildren(ctx)
