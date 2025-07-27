#!/usr/bin/env python3
"""
🚀 AUTONOMOUS LAUNCHER
Quick launcher for autonomous self-healing and self-learning capabilities

This provides quick access to the most common autonomous operations.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from scripts.monitoring.unified_monitoring_optimization_system import (
    EnterpriseUtility,
)


def show_banner():
    """Show launcher banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════════════╗
║                           🚀 AUTONOMOUS SYSTEM LAUNCHER                               ║
║                        Quick Access to Self-Healing Capabilities                     ║
╚══════════════════════════════════════════════════════════════════════════════════════╝

Available Quick Commands:
1. 🔄 Start Continuous Operation (30 minutes)
2. ⚡ Run Standard Optimization
3. 📊 Real-Time Health Monitor (5 minutes)
4. 🧠 Learning Pattern Analysis
5. 📋 System Status
6. 🛠️ Custom Command
7. ❌ Exit
    """
    print(banner)


def run_command(command_args):
    """Run autonomous CLI command"""
    try:
        result = subprocess.run([sys.executable, "autonomous_cli.py"] + command_args,
                                capture_output=False, text=True, check=False)
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError) as e:
        print(f"❌ Error running command: {e}")
        return False


def process_choice(choice: str, custom_command: str | None = None) -> None:
    if choice == "1":
        print("\n🔄 Starting continuous operation for 30 minutes...")
        run_command(["start", "--mode", "continuous", "--duration", "30"])
    elif choice == "2":
        print("\n⚡ Running standard optimization...")
        run_command(["start", "--mode", "standard"])
    elif choice == "3":
        print("\n📊 Starting real-time monitor for 5 minutes...")
        run_command(["monitor", "--realtime", "--duration", "300"])
    elif choice == "4":
        print("\n🧠 Running learning pattern analysis...")
        run_command(["learn", "--analyze-history"])
    elif choice == "5":
        print("\n📋 Checking system status...")
        run_command(["status"])
    elif choice == "6" and custom_command:
        args = custom_command.strip().split()
        run_command(args)
    elif choice == "7":
        print("\n👋 Goodbye! Autonomous systems remain operational.")
        sys.exit(0)
    else:
        print("❌ Invalid choice. Please select 1-7.")


def main() -> None:
    """Main launcher"""
    EnterpriseUtility().execute_utility()
    parser = argparse.ArgumentParser(description="Autonomous launcher")
    parser.add_argument("--choice", help="Menu option (1-7)")
    parser.add_argument("--custom-command", help="Command string for option 6")
    parser.add_argument("--no-wait", action="store_true", help="Skip pause prompts")
    args = parser.parse_args()

    workspace = Path("e:/gh_COPILOT")
    if not workspace.exists():
        print("❌ Error: gh_COPILOT workspace not found")
        return

    if args.choice:
        process_choice(args.choice, args.custom_command)
        return

    while True:
        show_banner()

        try:
            choice = input("\n🎯 Select option (1-7): ").strip()
            
            custom_cmd = None
            if choice == "6":
                prompt = "🛠️ Enter custom command (e.g., 'optimize --priority critical'): "
                custom_cmd = input(prompt)
            process_choice(choice, custom_cmd)
            if not args.no_wait:
                input("\n⏸️  Press Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n🛑 Launcher interrupted by user")
            break
        except (OSError, ValueError) as e:
            print(f"\n❌ Error: {e}")
            input("⏸️  Press Enter to continue...")


if __name__ == "__main__":
    EnterpriseUtility().execute_utility()
    main()
