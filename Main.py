from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time
import pandas as pd
from datetime import datetime
import random
import re
# Function to set up the Chrome driver with required options to avoid bot detection
def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    
    # Enable incognito mode and disable automation flags for smoother scraping
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option("detach", True)
    
    # Set a user-agent to simulate browser traffic
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    return chrome_options

# Function to introduce random sleep times to mimic human behaviour
def random_sleep(min_time=3, max_time=6):
    time.sleep(random.uniform(min_time, max_time))
  

# Function to extract agent profile URL using multiple selectors
def get_agent_url(agent, browser):
    try:
        # Try multiple selectors to find the URL
        selectors = [
            "a.agent-contact",
            "a.agent-info-name",
            "div.agent-card a"
        ]
        
        for selector in selectors:
            try:
                element = agent.find_element(By.CSS_SELECTOR, selector)
                url = element.get_attribute('href')
                if url:
                    return url
            except:
                continue
        
        return "Not available"
    except Exception as e:
        print(f"Error getting URL: {str(e)}")
        return "Not available"

# Function to navigate to a specific page using pagination
def go_to_page(browser, page_number):
    try:
        # Scroll to bottom of page to ensure pagination is visible
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        random_sleep(2, 3)

        # Check if the page is already correct
        current_url = browser.current_url
        if f"page={page_number}" in current_url:
            print(f"Already on page {page_number}")
            return True

        # Try multiple ways to click pagination button
        selectors = [
            f"//a[contains(@class, 'pagination') and text()='{page_number}']",
            f"//div[contains(@class, 'pagination')]//a[text()='{page_number}']",
            f"//ul[contains(@class, 'pagination')]//a[text()='{page_number}']",
            f"//button[contains(@class, 'pagination') and text()='{page_number}']"
        ]

        for selector in selectors:
            try:
                page_button = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, selector)))
                browser.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", page_button)
                random_sleep(2, 3)
                
                # Try normal click first, then fallback to JS click
                try:
                    page_button.click()
                except:
                    browser.execute_script("arguments[0].click();", page_button)

                print(f"Clicked on page {page_number}")
                random_sleep(4, 6)

                # Ensure content is refreshed
                WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "agent-card")))
                return True
            except:
                continue

        # If pagination button click fails, modify the URL
        if 'page=' in current_url:
            new_url = re.sub(r'page=\d+', f'page={page_number}', current_url)
        else:
            new_url = f"{current_url}&page={page_number}" if '?' in current_url else f"{current_url}?page={page_number}"

        browser.get(new_url)
        random_sleep(4, 6)
        browser.refresh()  # Ensure the page loads fresh content
        return True

    except Exception as e:
        print(f"Error navigating to page {page_number}: {str(e)}")
        return False

      
def scrape_agent_details(browser, url):
    """
    Scrapes detailed information from an individual agent's page
    """
    if url == "Not available":
        return {}
        
    try:
        browser.get(url)
        random_sleep(3, 5)
        
        details = {}
        # Extracting page source and searching for phone numbers
        page_source = browser.page_source
        
        # Look for phone number in script content
        import re

        # Wait for the agent details to load
        wait = WebDriverWait(browser, 10)
        
        try:
            # Get agent's years of experience
            experience = browser.find_element(By.CSS_SELECTOR, "span[data-automation-id='stat-years-with-pg']").text
            details['Experience'] = experience.strip()
        except:
            details['Experience'] = "Not available"
            
        try:
            # Get agent's phone number (if visible)
            phone_pattern = r'"mobilePretty":"\+?[\d\s]+"'
            phone_matches = re.findall(phone_pattern, page_source)
        
            if phone_matches:
                phone_number = phone_matches[0].split(":")[1].strip('"')
                details['Phone'] = phone_number
        except:
            details['Phone'] = "Not available"
            
        try:
            reg_type = browser.find_element(By.CSS_SELECTOR, "span[data-automation-id='agent-detail-license-name']").text
            reg_number = browser.find_element(By.CSS_SELECTOR, "span[data-automation-id='agent-detail-agent-license-formatted']").text
            details['Registration'] = f"{reg_type} {reg_number}".strip()
        except:
            details['Registration'] = "Not available"
            
        try:
            # Get areas of expertise
            show_more_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.show-more-item[data-automation-id='map-regions-show-more']"))
            )
            # Use JavaScript click to ensure it works
            browser.execute_script("arguments[0].click();", show_more_button)
            
            # Wait for additional regions to load
            random_sleep(2, 3)
    
            expertise = browser.find_elements(By.CSS_SELECTOR, "div.region-item label")
            details['Areas'] = ", ".join([area.text.strip() for area in expertise if area.text.strip()])
        except:
            details['Areas'] = "Not available"
        
        try:
            # Wait until the element is available
            wait = WebDriverWait(browser, 10)
            source_of_contact = wait.until(EC.presence_of_element_located((By.ID, "footer-guru-info-label-1")))
        
            # Extract the label (text of the anchor tag)
            label_text = source_of_contact.text.strip()
            details['Source_of_contact'] = label_text
            


        except TimeoutException:
            details['Source_of_contact'] = "Not available"
        except Exception as e:
            details['Source_of_contact'] = "Not available"
        
        return details
        
    except Exception as e:
        print(f"Error scraping agent details: {str(e)}")
        return {}

