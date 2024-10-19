import base64
import random
import string
import ast
import argparse

# Генерация случайного имени переменной или функции
def random_var_name(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

# Функция для обфускации строки
def obfuscate_string(s):
    if isinstance(s, str):  # Проверяем, является ли s строкой
        return base64.b64encode(s.encode()).decode()
    return str(s)  # Если не строка, просто преобразуем в строку

# Проверка, является ли строка закодированной в Base64
def is_base64_encoded(s):
    try:
        return base64.b64encode(base64.b64decode(s)).decode() == s
    except Exception:
        return False

# Проверка, является ли строка числом
def is_numeric_string(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Рекурсивная функция для обфускации дерева AST
def obfuscate_ast(node, var_mapping):
    if isinstance(node, ast.FunctionDef):
        original_name = node.name
        obfuscated_name = random_var_name()
        var_mapping[original_name] = obfuscated_name
        node.name = obfuscated_name

        for arg in node.args.args:
            if arg.arg not in var_mapping:
                var_mapping[arg.arg] = random_var_name()
            arg.arg = var_mapping[arg.arg]

        for stmt in node.body:
            obfuscate_ast(stmt, var_mapping)

    elif isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name):
                if target.id not in var_mapping:
                    var_mapping[target.id] = random_var_name()
                target.id = var_mapping[target.id]
        obfuscate_ast(node.value, var_mapping)

    elif isinstance(node, ast.Expr):
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            func_name = node.value.func.id
            if func_name in var_mapping:
                node.value.func.id = var_mapping[func_name]

    elif isinstance(node, ast.Constant):  # Используем ast.Constant
        original_value = node.value  # Получаем значение
        if isinstance(original_value, str):
            # Если значение - это закодированная строка
            if is_base64_encoded(original_value):
                decoded_value = base64.b64decode(original_value).decode()
                # Преобразуем в число, если это возможно
                if is_numeric_string(decoded_value):
                    node.value = int(decoded_value) if decoded_value.isdigit() else float(decoded_value)
                else:
                    node.value = obfuscate_string(original_value)  # Используем обфускацию
            else:
                node.value = obfuscate_string(original_value)  # Обфускаем строку
        # Не обфусцируем, если это не строка

    for child in ast.iter_child_nodes(node):
        obfuscate_ast(child, var_mapping)

def obfuscate_code(code):
    tree = ast.parse(code)
    var_mapping = {}
    obfuscate_ast(tree, var_mapping)
    obfuscated_code = ast.unparse(tree)
    return obfuscated_code

def main(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:  # Указать кодировку
        original_code = f.read()

    obfuscated_code = obfuscate_code(original_code)

    with open(output_file, 'w', encoding='utf-8') as f:  # Указать кодировку
        f.write(obfuscated_code)

    print(f"Обфусцированный код сохранен в {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Обфускация Python кода")
    parser.add_argument('-o', '--output', type=str, required=True, 
                        help="Путь к выходному файлу для обфусцированного кода.")
    parser.add_argument('-e', '--example', type=str, required=True, 
                        help="Путь к входному файлу с оригинальным кодом.")
    args = parser.parse_args()

    main(args.example, args.output)