import sys
import os
import re
import subprocess
import argparse
import requests
import tarfile
import csv

def download_and_extract_apkindex(repo_url):
    apkindex_url = repo_url.rstrip('/') + '/APKINDEX.tar.gz'
    print(f"Загрузка {apkindex_url}...")
    response = requests.get(apkindex_url, stream=True)
    if response.status_code != 200:
        print(f"Ошибка загрузки APKINDEX: статус {response.status_code}")
        sys.exit(1)
    with open('APKINDEX.tar.gz', 'wb') as f:
        f.write(response.content)
    print("Распаковка APKINDEX.tar.gz...")
    with tarfile.open('APKINDEX.tar.gz', 'r:gz') as tar:
        tar.extract('APKINDEX')
    print("APKINDEX успешно загружен и распакован.")

def parse_apkindex_content(content):
    packages = {}
    entries = content.strip().split('\n\n')
    for entry in entries:
        pkg_info = {}
        lines = entry.strip().split('\n')
        for line in lines:
            if line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key, value = parts
                    pkg_info[key.strip()] = value.strip()
        if 'P' in pkg_info:
            pkg_name = pkg_info['P'].strip().lower()
            packages[pkg_name] = pkg_info
    return packages

def build_dependency_graph(packages, pkg_name, graph, visited, depth=0, max_depth=10):
    pkg_name = pkg_name.strip().lower()
    if pkg_name not in packages:
        print(f"Пакет '{pkg_name}' не найден в репозитории.")
        return
    if pkg_name in visited:
        return
    if depth > max_depth:
        return
    visited.add(pkg_name)
    pkg_info = packages[pkg_name]
    deps_line = pkg_info.get('D', '')
    deps = deps_line.strip().split()
    for dep in deps:
        dep = dep.strip().lower()
        if dep:
            graph.append((pkg_name, dep))
            build_dependency_graph(packages, dep, graph, visited, depth + 1, max_depth)

def sanitize_node_id(name):
    # Заменяем недопустимые символы на подчёркивания
    return re.sub(r'[^a-zA-Z0-9_]', '_', name)

def generate_graphviz_graph(graph):
    graphviz = 'digraph G {\n'
    for src, dst in graph:
        src_id = sanitize_node_id(src)
        dst_id = sanitize_node_id(dst)
        graphviz += f'    "{src_id}" -> "{dst_id}"\n'
    graphviz += '}'
    return graphviz

def visualize_graph(graphviz_code):
    print("Сгенерирован код диаграммы Graphviz:")
    print(graphviz_code)

def read_config_file(config_file):
    with open(config_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

def main():
    config_file = 'config.csv'  # Укажите путь к вашему конфиг-файлу
    config = read_config_file(config_file)

    for entry in config:
        renderer = entry['renderer']
        package = entry['package']
        repository = entry['repository']
        output = entry['output']

        print(f"Обработка пакета: {package} из репозитория: {repository}")

        download_and_extract_apkindex(repository)

        try:
            with open('APKINDEX', 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            print("Файл APKINDEX не найден. Убедитесь, что он находится в текущей директории.")
            sys.exit(1)

        packages = parse_apkindex_content(content)

        if package not in packages:
            print(f"Пакет '{package}' не найден в репозитории.")
            sys.exit(1)

        graph = []
        visited = set()
        build_dependency_graph(packages, package, graph, visited)

        if not graph:
            print(f"Пакет '{package}' не имеет зависимостей.")
            sys.exit(0)

        graphviz_code = generate_graphviz_graph(graph)
        visualize_graph(graphviz_code)

        # Сохраняем результат в файл
        with open(output, 'w', encoding='utf-8') as output_file:
            output_file.write(graphviz_code)

        print(f"Граф зависимостей сохранён в файл {output}")

if __name__ == '__main__':
    main()