#!/usr/bin/env python3
# main.py - Ponto de entrada do bot de detecção de fraude (CLI)

import argparse
import json
import sys
import os

from config import LOG_FILE_DEFAULT, REPORT_FILE_DEFAULT
from log_generator import generate_logs, save_logs, load_logs
from log_analyzer import analyze_logs, generate_report, save_report, print_report_summary


def cmd_generate(args):
    """Gera logs simulados e salva no arquivo."""
    output_path = args.output or LOG_FILE_DEFAULT
    logs = generate_logs(count=args.count, suspicious_ratio=args.suspicious_ratio)
    save_logs(logs, output_path)
    print(f"   Logs normais  : ~{int(args.count * (1 - args.suspicious_ratio))}")
    print(f"   Logs suspeitos: ~{int(args.count * args.suspicious_ratio)}")


def cmd_analyze(args):
    """Analisa logs de um arquivo e gera relatório."""
    input_path = args.file or LOG_FILE_DEFAULT

    if not os.path.exists(input_path):
        print(f"❌ Arquivo '{input_path}' não encontrado. Gere os logs primeiro com --generate-logs.")
        sys.exit(1)

    logs = load_logs(input_path)
    print(f"📂 Carregados {len(logs)} logs de '{input_path}'")

    # Limita a quantidade se especificado
    if args.limit and args.limit < len(logs):
        logs = logs[:args.limit]
        print(f"⚡ Limitando análise aos primeiros {args.limit} logs.")

    analyzed = analyze_logs(logs, verbose=not args.quiet)
    report = generate_report(analyzed)

    report_path = args.report_output or REPORT_FILE_DEFAULT
    save_report(report, report_path)

    if not args.quiet:
        print_report_summary(report)


def cmd_report(args):
    """Exibe o relatório de fraudes salvo."""
    report_path = args.file or REPORT_FILE_DEFAULT

    if not os.path.exists(report_path):
        print(f"❌ Relatório '{report_path}' não encontrado. Execute --analyze-logs primeiro.")
        sys.exit(1)

    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    print_report_summary(report)


def main():
    parser = argparse.ArgumentParser(
        description="🔐 Bot de Análise de Logs Suspeitos e Detecção de Fraude",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py --generate-logs 100
  python main.py --analyze-logs logs.json --limit 20
  python main.py --report
  python main.py --generate-logs 50 --output meus_logs.json
  python main.py --analyze-logs meus_logs.json --report-output meu_relatorio.json
        """,
    )

    subparsers = parser.add_subparsers(dest="command")

    # --- Subcomando: generate-logs ---
    gen_parser = subparsers.add_parser("--generate-logs", help="Gera logs simulados")
    gen_parser.add_argument("count", type=int, nargs="?", default=50, help="Quantidade de logs a gerar (padrão: 50)")
    gen_parser.add_argument("--output", "-o", type=str, help=f"Caminho do arquivo de saída (padrão: {LOG_FILE_DEFAULT})")
    gen_parser.add_argument(
        "--suspicious-ratio", type=float, default=0.25,
        help="Proporção de eventos suspeitos (0.0-1.0, padrão: 0.25)"
    )

    # --- Subcomando: analyze-logs ---
    analyze_parser = subparsers.add_parser("--analyze-logs", help="Analisa logs existentes")
    analyze_parser.add_argument("file", type=str, nargs="?", help=f"Caminho do arquivo de logs (padrão: {LOG_FILE_DEFAULT})")
    analyze_parser.add_argument("--limit", "-n", type=int, help="Limitar número de logs a analisar")
    analyze_parser.add_argument("--report-output", "-r", type=str, help=f"Caminho do relatório de saída (padrão: {REPORT_FILE_DEFAULT})")
    analyze_parser.add_argument("--quiet", "-q", action="store_true", help="Não exibe progresso detalhado")

    # --- Subcomando: report ---
    report_parser = subparsers.add_parser("--report", help="Exibe o relatório de fraudes")
    report_parser.add_argument("file", type=str, nargs="?", help=f"Caminho do relatório (padrão: {REPORT_FILE_DEFAULT})")

    # Suporte a chamadas antigas estilo --generate-logs <n> diretamente
    # Redireciona argv para subcomandos sem o "--"
    args_list = sys.argv[1:]
    if args_list and args_list[0] in ("--generate-logs", "--analyze-logs", "--report"):
        args_list[0] = args_list[0].lstrip("-")
        sys.argv = [sys.argv[0]] + args_list

    args = parser.parse_args()

    if args.command in ("generate-logs", "-generate-logs"):
        cmd_generate(args)
    elif args.command in ("analyze-logs", "-analyze-logs"):
        cmd_analyze(args)
    elif args.command in ("report", "-report"):
        cmd_report(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
