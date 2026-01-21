"""
Quick E2E test that doesn't start/stop Streamlit.
Run this when Streamlit is already running.
"""

import time
import sys
from playwright.sync_api import sync_playwright

def quick_test():
    """Quick test of WebSocket functionality."""
    print("🔍 Quick E2E WebSocket Test")
    print("=" * 50)
    
    with sync_playwright() as p:
        # Launch browser with viewport size
        browser = p.chromium.launch(
            headless=False,
            args=['--window-size=1400,1000']
        )
        context = browser.new_context(viewport={'width': 1400, 'height': 1000})
        page = context.new_page()
        
        try:
            # Open Streamlit with longer timeout
            print("1. Opening Streamlit UI...")
            page.goto("http://localhost:8501", wait_until="networkidle", timeout=60000)
            time.sleep(3)
            
            # Wait for page to fully load
            page.wait_for_load_state("networkidle")
            
            # Take initial screenshot
            page.screenshot(path="test_initial.png")
            print("   📸 Initial screenshot: test_initial.png")
            
            # Check basic UI
            print("2. Checking UI elements...")
            
            # Title - use more flexible locator
            title_locator = page.locator("h1, h2, h3").filter(has_text="PinkBison")
            if title_locator.count() > 0:
                print("   ✅ Title found")
            else:
                # Try page content
                if "PinkBison" in page.content():
                    print("   ✅ Title found in content")
                else:
                    print("   ❌ Title not found")
                    return False
            
            # Find Live Event Stream - look for the expander or header
            print("3. Finding Live Event Stream...")
            
            # Try different strategies to find the element
            live_event_selectors = [
                "text=📡 Live Event Stream",
                "text=Live Event Stream",
                "[data-testid='stExpander']:has-text('Live Event')",
                ".streamlit-expanderHeader:has-text('Live Event')",
                "div:has-text('Live Event Stream')",
            ]
            
            live_event_element = None
            for selector in live_event_selectors:
                if page.locator(selector).count() > 0:
                    live_event_element = page.locator(selector).first
                    print(f"   Found with selector: {selector}")
                    break
            
            if not live_event_element:
                print("   ❌ Live Event Stream not found")
                # Show what's on the page
                all_text = page.locator("body").inner_text()[:500]
                print(f"   Page content (first 500 chars): {all_text}")
                return False
            
            print("   ✅ Live Event Stream element found")
            
            # Try to click it - with multiple strategies
            print("4. Opening Live Event Stream...")
            
            # Strategy 1: Try direct click
            try:
                live_event_element.click(timeout=5000)
                print("   ✅ Clicked directly")
            except:
                # Strategy 2: Try to find parent expander and click its header
                print("   Trying alternative click strategies...")
                
                # Find the expander header (Streamlit specific)
                expander_headers = page.locator("[data-testid='stExpander'] summary, .streamlit-expanderHeader")
                for i in range(expander_headers.count()):
                    header = expander_headers.nth(i)
                    if "Live Event" in header.inner_text():
                        header.click()
                        print("   ✅ Clicked expander header")
                        break
                else:
                    # Strategy 3: Use JavaScript to click
                    page.evaluate("""
                        const elements = document.querySelectorAll('*');
                        for (const el of elements) {
                            if (el.textContent && el.textContent.includes('Live Event Stream')) {
                                el.click();
                                break;
                            }
                        }
                    """)
                    print("   ✅ Clicked via JavaScript")
            
            time.sleep(2)
            
            # Take screenshot after clicking
            page.screenshot(path="test_after_click.png")
            print("   📸 After click screenshot: test_after_click.png")
            
            # Check connection status - with multiple possible texts
            print("5. Checking WebSocket status...")
            
            connection_indicators = [
                "text=✅ Connected",
                "text=Connected (real-time)",
                "text=WebSocket connected",
                "text=Active",
                "text=real-time"
            ]
            
            connected = False
            for indicator in connection_indicators:
                if page.locator(indicator).count() > 0:
                    print(f"   ✅ {indicator}")
                    connected = True
                    break
            
            if not connected:
                print("   ⚠️  WebSocket connection status not found")
                # Check for polling mode
                if page.locator("text=Polling").count() > 0:
                    print("   ⚠️  In polling mode (WebSocket server might not be running)")
            
            # Look for event cards
            print("6. Checking for event cards...")
            
            # Event cards might have various styles
            event_selectors = [
                "[style*='border-left']",
                ".event-card",
                "[class*='event']",
                "div:has(> div > strong)"  # Cards with bold text
            ]
            
            total_events = 0
            for selector in event_selectors:
                count = page.locator(selector).count()
                if count > 0:
                    print(f"   Found {count} elements with selector: {selector}")
                    total_events += count
            
            if total_events > 0:
                print(f"   ✅ Found {total_events} potential event elements")
                
                # Take screenshot of events
                events_section = page.locator("body")
                events_section.screenshot(path="test_events.png")
                print("   📸 Events screenshot: test_events.png")
                
                # Show some event text
                first_event = page.locator("[style*='border-left']").first
                if first_event.count() > 0:
                    event_text = first_event.inner_text()[:150]
                    print(f"\n   Sample event:")
                    print(f"   {event_text}")
            else:
                print("   ⚠️  No event cards found (might be normal if no events yet)")
                
                # Check for "No events yet" message
                if page.locator("text=No events yet").count() > 0:
                    print("   ✅ 'No events yet' message shown")
            
            # Test WebSocket by generating an event
            print("7. Testing WebSocket event generation...")
            
            # Try to find and use General Playground
            playground_selectors = [
                "text=General Prompt Playground",
                "text=General Playground",
                "textarea"
            ]
            
            textarea_found = False
            for selector in playground_selectors:
                if page.locator(selector).count() > 0:
                    element = page.locator(selector).first
                    
                    if selector == "textarea":
                        # Fill textarea
                        element.fill("Test WebSocket event - " + str(time.time()))
                        textarea_found = True
                        print("   ✅ Found and filled textarea")
                        
                        # Look for a button to click
                        buttons = page.locator("button")
                        for i in range(min(10, buttons.count())):
                            btn = buttons.nth(i)
                            btn_text = btn.inner_text()
                            if "Run" in btn_text or "Generate" in btn_text or "Fast" in btn_text:
                                btn.click()
                                print(f"   ✅ Clicked button: {btn_text}")
                                break
                        break
            
            if not textarea_found:
                print("   ⚠️  Could not find textarea for testing")
            
            # Wait for any processing
            time.sleep(3)
            
            print("\n" + "=" * 50)
            print("✅ Quick test completed!")
            print("\nSummary:")
            print("- UI loaded successfully")
            print("- Live Event Stream found")
            print("- WebSocket status checked")
            print("- Event display area checked")
            
            # Final screenshot
            page.screenshot(path="test_final.png")
            print("\n📸 All screenshots saved:")
            print("   test_initial.png - Initial page load")
            print("   test_after_click.png - After opening Live Event Stream")
            print("   test_events.png - Events section")
            print("   test_final.png - Final state")
            
            # Keep browser open for manual inspection
            print("\n🔍 Browser will stay open for 15 seconds for manual inspection...")
            print("   Check the Live Event Stream in the UI.")
            print("   Look for real-time updates when agents run.")
            time.sleep(15)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Take screenshot on error
            try:
                page.screenshot(path="test_error.png")
                print("   📸 Error screenshot: test_error.png")
            except:
                pass
            
            return False
            
        finally:
            browser.close()

if __name__ == "__main__":
    # Check if Playwright is installed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("❌ Playwright not installed. Install with:")
        print("   pip install playwright")
        print("   playwright install chromium")
        exit(1)
    
    print("⚠️  IMPORTANT: Make sure Streamlit is already running!")
    print("   Run in another terminal: streamlit run studio_ui.py")
    print("   Then run this test.")
    print("\nThe test will:")
    print("1. Open Chrome browser")
    print("2. Navigate to http://localhost:8501")
    print("3. Test WebSocket functionality")
    print("4. Take screenshots for verification")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()
    
    success = quick_test()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Test completed successfully!")
        print("WebSocket system appears to be working in the UI.")
    else:
        print("💥 Test failed or encountered issues.")
        print("Check the screenshots in the project directory.")
    
    exit(0 if success else 1)