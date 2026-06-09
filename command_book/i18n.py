from __future__ import annotations

import os

_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        # app
        "app_help": "Command Book — save and run commands with interactive parameters.",  # noqa
        # add
        "add_help": "Register a new command interactively.",
        "add_prompt_key": "Key (slug):",
        "add_prompt_cmd": "Commad:",
        "add_example_cmd": "Example: echo {{greeting::hello}} {{required_name!}} {{optional_text}}",  # noqa
        "add_prompt_description": "Short description:",
        "add_prompt_tags": "Tags (comma-separated):",
        "add_saved": "✔ Command '{key}' saved.",
        "key_invalid": "Must be unique, required and without spaces!",
        # list
        "list_help": "List all saved commands.",
        "list_empty": "No commands saved.",
        "col_key": "KEY",
        "col_description": "DESCRIPTION",
        "col_tags": "TAGS",
        # run
        "run_help": "Run a command by key.",
        "required": "required",
        "run_arg_help": "Key of the command to run",
        "run_not_found": "Command '{key}' not found.",
        "run_executing": "✔ Running:",
        # remove
        "remove_help": "Delete a command.",
        "remove_arg_help": "Key of the command to delete",
        "remove_deleted": "✔ Command '{key}' deleted.",
        "remove_not_found": "Command '{key}' not found.",
        # edit
        "edit_help": "Edit an existing command interactively.",
        "edit_arg_help": "Name of the command to edit",
        "edit_saved": "✔ Command '{key}' updated.",
        # search
        "search_help": "Filter commands by any field.",
        "search_arg_help": "Search term",
        "search_no_results": "No results for '{term}'.",
        # tags
        "tags_help": "List all available tags.",
        "tags_empty": "No tags registered.",
        # config
        "config_help": "Show or edit the config file.",
        "config_file": "Config file:",
        "config_created": "Created empty config file.",
        # menu
        "menu_empty": "No commands saved. Use `bb add` to add one.",
        "menu_title": "Command Book",
        "menu_instruction": "[↑↓] navigate  [enter] select  [esc] quit",
        "menu_exit": "EXIT",
        },
    "es": {
        # app
        "app_help": "Command Book — guarda y ejecuta comandos con parámetros interactivos.",  # noqa
        # add
        "add_help": "Registra un nuevo comando de forma interactiva.",
        "add_prompt_key": "Nombre clave (slug):",
        "add_prompt_cmd": "Comando:",
        "add_example_cmd": "Ejemplo: echo {{greeting::hello}} {{required_name}!} {{optional_text}}",  # noqa
        "add_prompt_description": "Descripción breve:",
        "add_prompt_tags": "Tags (separados por coma):",
        "add_saved": "✔ Comando '{key}' guardado.",
        "key_invalid": "Debe ser única, requerida y sin espacios!",
        # list
        "list_help": "Lista todos los comandos guardados.",
        "list_empty": "No hay comandos guardados.",
        "col_key": "CLAVE",
        "col_description": "DESCRIPCIÓN",
        "col_tags": "TAGS",
        # run
        "run_help": "Ejecuta un comando por su clave.",
        "required": "requerido",
        "run_arg_help": "Clave del comando a ejecutar",
        "run_not_found": "Comando '{key}' no encontrado.",
        "run_executing": "✔ Ejecutando:",
        # remove
        "remove_help": "Elimina un comando.",
        "remove_arg_help": "Clave del comando a eliminar",
        "remove_deleted": "✔ Comando '{key}' eliminado.",
        "remove_not_found": "Comando '{key}' no encontrado.",
        # edit
        "edit_help": "Edita un comando existente de forma interactiva.",
        "edit_arg_help": "Clave del comando a editar",
        "edit_saved": "✔ Comando '{key}' actualizado.",
        # search
        "search_help": "Filtra comandos por todos sus campos.",
        "search_arg_help": "Término de búsqueda",
        "search_no_results": "Sin resultados para '{term}'.",
        # tags
        "tags_help": "Lista todos los tags disponibles.",
        "tags_empty": "No hay tags registrados.",
        # config
        "config_help": "Muestra o edita el fichero de configuración.",
        "config_file": "Fichero de configuración:",
        "config_created": "Fichero de configuración creado.",
        # menu
        "menu_empty": "No hay comandos guardados. Usa `bb add` para añadir uno.",  # noqa
        "menu_title": "Command Book",
        "menu_instruction": "[↑↓] navegar  [enter] seleccionar  [esc] salir",
        "menu_cancel": "SALIR",
        },
    }

_SUPPORTED = set(_TRANSLATIONS.keys())


def _detect_lang() -> str:
    """Detects language from CB_LANG, then LANG env var. Falls back to 'en'."""
    lang = os.environ.get("CB_LANG", "").strip().lower()[:2]
    if lang in _SUPPORTED:
        return lang
    lang = os.environ.get("LANG", "").strip().lower()[:2]
    if lang in _SUPPORTED:
        return lang
    return "en"


_current_lang: str = _detect_lang()
_strings: dict[str, str] = _TRANSLATIONS[_current_lang]


def _(key: str) -> str:
    """Return the translated string for *key* in the current language."""
    return _strings.get(key, _TRANSLATIONS["en"].get(key, key))
