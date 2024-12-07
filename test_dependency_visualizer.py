import pytest
from dependency_visualizer import parse_apkindex_content, build_dependency_graph, generate_graphviz_graph

def test_parse_apkindex_content():
    print("Запуск теста test_parse_apkindex_content...")
    content = '''
P:package-a
V:1.0.0
D:package-b package-c
T:Example package A

P:package-b
V:1.0.0
D:package-d
T:Example package B

P:package-c
V:1.0.0
D:
T:Example package C

P:package-d
V:1.0.0
D:
T:Example package D
'''
    packages = parse_apkindex_content(content)
    print(f"Parsed packages: {packages}")
    assert len(packages) == 4
    assert 'package-a' in packages
    assert packages['package-a']['D'] == 'package-b package-c'
    print("Тест test_parse_apkindex_content прошел успешно.\n")

def test_build_dependency_graph():
    print("Запуск теста test_build_dependency_graph...")
    packages = {
        'package-a': {'D': 'package-b package-c'},
        'package-b': {'D': 'package-d'},
        'package-c': {'D': ''},
        'package-d': {'D': ''},
    }
    graph = []
    visited = set()
    build_dependency_graph(packages, 'package-a', graph, visited)
    print(f"Generated graph: {graph}")
    assert len(graph) == 3
    assert ('package-a', 'package-b') in graph
    assert ('package-a', 'package-c') in graph
    assert ('package-b', 'package-d') in graph
    print("Тест test_build_dependency_graph прошел успешно.\n")

def test_generate_graphviz_graph():
    print("Запуск теста test_generate_graphviz_graph...")
    graph = [
        ('package-a', 'package-b'),
        ('package-a', 'package-c'),
        ('package-b', 'package-d')
    ]
    graphviz_code = generate_graphviz_graph(graph)
    print(f"Generated Graphviz code: {graphviz_code}")
    expected_code = '''digraph G {
    "package_a" -> "package_b"
    "package_a" -> "package_c"
    "package_b" -> "package_d"
}'''
    assert graphviz_code.strip() == expected_code.strip()
    print("Тест test_generate_graphviz_graph прошел успешно.\n")