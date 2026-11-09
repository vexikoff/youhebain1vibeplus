import ast
import sys
from pathlib import Path


def _call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _calls(tree, name):
    return [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call) and _call_name(node.func) == name
    ]


def _keyword(call, name):
    for keyword in call.keywords:
        if keyword.arg == name:
            return keyword.value
    return None


def _literal(node, default=None):
    if node is None:
        return default
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError):
        return default


def _runtime_assets(main_path):
    tree = ast.parse(main_path.read_text(encoding="utf-8"), filename=str(main_path))
    assets = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or _call_name(node.func) not in {"load", "Sound"}:
            continue
        if not node.args or not isinstance(node.args[0], ast.Call):
            continue
        asset_call = node.args[0]
        if _call_name(asset_call.func) != "asset_path" or not asset_call.args:
            continue
        asset = _literal(asset_call.args[0])
        if isinstance(asset, str):
            assets.add(asset)
    return assets


def _spec_details(spec_path):
    tree = ast.parse(spec_path.read_text(encoding="utf-8"), filename=str(spec_path))
    analyses = _calls(tree, "Analysis")
    executables = _calls(tree, "EXE")
    collections = _calls(tree, "COLLECT")
    if len(analyses) != 1 or len(executables) != 1 or len(collections) != 1:
        raise ValueError(f"{spec_path.name}: expected one Analysis, EXE and COLLECT call")

    analysis = analyses[0]
    executable = executables[0]
    collection = collections[0]
    data_items = _literal(_keyword(analysis, "datas"), [])
    icon = _literal(_keyword(executable, "icon"))
    console = _literal(_keyword(executable, "console"))
    exe_name = _literal(_keyword(executable, "name"))
    collection_name = _literal(_keyword(collection, "name"))

    if not isinstance(data_items, (list, tuple)):
        raise ValueError(f"{spec_path.name}: Analysis.datas must be a literal list")
    assets = set()
    for item in data_items:
        if isinstance(item, (list, tuple)) and item and isinstance(item[0], str):
            assets.add(Path(item[0]).name)

    return {
        "assets": assets,
        "icon": icon,
        "console": console,
        "exe_name": exe_name,
        "collection_name": collection_name,
    }


def check_project(project_dir, spec_paths=None):
    root = Path(project_dir)
    main_path = root / "main.py"
    if not main_path.is_file():
        return [f"Missing game entry point: {main_path}"]

    try:
        required_assets = _runtime_assets(main_path)
    except (OSError, SyntaxError) as error:
        return [f"Cannot inspect runtime assets in main.py: {error}"]

    if spec_paths is None:
        spec_paths = sorted(root.glob("*.spec"))
    else:
        spec_paths = [Path(path) if Path(path).is_absolute() else root / path for path in spec_paths]
    if not spec_paths:
        return ["No PyInstaller spec files found"]

    errors = []
    for spec_path in spec_paths:
        if not spec_path.is_file():
            errors.append(f"{spec_path.name}: spec file not found")
            continue
        try:
            details = _spec_details(spec_path)
        except (OSError, SyntaxError, ValueError) as error:
            errors.append(str(error))
            continue

        if not details["icon"]:
            errors.append(f"{spec_path.name}: EXE.icon is not configured")
        elif not (root / details["icon"]).is_file():
            errors.append(f"{spec_path.name}: icon file not found: {details['icon']}")

        if details["console"] is not True:
            errors.append(f"{spec_path.name}: EXE.console must be True for this console game")
        if not details["exe_name"] or details["exe_name"] != details["collection_name"]:
            errors.append(f"{spec_path.name}: EXE and COLLECT names must both be set and match")

        missing_entries = sorted(required_assets - details["assets"])
        if missing_entries:
            errors.append(
                f"{spec_path.name}: runtime assets missing from Analysis.datas: "
                + ", ".join(missing_entries)
            )

        for asset in sorted(required_assets):
            asset_path = root / asset
            if not asset_path.is_file():
                errors.append(f"{spec_path.name}: runtime asset not found: {asset}")
            elif asset_path.stat().st_size == 0:
                errors.append(f"{spec_path.name}: runtime asset is empty: {asset}")

    return errors


def main():
    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    errors = check_project(project_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("PyInstaller preflight passed: icon, console mode and runtime assets are configured.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
