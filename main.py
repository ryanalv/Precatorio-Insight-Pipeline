from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_APP = ROOT_DIR / "frontend" / "streamlit_app.py"
BACKEND_SERVICE_NAME = "precatorio-insight-pipeline"


def main() -> int:
    load_env_file()
    args = parse_args()

    backend_url = build_local_url(args.backend_host, args.backend_port)
    streamlit_url = build_local_url(args.frontend_host, args.frontend_port)

    child_env = os.environ.copy()
    child_env["API_BASE_URL"] = backend_url
    child_env.setdefault("PYTHONUNBUFFERED", "1")

    backend_process: subprocess.Popen[bytes] | None = None
    frontend_process: subprocess.Popen[bytes] | None = None

    print("Precatorio Insight Pipeline")
    print(f"API:       {backend_url}")
    print(f"Streamlit: {streamlit_url}")
    print()

    try:
        if is_backend_ready(backend_url):
            print("Backend ja esta online. Vou reutilizar a API em execucao.")
        else:
            backend_process = start_backend(args.backend_host, args.backend_port, child_env)
            wait_for_backend(backend_url, backend_process, timeout=args.startup_timeout)

        frontend_process = start_frontend(
            args.frontend_host,
            args.frontend_port,
            child_env,
            open_browser=not args.no_browser,
        )

        print()
        print("Tudo pronto. Use Ctrl+C para encerrar backend e frontend.")
        print(f"Abra o site em: {streamlit_url}")
        print()

        monitor_processes(backend_process, frontend_process)
    except KeyboardInterrupt:
        print("\nEncerrando aplicacao...")
    except RuntimeError as exc:
        print(f"\nErro ao iniciar o projeto: {exc}", file=sys.stderr)
        return 1
    finally:
        terminate_process(frontend_process, "Streamlit")
        terminate_process(backend_process, "Backend")

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inicia backend FastAPI e frontend Streamlit com um unico comando.",
    )
    parser.add_argument(
        "--backend-host",
        default=os.getenv("BACKEND_HOST", "127.0.0.1"),
        help="Host do backend FastAPI. Padrao: 127.0.0.1",
    )
    parser.add_argument(
        "--backend-port",
        default=int(os.getenv("BACKEND_PORT", "8000")),
        type=int,
        help="Porta do backend FastAPI. Padrao: 8000",
    )
    parser.add_argument(
        "--frontend-host",
        default=os.getenv("FRONTEND_HOST", "127.0.0.1"),
        help="Host do Streamlit. Padrao: 127.0.0.1",
    )
    parser.add_argument(
        "--frontend-port",
        default=int(os.getenv("FRONTEND_PORT", "8501")),
        type=int,
        help="Porta do Streamlit. Padrao: 8501",
    )
    parser.add_argument(
        "--startup-timeout",
        default=int(os.getenv("STARTUP_TIMEOUT", "45")),
        type=int,
        help="Tempo maximo, em segundos, para a API ficar pronta. Padrao: 45",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Inicia o Streamlit sem abrir o navegador automaticamente.",
    )
    return parser.parse_args()


def load_env_file() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv(ROOT_DIR / ".env")


def build_local_url(host: str, port: int) -> str:
    url_host = "127.0.0.1" if host in {"0.0.0.0", "::"} else host
    return f"http://{url_host}:{port}"


def start_backend(host: str, port: int, env: dict[str, str]) -> subprocess.Popen[bytes]:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    return start_process("Backend FastAPI", command, env)


def start_frontend(
    host: str,
    port: int,
    env: dict[str, str],
    *,
    open_browser: bool,
) -> subprocess.Popen[bytes]:
    if not FRONTEND_APP.exists():
        raise RuntimeError(f"Arquivo do frontend nao encontrado: {FRONTEND_APP}")

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(FRONTEND_APP),
        "--server.address",
        host,
        "--server.port",
        str(port),
        "--server.headless",
        "false" if open_browser else "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    return start_process("Frontend Streamlit", command, env)


def start_process(
    name: str,
    command: list[str],
    env: dict[str, str],
) -> subprocess.Popen[bytes]:
    print(f"Iniciando {name}...")
    return subprocess.Popen(command, cwd=ROOT_DIR, env=env)


def wait_for_backend(
    backend_url: str,
    backend_process: subprocess.Popen[bytes],
    *,
    timeout: int,
) -> None:
    print("Aguardando backend ficar pronto...")
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        if backend_process.poll() is not None:
            raise RuntimeError(
                "o backend encerrou antes de responder. Confira se as dependencias "
                "foram instaladas com `pip install -r requirements.txt` e se a porta esta livre."
            )

        if is_backend_ready(backend_url):
            print("Backend pronto.")
            return

        time.sleep(0.5)

    raise RuntimeError(f"backend nao respondeu em {timeout}s em {backend_url}.")


def is_backend_ready(backend_url: str) -> bool:
    try:
        with urllib.request.urlopen(f"{backend_url}/", timeout=1.5) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return False

    return payload.get("service") == BACKEND_SERVICE_NAME


def monitor_processes(
    backend_process: subprocess.Popen[bytes] | None,
    frontend_process: subprocess.Popen[bytes] | None,
) -> None:
    while True:
        if backend_process is not None and backend_process.poll() is not None:
            raise RuntimeError(f"backend encerrou com codigo {backend_process.returncode}.")

        if frontend_process is not None and frontend_process.poll() is not None:
            raise RuntimeError(f"Streamlit encerrou com codigo {frontend_process.returncode}.")

        time.sleep(1)


def terminate_process(process: subprocess.Popen[bytes] | None, name: str) -> None:
    if process is None or process.poll() is not None:
        return

    print(f"Encerrando {name}...")
    process.terminate()

    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        print(f"Forcando encerramento de {name}...")
        process.kill()
        process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
