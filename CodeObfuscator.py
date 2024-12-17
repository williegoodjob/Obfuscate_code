"""
Copyright (c) 2024 豆伯

This software is licensed under the MIT License. See LICENSE for details.
"""
import ast
import random
import keyword
import string
import builtins
from typing import Callable

class CodeObfuscator:
    def __init__(self, name_generator: Callable[[], str] = None, length: int = 64):
        self.name_length = length
        self.name_generator = name_generator or self._default_name_generator
        self.builtin_names = self._get_builtin_names()
        self.name_mapping = {}
        self.alias_names = set()

    # Set Function
    def set_name_generator(self, name_generator: Callable[[], str]):
        self.name_generator = name_generator

    def set_name_length(self, length: int):
        self.name_length = length

    def set_input_file(self, input_file: str):
        self.input_file = input_file

    def set_output_file(self, output_file: str):
        self.output_file = output_file

    # Get Function
    def isDefaultMode(self):
        return self.name_generator == self._default_name_generator
    
    def get_name_Length(self):
        return self.name_length
    
    def get_input_file(self):
        return self.input_file
    
    def get_output_file(self):
        return self.output_file
    
    def get_Preview(self):
        return self.name_generator()
    
    def _get_builtin_names(self):
        builtin_names = set(dir(builtins))
        builtin_names.update(keyword.kwlist)
        builtin_names.update({'__name__', '__main__'})
        return builtin_names

    def _default_name_generator(self) -> str:
        letters = string.ascii_letters + string.digits
        while True:
            new_name = ''.join(random.choice(letters) for _ in range(self.name_length))
            if not new_name[0].isdigit() and new_name not in keyword.kwlist:
                return new_name

    def obfuscate(self, input_file: str = None, output_file: str = None):
        if input_file is None:
            input_file = self.input_file
        if output_file is None:
            output_file = self.output_file or input_file
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source)
        
        # 收集模組別名
        class AliasCollector(ast.NodeVisitor):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator

            def visit_Import(self, node):
                for alias in node.names:
                    if alias.asname:
                        self.obfuscator.alias_names.add(alias.asname)
                    else:
                        self.obfuscator.alias_names.add(alias.name.split('.')[0])
                self.generic_visit(node)

            def visit_ImportFrom(self, node):
                for alias in node.names:
                    if alias.asname:
                        self.obfuscator.alias_names.add(alias.asname)
                    else:
                        self.obfuscator.alias_names.add(alias.name)
                self.generic_visit(node)

        AliasCollector(self).visit(tree)
        self.builtin_names.update(self.alias_names)

        class RenameTransformer(ast.NodeTransformer):
            def __init__(self, obfuscator):
                self.obfuscator = obfuscator

            def visit_FunctionDef(self, node):
                if node.name not in self.obfuscator.builtin_names:
                    if node.name not in self.obfuscator.name_mapping:
                        self.obfuscator.name_mapping[node.name] = self.obfuscator.name_generator()
                    node.name = self.obfuscator.name_mapping[node.name]
                self.generic_visit(node)
                return node

            def visit_ClassDef(self, node):
                if node.name not in self.obfuscator.builtin_names:
                    if node.name not in self.obfuscator.name_mapping:
                        self.obfuscator.name_mapping[node.name] = self.obfuscator.name_generator()
                    node.name = self.obfuscator.name_mapping[node.name]
                self.generic_visit(node)
                return node

            def visit_Name(self, node):
                if isinstance(node.ctx, (ast.Load, ast.Store, ast.Del)):
                    if node.id not in self.obfuscator.builtin_names:
                        if node.id not in self.obfuscator.name_mapping:
                            self.obfuscator.name_mapping[node.id] = self.obfuscator.name_generator()
                        node.id = self.obfuscator.name_mapping[node.id]
                return node

            def visit_Attribute(self, node):
                self.generic_visit(node)
                return node

            def visit_arg(self, node):
                if node.arg not in self.obfuscator.builtin_names:
                    if node.arg not in self.obfuscator.name_mapping:
                        self.obfuscator.name_mapping[node.arg] = self.obfuscator.name_generator()
                    node.arg = self.obfuscator.name_mapping[node.arg]
                return node

        transformer = RenameTransformer(self)
        transformer.visit(tree)
        ast.fix_missing_locations(tree)

        try:
            new_source = ast.unparse(tree)
        except AttributeError:
            import astor
            new_source = astor.to_source(tree)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(new_source)