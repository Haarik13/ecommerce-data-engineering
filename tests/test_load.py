import pandas as pd

from src.etl.load import load_parquet


def test_load_parquet_creates_file(tmp_path, monkeypatch):
    df = pd.DataFrame(
        {
            "order_id": ["order_1", "order_2"],
            "price": [100.0, 200.0],
            "is_late_delivery": [False, True],
        }
    )

    output_dir = tmp_path / "processed"

    monkeypatch.setattr(
        "src.etl.load.PROCESSED_DATA_DIR",
        output_dir,
    )

    output_path = output_dir / "test_output.parquet"

    result = load_parquet(
        df,
        "test_output.parquet",
    )

    assert result.exists()
    assert result == output_path


def test_load_parquet_preserves_data(tmp_path, monkeypatch):
    df = pd.DataFrame(
        {
            "order_id": ["order_1", "order_2"],
            "price": [100.0, 200.0],
            "freight_value": [10.0, 20.0],
        }
    )

    output_dir = tmp_path / "processed"

    monkeypatch.setattr(
        "src.etl.load.PROCESSED_DATA_DIR",
        output_dir,
    )

    output_path = load_parquet(
        df,
        "test_output.parquet",
    )

    loaded_df = pd.read_parquet(output_path)

    pd.testing.assert_frame_equal(
        df,
        loaded_df,
    )