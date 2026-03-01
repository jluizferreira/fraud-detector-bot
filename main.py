#!/usr/bin/env python3
# main.py - Ponto de entrada do bot de detecção de fraude (CLI)

import sys
import os
import json

from config import LOG_FILE_DEFAULT, REPORT_FILE_DEFAULT
from log_generator import generate_logs, save_logs, load_logs
from log_analyzer import analyze_logs, generate_report, save_report, print_report_summary


def cmd_generate(count=50, output=None, suspicious_ratio=0.25):
    output_path = output or LOG_FILE_DEFAULT
    logs = generate_logs(count=count, suspicious_ratio=suspicious_ratio)
    save_logs(logs, output_path)
    print(f"   Logs normais  : ~{int(count * (1 - suspicious_ratio))}")
    print(f"   Logs suspeitos: ~{int(count * suspicious_ratio)}")


def cmd_analyze(file=None, limit=None, report_output=None, quiet=False):
    input_path = file or LOG_FILE_DEFAULT
    if not os.path.exists(input_path):
        print(f"❌ Arquivo '{input_path}' não encontrado. Gere os logs primeiro com --generate-logs.")
        sys.exit(1)

    logs = load_logs(input_path)
    print(f"📂 Carregados {len(logs)} logs de '{input_path}'")

    if limit and limit < len(logs):
        logs = logs[:limit]
        print(f"⚡ Limitando análise aos primeiros {limit} logs.")

    analyzed = analyze_logs(logs, verbose=not quiet)
    report = generate_report(analyzed)

    report_path = report_output or REPORT_FILE_DEFAULT
    save_report(report, report_path)

    if not quiet:
        print_report_summary(report)


def cmd_report(file=None):
    report_path = file or REPORT_FILE_DEFAULT
    if not os.path.exists(report_path):
        print(f"❌ Relatório '{report_path}' não encontrado. Execute --analyze-logs primeiro.")
        sys.exit(1)
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)
    print_report_summary(report)


def cmd_dashboard():
    print("🚀 Iniciando dashboard... Acesse http://localhost:8501")
    os.system("python -m streamlit run dashboard.py")


def print_help():
    print("""
🔐 Fraud Detector Bot

Uso:
  python main.py --generate-logs [quantidade]
  python main.py --analyze-logs [arquivo] [--limit N]
  python main.py --report [arquivo]
  python main.py --dashboard

Exemplos:
  python main.py --generate-logs 100
  python main.py --analyze-logs --limit 10
  python main.py --report
  python main.py --dashboard
""")


def main():
    args = sys.argv[1:]

    if not args:
        print_help()
        return

    cmd = args[0]

    if cmd == "--generate-logs":
        count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 50
        output = None
        ratio = 0.25
        for i, a in enumerate(args):
            if a == "--output" and i + 1 < len(args):
                output = args[i + 1]
            if a == "--suspicious-ratio" and i + 1 < len(args):
                ratio = float(args[i + 1])
        cmd_generate(count=count, output=output, suspicious_ratio=ratio)

    elif cmd == "--analyze-logs":
        file = None
        limit = None
        report_output = None
        quiet = False
        i = 1
        while i < len(args):
            if args[i] == "--limit" or args[i] == "-n":
                limit = int(args[i + 1]); i += 2
            elif args[i] == "--report-output" or args[i] == "-r":
                report_output = args[i + 1]; i += 2
            elif args[i] == "--quiet" or args[i] == "-q":
                quiet = True; i += 1
            elif not args[i].startswith("--"):
                file = args[i]; i += 1
            else:
                i += 1
        cmd_analyze(file=file, limit=limit, report_output=report_output, quiet=quiet)

    elif cmd == "--report":
        file = args[1] if len(args) > 1 and not args[1].startswith("--") else None
        cmd_report(file=file)

    elif cmd == "--dashboard":
        cmd_dashboard()

    else:
        print(f"❌ Comando desconhecido: {cmd}")
        print_help()


if __name__ == "__main__":
    main()
