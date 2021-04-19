all:
	java -Xmx500M -cp "/usr/local/lib/antlr-4.9.1-complete.jar:$CLASSPATH" org.antlr.v4.Tool -no-listener -visitor -Dlanguage=Python3 Calc.g4

test:
	python3 main.py > a.ll
	clang a.ll
	./a.out