def generate_badge():
    print("===================================================")
    print("            CoAgent Badge Generator                ")
    print("===================================================")
    title = input("Enter badge title/status: ").strip() or "System Healthy"
    print(f"\n [ {title.upper()} ] \n")
    print("[✓] Badge generated successfully.")

if __name__ == "__main__":
    generate_badge()
