import ast
from pathlib import Path


class TestLocustfileStructure:
    def test_public_site_user_delegates_helpers_to_scenario_composition(self) -> None:
        locustfile = Path("performance/locust/locustfile.py")
        tree = ast.parse(locustfile.read_text())
        user_class = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name == "PublicSiteUser"
        )
        method_names = {node.name for node in user_class.body if isinstance(node, ast.FunctionDef)}

        assert "request_api" not in method_names
        assert "request_validated_api" not in method_names
        assert "discover_matrix_sheets" not in method_names
        assert "discover_note_slugs" not in method_names

    def test_public_site_user_task_methods_delegate_to_scenario_attribute(self) -> None:
        locustfile = Path("performance/locust/locustfile.py")
        tree = ast.parse(locustfile.read_text())
        user_class = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef) and node.name == "PublicSiteUser"
        )
        delegated_methods = {
            node.name
            for node in user_class.body
            if isinstance(node, ast.FunctionDef)
            and any(
                isinstance(child, ast.Attribute) and child.attr == "scenario"
                for child in ast.walk(node)
            )
        }

        assert delegated_methods == {
            "on_start",
            "healthcheck",
            "i18n_languages",
            "i18n_bundle",
            "notes_list",
            "notes_tree",
            "note_detail",
            "matrix_sheets",
            "matrix_items",
            "matrix_item_detail",
            "matrix_resources_search",
            "matrix_question_suggestion",
            "spa_root",
        }