def scrape_agents():
    driverpath = r"D:\XMUM DEGREE\Udemy\Data Collection\chromedriver-win64\chromedriver-win64\chromedriver.exe"
    chrome_options = setup_driver()
    service = Service(driverpath)
    browser = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        main_url = 'https://www.propertyguru.com.my/property-agents/kuala-lumpur'
        browser.get(main_url)
        print("Waiting for initial page load...")
        random_sleep(5, 8)
        
        data_list = []
        current_page = 1
        max_pages = 100
        
        while current_page <= max_pages:
            print(f"Scraping page {current_page}...")
            
            # Create the paginated URL
            if current_page > 1:
                paginated_url = f"{main_url}/{current_page}"
            else:
                paginated_url = main_url
            
            # Store all agents on the current page first
            wait = WebDriverWait(browser, 15)
            agents = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "agent-card")))
            
            if not agents:
                print("No agents found on this page, stopping...")
                break
            
            # Store agent data for the current page
            page_agents_data = []
            for agent in agents:
                try:
                    name = agent.find_element(By.CLASS_NAME, "agent-info-name").text
                    company = agent.find_element(By.CLASS_NAME, "agent-info-description").text
                    listings = agent.find_element(By.CSS_SELECTOR, ".agent-info-listing.hidden-xs").text
                    url = get_agent_url(agent, browser)
                    
                    page_agents_data.append({
                        'name': name,
                        'company': company,
                        'listings': listings,
                        'url': url
                    })
                except Exception as e:
                    print(f"Error collecting basic agent data: {str(e)}")
                    continue
            
            # Now process each agent's details
            for i, agent_data in enumerate(page_agents_data, 1):
                try:
                    print(f"Processing agent {i} on page {current_page}")
                    
                    # Get detailed information
                    print(f"Scraping detailed information for {agent_data['name']}...")
                    agent_details = scrape_agent_details(browser, agent_data['url'])
                    
                    # Return directly to the current page using the paginated URL
                    browser.get(paginated_url)
                    random_sleep(2, 3)
                    
                    data_collected_date = datetime.now().strftime('%Y-%m-%d')
                    
                    # Combine basic and detailed information
                    agent_full_data = [
                        agent_data['name'],
                        agent_data['company'],
                        agent_data['listings'],
                        agent_data['url'],
                        agent_details.get('Experience', 'Not available'),
                        agent_details.get('Phone', 'Not available'),
                        agent_details.get('Registration', 'Not available'),
                        agent_details.get('Areas', 'Not available'),
                        agent_details.get('Source_of_contact', "Not available"),    
                        data_collected_date
                    ]
                    
                    data_list.append(agent_full_data)
                    print(f"Successfully collected detailed data for: {agent_data['name']}")
                    
                except Exception as e:
                    print(f"Error processing agent: {str(e)}")
                    continue
            
            # Move to next page after processing all agents on current page
            current_page += 1
            if current_page <= max_pages:
                paginated_url = f"https://www.propertyguru.com.my/property-agents/kuala-lumpur/{current_page}"
                browser.get(paginated_url)
                # if not go_to_page(browser, current_page):
                #     print("Failed to navigate to next page, stopping...")
                #     break
                WebDriverWait(browser, 10).until(EC.staleness_of(agents[0]))  

                random_sleep(4, 6)
            
        return data_list
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return data_list
    finally:
        print("Scraping completed. Browser will remain open for inspection.")
        pass

def save_to_excel(data_list):
    if not data_list:
        print("No data to save!")
        return
        
    df = pd.DataFrame(data_list, columns=[
        "Agent Name", 
        "Company", 
        "Active Listings", 
        "URL", 
        "Experience",
        "Phone Number",
        "Registration Number",
        "Areas of Expertise",
        "Source of Contact",
        "Data Collected Date"
        
    ])
    df.to_excel("property_agents_detailed.xlsx", index=False)
    print(f"Data successfully saved to Excel! Total agents scraped: {len(data_list)}")

if __name__ == "__main__":
    data_list = scrape_agents()
    save_to_excel(data_list)