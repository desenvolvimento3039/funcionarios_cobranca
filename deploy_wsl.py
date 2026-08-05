#!/usr/bin/env python3
"""
Script de Sincronização e Deploy no Docker via WSL
=================================================
Copia automaticamente os arquivos para:
\\\\wsl.localhost\\Ubuntu-22.04\\home\\desenvolvimento\\funcionarios-cobranca
e executa o 'docker compose up --build -d' no WSL (Ubuntu-22.04).

Uso:
    python deploy_wsl.py [--no-rebuild]
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path

# Suporte a UTF-8 no Windows Console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_DISTRO = "Ubuntu-22.04"
DEFAULT_WSL_INTERNAL_PATH = "/home/desenvolvimento/funcionarios-cobranca"
DEFAULT_UNC_PATH = Path(r"\\wsl.localhost\Ubuntu-22.04\home\desenvolvimento\funcionarios-cobranca")

PROJECT_ROOT = Path(__file__).parent.resolve()

def execute_cmd(cmd, check=True, capture=False):
    """Executa um comando no terminal Windows."""
    print(f" -> Executando: {cmd if isinstance(cmd, str) else ' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        shell=isinstance(cmd, str),
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None
    )
    if check and result.returncode != 0:
        err = result.stderr if capture else f"Codigo de saida {result.returncode}"
        print(f"[ERRO] Falha no comando: {err}")
        sys.exit(result.returncode)
    return result

def run_in_wsl(wsl_cmd: str, distro: str = DEFAULT_DISTRO, check=True):
    """Executa um comando bash dentro da distribuição WSL especificada."""
    cmd = ["wsl", "-d", distro, "bash", "-c", wsl_cmd]
    return execute_cmd(cmd, check=check)

def sync_via_unc(target_unc: Path, distro: str = DEFAULT_DISTRO, internal_path: str = DEFAULT_WSL_INTERNAL_PATH):
    """Garante que a pasta exista no WSL e copia os arquivos via UNC Path (\\\\wsl.localhost\\...)."""
    print(f"\n[INFO] Garantindo diretorio no WSL em '{internal_path}'...")
    run_in_wsl(f"mkdir -p '{internal_path}'", distro=distro)

    print(f"[INFO] Copiando arquivos de '{PROJECT_ROOT}' para '{target_unc}'...")
    
    if not target_unc.exists():
        try:
            target_unc.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

    # Copia backend
    src_backend = PROJECT_ROOT / "backend"
    dst_backend = target_unc / "backend"
    if src_backend.exists():
        try:
            shutil.copytree(
                src_backend,
                dst_backend,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(".venv", "venv", "__pycache__", "*.pyc")
            )
            print("  [OK] Pasta 'backend' copiada com sucesso.")
        except Exception as e:
            print(f"  [AVISO] Ao copiar 'backend' via UNC ({e}), aplicando fallback via WSL...")
            win_src = str(PROJECT_ROOT).replace("\\", "/").replace("C:", "/mnt/c")
            run_in_wsl(f"mkdir -p '{internal_path}/backend' && cp -rf '{win_src}/backend/'* '{internal_path}/backend/' 2>/dev/null || true", distro=distro)

    # Copia frontend
    src_frontend = PROJECT_ROOT / "frontend"
    dst_frontend = target_unc / "frontend"
    if src_frontend.exists():
        try:
            shutil.copytree(
                src_frontend,
                dst_frontend,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("node_modules", ".next", "__pycache__")
            )
            print("  [OK] Pasta 'frontend' copiada com sucesso.")
        except Exception as e:
            print(f"  [AVISO] Ao copiar 'frontend' via UNC ({e}), aplicando fallback via WSL...")
            win_src = str(PROJECT_ROOT).replace("\\", "/").replace("C:", "/mnt/c")
            run_in_wsl(f"mkdir -p '{internal_path}/frontend' && cp -rf '{win_src}/frontend/'* '{internal_path}/frontend/' 2>/dev/null || true", distro=distro)

    # Copia arquivos da raiz (Dockerfile, docker-compose.yml, excel, etc)
    single_files = ["Dockerfile", "docker-compose.yml", "funcionarios_cobranca.xlsx"]
    for fname in single_files:
        src_f = PROJECT_ROOT / fname
        dst_f = target_unc / fname
        if src_f.exists():
            try:
                shutil.copy2(src_f, dst_f)
                print(f"  [OK] Arquivo '{fname}' copiado com sucesso.")
            except Exception:
                win_src = str(PROJECT_ROOT).replace("\\", "/").replace("C:", "/mnt/c")
                run_in_wsl(f"cp -f '{win_src}/{fname}' '{internal_path}/' 2>/dev/null || true", distro=distro)

    print("[OK] Sincronizacao de arquivos concluida!")

def deploy_docker(internal_path: str = DEFAULT_WSL_INTERNAL_PATH, distro: str = DEFAULT_DISTRO, rebuild: bool = True):
    """Executa o build e subida dos containers no WSL."""
    print(f"\n[INFO] Subindo Docker Compose em '{internal_path}' (Distro: {distro})...")
    build_flag = "--build" if rebuild else ""
    
    script = f"""
    cd '{internal_path}' && \
    if docker compose version >/dev/null 2>&1; then
        docker compose up {build_flag} -d
    elif command -v docker-compose >/dev/null 2>&1; then
        docker-compose up {build_flag} -d
    else
        echo '[ERRO] Docker Compose nao encontrado no WSL.'
        exit 1
    fi
    """
    run_in_wsl(script, distro=distro)
    print("[OK] Docker Compose executado com sucesso!")

def check_status(internal_path: str = DEFAULT_WSL_INTERNAL_PATH, distro: str = DEFAULT_DISTRO):
    """Exibe o status do container."""
    print("\n[INFO] Status dos Containers no WSL:")
    run_in_wsl(f"cd '{internal_path}' && (docker compose ps 2>/dev/null || docker ps)", distro=distro, check=False)
    print("\n[INFO] Aplicacao disponivel em: http://localhost:8587")

def main():
    parser = argparse.ArgumentParser(description="Deploy automatizado no WSL Ubuntu-22.04")
    parser.add_argument("--no-rebuild", action="store_true", help="Nao passar --build no docker compose")
    args = parser.parse_args()

    print("=== DEPLOY AUTOMATICO PARA WSL (Ubuntu-22.04) ===")
    print(f"Destino: {DEFAULT_UNC_PATH}")

    try:
        sync_via_unc(DEFAULT_UNC_PATH, distro=DEFAULT_DISTRO, internal_path=DEFAULT_WSL_INTERNAL_PATH)
        deploy_docker(internal_path=DEFAULT_WSL_INTERNAL_PATH, distro=DEFAULT_DISTRO, rebuild=not args.no_rebuild)
        check_status(internal_path=DEFAULT_WSL_INTERNAL_PATH, distro=DEFAULT_DISTRO)
        print("\n[SUCESSO] Deploy concluido com sucesso!")
    except Exception as e:
        print(f"\n[ERRO] Falha durante o deploy: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
