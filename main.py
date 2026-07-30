import os
import sys
import subprocess
import time

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = """
  =============================================================
             CoAgent Enterprise Orchestrator v2.0              
  =============================================================
  [+] System: Operational
  [+] Root Path: C:\\CoAgent
  =============================================================
    """
    if HAS_COLOR:
        print(Fore.CYAN + banner)
    else:
        print(banner)

def run_module(script_path):
    if not os.path.exists(script_path):
        print(f"\n[!] Error: Module target non-existent: {script_path}")
        input("\nPress Enter to continue...")
        return
    
    print(f"\n[>] Launching module: {script_path}\n" + "-"*50)
    try:
        subprocess.run([sys.executable, script_path], check=False)
    except Exception as e:
        print(f"\n[!] Module Execution Error: {e}")
    
    print("-" * 50)
    input("\n[+] Process finished. Press Enter to return to main menu...")

def main_menu():
    while True:
        print_header()
        print("  1. Web Site Cloner (modules/web_clone.py)")
        print("  2. SEO Diagnostic Engine (modules/co_seo.py)")
        print("  3. Quick Site Clone Wrapper (co_siteclone.py)")
        print("  4. Quick SEO Audit Wrapper (co_seo.py)")
        print("  5. System Diagnostics & Health (co_upgrade.py)")
        print("  6. Status Badge Generator (co_badge.py)")
        print("  7. Fuel & Cost Calculator (modules/co_fuelcalc.py)")
        print("  8. Proposal & Script Generator (modules/co_proposal.py)")
        print("  0. Exit Enterprise Interface")
        print("\n" + "="*61)
        
        choice = input("\nSelect Option [0-8]: ").strip()
        
        if choice == '1':
            run_module(os.path.join('modules', 'web_clone.py'))
        elif choice == '2':
            run_module(os.path.join('modules', 'co_seo.py'))
        elif choice == '3':
            run_module('co_siteclone.py')
        elif choice == '4':
            run_module('co_seo.py')
        elif choice == '5':
            run_module('co_upgrade.py')
        elif choice == '6':
            run_module('co_badge.py')
        elif choice == '7':
            run_module(os.path.join('modules', 'co_fuelcalc.py'))
        elif choice == '8':
            run_module(os.path.join('modules', 'co_proposal.py'))
        elif choice == '0':
            print("\nShutting down CoAgent Enterprise Orchestrator. Goodbye!")
            sys.exit(0)
        else:
            print("\n[!] Invalid choice. Try again.")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
