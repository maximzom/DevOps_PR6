import pytest

@pytest.mark.parametrize("file_path", [
    "/app/requirements.txt",
    "/app/app/main.py",
])
def test_required_files_exist(host, file_path):
    f = host.file(file_path)
    assert f.exists
    assert f.is_file
    assert f.user == "appuser"

def test_non_root_user(host):
    current_user = host.user()
    assert current_user.name == "appuser"
    assert current_user.uid != 0
    assert current_user.uid == 10001

def test_process_is_running(host):
    processes = host.process.filter(user="appuser", comm="gunicorn")
    assert len(processes) >= 1

def test_port_is_listening(host):
    socket = host.socket("tcp://0.0.0.0:5000")
    assert socket.is_listening