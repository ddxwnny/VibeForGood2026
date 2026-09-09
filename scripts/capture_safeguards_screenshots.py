import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
BASE_URL = "https://vibeforgood2026-ruddy.vercel.app"
OUT_DIR = Path("docs/screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)
BRAIN_DIR = Path(r"C:\Users\braed\.gemini\antigravity\brain\bcfdf963-2e74-46de-831f-0e73bc928184")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=EDGE_PATH, headless=True)
        # Desktop high-DPI viewport (1440x960, scale factor 2 for razor sharp text)
        context = await browser.new_context(
            viewport={"width": 1400, "height": 920},
            device_scale_factor=2,
        )
        page = await context.new_page()

        # ---------------------------------------------------------------------
        # 1. INFORMED CONSENT & TRANSPARENCY SCREENSHOT
        # ---------------------------------------------------------------------
        print("Capturing 1. Informed Consent & Transparency...")
        await page.goto(f"{BASE_URL}/#consent")
        await page.wait_for_selector(".consent-panel, .card, h2", timeout=10000)
        await asyncio.sleep(1.5)
        
        # Scroll to show full consent cards
        img1_path = OUT_DIR / "1_informed_consent_transparency.png"
        await page.screenshot(path=str(img1_path), full_page=False)

        # ---------------------------------------------------------------------
        # 2. OBSERVATIONS, NOT MEDICAL DIAGNOSES SCREENSHOT
        # ---------------------------------------------------------------------
        print("Capturing 2. Observations, Not Medical Diagnoses...")
        await page.goto(f"{BASE_URL}/#dashboard")
        await page.wait_for_selector(".obs-card, .window-card, .dashboard", timeout=10000)
        await asyncio.sleep(1.5)
        
        img2_path = OUT_DIR / "2_observations_not_diagnoses.png"
        await page.screenshot(path=str(img2_path), full_page=False)

        # ---------------------------------------------------------------------
        # 3. PRIVACY-BY-DESIGN & DATA MINIMIZATION SCREENSHOT
        # ---------------------------------------------------------------------
        print("Capturing 3. Privacy-by-Design & Data Minimization...")
        # Scroll down on dashboard to show privacy controls, audio discard, & key shredding
        privacy_el = await page.query_selector(".privacy-card, .erasure-section, #privacy-section, footer, .danger-zone")
        if privacy_el:
            await privacy_el.scroll_into_view_if_needed()
        else:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await asyncio.sleep(1.0)
        
        img3_path = OUT_DIR / "3_privacy_data_minimization.png"
        await page.screenshot(path=str(img3_path), full_page=False)

        # ---------------------------------------------------------------------
        # 4. BIAS & DIALECT CALIBRATION SCREENSHOT
        # ---------------------------------------------------------------------
        print("Capturing 4. Bias & Dialect Calibration (Singlish & Heritage Places)...")
        await page.goto(f"{BASE_URL}/#chat")
        await page.wait_for_selector("#message, .conversation", timeout=10000)
        await asyncio.sleep(1.0)
        
        # Send a natural Singapore English message to demonstrate dialect calibration
        msg_input = await page.query_selector("#message")
        if msg_input:
            await msg_input.fill("Good morning Aunty! I haven't taken my pills yet, going to buy kopi and chwee kueh first lah.")
            send_btn = await page.query_selector("button[type='submit']")
            if send_btn:
                await send_btn.click()
                await asyncio.sleep(2.5)

        img4_path = OUT_DIR / "4_bias_dialect_calibration.png"
        await page.screenshot(path=str(img4_path), full_page=False)

        await browser.close()
        print("All screenshots captured successfully!")

        # Copy to brain dir for embedding in artifacts
        if BRAIN_DIR.exists():
            for p in [img1_path, img2_path, img3_path, img4_path]:
                shutil.copyfile(p, BRAIN_DIR / p.name)
            print("Copied screenshots to artifact directory.")

asyncio.run(run())
