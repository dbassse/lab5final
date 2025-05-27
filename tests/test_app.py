from pathlib import Path

import pandas as pd

from src.app import load_data, save_data  # Убедитесь в корректности импорта


def test_load_save_cycle(tmp_path: Path) -> None:  # Используем временный файл
    test_file = tmp_path / "people.parquet"

    # Создаём тестовые данные
    test_data = pd.DataFrame(
        [
            {
                "Фамилия": "Иванов",
                "Имя": "Иван",
                "Телефон": "123",
                "Дата рождения": [1990, 1, 1],  # Исправлено на список
            }
        ]
    )

    # Сохраняем данные во временный файл
    save_data(test_data, str(test_file))  # Теперь передаём путь

    # Загружаем данные
    loaded_data = load_data(str(test_file))  # Теперь передаём путь

    # Проверяем целостность данных
    pd.testing.assert_frame_equal(test_data, loaded_data)
