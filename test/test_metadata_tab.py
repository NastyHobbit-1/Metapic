import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

pytest.importorskip("PySide6", reason="PySide6 is required for GUI metadata tests")
from PySide6.QtWidgets import QApplication

from metapic.gui.enhanced_app import MetadataTab
from metapic.models import ImageMeta


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # QApplication will be cleaned up when the interpreter exits


def test_save_metadata_creates_sidecar(tmp_path, monkeypatch, qapp):
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"")

    tab = MetadataTab()
    tab.current_meta = ImageMeta(path=str(image_path))
    tab.save_btn.setEnabled(True)

    tab.model_edit.setText("Test Model")
    tab.base_model_edit.setText("Base")
    tab.sampler_edit.setText("Euler")
    tab.steps_spin.setValue(30)
    tab.cfg_spin.setValue(7.5)
    tab.seed_spin.setValue(1234)
    tab.prompt_edit.setPlainText("Hello world")
    tab.negative_prompt_edit.setPlainText("None")

    monkeypatch.setattr("metapic.gui.enhanced_app.QMessageBox.information", lambda *args, **kwargs: None)
    monkeypatch.setattr("metapic.gui.enhanced_app.QMessageBox.critical", lambda *args, **kwargs: None)

    tab.save_metadata()

    sidecar = Path(str(image_path.with_suffix(".json")))
    assert sidecar.exists()

    data = json.loads(sidecar.read_text("utf-8"))
    assert data["model"] == "Test Model"
    assert data["base_model"] == "Base"
    assert data["sampler"] == "Euler"
    assert data["steps"] == 30
    assert pytest.approx(data["cfg"], rel=1e-4) == 7.5
    assert data["seed"] == 1234
    assert data["prompt"] == "Hello world"
    assert data["negative_prompt"] == "None"

    assert tab.current_meta.model == "Test Model"
    assert tab.current_meta.parsed_raw["model"] == "Test Model"
    assert not tab.save_btn.isEnabled()
