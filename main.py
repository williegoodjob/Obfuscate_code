"""
Copyright (c) 2024 豆伯

This software is licensed under the MIT License. See LICENSE for details.
"""
import ast
import random
import keyword
import string
import sys
import builtins
from faker import Faker

fake = Faker('zh_TW')

def get_builtin_names():
    builtin_names = set(dir(builtins))
    builtin_names.update(keyword.kwlist)
    builtin_names.update({'__name__', '__main__'})
    return builtin_names

def random_string(mode = 'code',length=64):
    letters = string.ascii_letters + string.digits
    while True:
        if mode == 'code':
            new_name = ''.join(random.choice(letters) for _ in range(length))
        elif mode == 'name':
            new_name = ''.join(fake.name() for _ in range(length))
        if not new_name[0].isdigit() and new_name not in keyword.kwlist:
            return new_name

def obfuscate_code(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    tree = ast.parse(source)
    builtin_names = get_builtin_names()
    name_mapping = {}
    alias_names = set()

    # 收集所有的模組別名名稱
    class AliasCollector(ast.NodeVisitor):
        def visit_Import(self, node):
            for alias in node.names:
                if alias.asname:
                    alias_names.add(alias.asname)
                else:
                    # 如果沒有別名，則使用模組名的第一部分
                    alias_names.add(alias.name.split('.')[0])
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            for alias in node.names:
                if alias.asname:
                    alias_names.add(alias.asname)
                else:
                    alias_names.add(alias.name)
            self.generic_visit(node)

    AliasCollector().visit(tree)
    # 將模組別名加入到內建名稱集合中，避免被替換
    builtin_names.update(alias_names)

    class RenameTransformer(ast.NodeTransformer):
        def visit_FunctionDef(self, node):
            # 替換函數名稱
            if node.name not in builtin_names:
                if node.name not in name_mapping:
                    name_mapping[node.name] = random_string()
                node.name = name_mapping[node.name]
            self.generic_visit(node)
            return node

        def visit_ClassDef(self, node):
            # 替換類別名稱
            if node.name not in builtin_names:
                if node.name not in name_mapping:
                    name_mapping[node.name] = random_string()
                node.name = name_mapping[node.name]
            self.generic_visit(node)
            return node

        def visit_Name(self, node):
            if isinstance(node.ctx, (ast.Load, ast.Store, ast.Del)):
                if node.id not in builtin_names:
                    if node.id not in name_mapping:
                        name_mapping[node.id] = random_string()
                    node.id = name_mapping[node.id]
            return node

        def visit_Attribute(self, node):
            # 不替換屬性名稱，避免影響調用
            self.generic_visit(node)
            return node

        def visit_arg(self, node):
            # 替換參數名稱
            if node.arg not in builtin_names:
                if node.arg not in name_mapping:
                    name_mapping[node.arg] = random_string()
                node.arg = name_mapping[node.arg]
            return node

    transformer = RenameTransformer()
    transformer.visit(tree)

    # 修復位置資訊
    ast.fix_missing_locations(tree)

    # 將 AST 轉換回代碼
    try:
        new_source = ast.unparse(tree)
    except AttributeError:
        # ast.unparse 在 Python 3.9+ 可用，舊版本需要使用 astor 模組
        import astor
        new_source = astor.to_source(tree)

    # 將新代碼寫回文件
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(new_source)

def main():
    if len(sys.argv) < 2:
        print("使用方法：python main.py <輸入文件> [輸出文件]")
        sys.exit(1)

    input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = 'default_output.py'  # 預設輸出文件名

    # 在此處加入處理代碼
    with open(input_file, 'r') as input_stream, open(output_file, 'w') as output_stream:
        # 例如，將輸入文件的內容複製到輸出文件
        for line in input_stream:
            output_stream.write(line)
    obfuscate_code(output_file)

if __name__ == "__main__":
    main()