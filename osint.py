import os
import subprocess
import phonenumbers
import requests
import questionary
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

OSINTGRAM_PATH = "./Osintgram"
SESSION_FILE = "config/username_sessionid.json"  # Update if you use auth

def analyze_email(email):
    return f"""[Email Analysis: {email}]
- Breach Check: https://haveibeenpwned.com
- Gravatar: https://www.gravatar.com/{email.lower()}
- Google: https://www.google.com/search?q="{email}"
Advice:
• Use aliases
• Avoid reusing the same email across platforms
"""

def analyze_phone(phone):
    try:
        parsed = phonenumbers.parse(phone, None)
        region = phonenumbers.region_code_for_number(parsed)
        return f"""[Phone Analysis: {phone}]
- Region: {region}
- Google Search: https://www.google.com/search?q="{phone}"
Advice:
• Use a virtual number on public platforms
"""
    except:
        return f"[Phone Analysis Failed] Invalid phone number: {phone}\n"

def analyze_instagram(username):
    profile_url = f"https://www.instagram.com/{username}/"
    return f"""[Instagram Analysis: @{username}]
- Profile: {profile_url}
- Use Osintgram integration below
"""

def analyze_linkedin(username):
    url = f"https://www.linkedin.com/in/{username}"
    return f"""[LinkedIn Analysis: {username}]
- Profile: {url}
Advice:
• Limit profile visibility
• Avoid oversharing job/location details
"""

def cross_platform_check(username):
    result = f"[Cross-Platform Username Check: @{username}]\n"
    platforms = ["github.com", "twitter.com", "reddit.com", "medium.com", "pinterest.com"]
    headers = {'User-Agent': 'Mozilla/5.0'}
    for site in platforms:
        url = f"https://{site}/{username}"
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                result += f"- Found: {url}\n"
        except:
            continue
    result += "Advice:\n• Don’t use the same username everywhere\n"
    return result

def search_engines(email, phone, username):
    return f"""[Search Engine Intelligence]
- Email Leaks: https://www.google.com/search?q=site:pastebin.com+{email}
- Phone Leaks: https://www.google.com/search?q={phone}+dox
- Username Leaks: https://www.google.com/search?q="{username}"+leak
"""

def run_osintgram(username):
    print("🔍 Running Osintgram for Instagram recon...")
    os.chdir(OSINTGRAM_PATH)

    # Generate output file
    out_file = f"../osintgram_output_{username}.txt"

    try:
        commands = ["info", "followers", "following", "hashtags", "captions", "emails"]
        full_report = ""

        for cmd in commands:
            print(f"→ {cmd}")
            result = subprocess.run(
                ["python3", "main.py", username, f"-c", cmd],
                capture_output=True, text=True
            )
            full_report += f"\n[Instagram {cmd.capitalize()}]\n" + result.stdout

        os.chdir("..")
        return full_report
    except Exception as e:
        os.chdir("..")
        return f"[Osintgram Error] {e}"

def generate_pdf(report, filename="osintgram_osint_report.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)
    text = c.beginText(40, 750)
    text.setFont("Helvetica", 10)
    for line in report.split("\n"):
        text.textLine(line)
        if text.getY() < 40:
            c.drawText(text)
            c.showPage()
            text = c.beginText(40, 750)
            text.setFont("Helvetica", 10)
    c.drawText(text)
    c.save()
    print(f"\n✅ Report saved as: {filename}")

def main():
    print("\n🕵️ OSINT HUNTER - CLI with Osintgram")

    modules = questionary.checkbox(
        "Select the OSINT modules you want to run:",
        choices=[
            "Email Analysis",
            "Phone Number Analysis",
            "Instagram Profile Check + Osintgram",
            "LinkedIn Profile Check",
            "Username Cross-Platform Check",
            "Search Engine Intel (Google Dorking)"
        ]).ask()

    report = ""
    email = phone = insta = linkedin = ""

    if "Email Analysis" in modules or "Search Engine Intel (Google Dorking)" in modules:
        email = questionary.text("Enter email:").ask()
    if "Phone Number Analysis" in modules or "Search Engine Intel (Google Dorking)" in modules:
        phone = questionary.text("Enter phone (+countrycode):").ask()
    if any(m in modules for m in ["Instagram Profile Check + Osintgram", "Username Cross-Platform Check", "Search Engine Intel (Google Dorking)"]):
        insta = questionary.text("Instagram username:").ask()
    if "LinkedIn Profile Check" in modules:
        linkedin = questionary.text("LinkedIn username:").ask()

    if "Email Analysis" in modules:
        report += analyze_email(email)
    if "Phone Number Analysis" in modules:
        report += analyze_phone(phone)
    if "Instagram Profile Check + Osintgram" in modules:
        report += analyze_instagram(insta)
        report += run_osintgram(insta)
    if "LinkedIn Profile Check" in modules:
        report += analyze_linkedin(linkedin)
    if "Username Cross-Platform Check" in modules:
        report += cross_platform_check(insta)
    if "Search Engine Intel (Google Dorking)" in modules:
        report += search_engines(email, phone, insta)

    generate_pdf(report)

if __name__ == "__main__":
    main()
