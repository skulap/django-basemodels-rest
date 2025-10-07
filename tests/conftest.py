import os
import sys
from pathlib import Path

# Корень проекта (предполагается, что tests/ лежит в корне)
ROOT = Path(__file__).resolve().parents[1]

# Добавляем src/ (poetry src layout) в sys.path
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Добавляем корень в sys.path, чтобы можно было импортировать tests.test_settings
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Устанавливаем DJANGO_SETTINGS_MODULE заблаговременно
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")

# Выполняем инициализацию Django
import django
django.setup()