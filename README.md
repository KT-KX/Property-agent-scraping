
# Property Agents Scraper

## Overview
This project is a web scraping tool that collects property agent information from the PropertyGuru Malaysia website. The collected data is stored in an Excel file for further analysis.

## Features
- Scrapes agent details such as name, company, active listings, phone number, registration number, and areas of expertise.
- Handles pagination to scrape multiple pages.
- Uses Selenium WebDriver to automate browser interactions.
- Implements random sleep intervals to mimic human behavior and avoid detection.
- Saves collected data into an Excel file.

## Technologies Used
- Python 3
- Selenium WebDriver
- Pandas
- Regular Expressions (re)
- WebDriverWait for dynamic page interactions

## Requirements
### Prerequisites
Ensure you have the following installed:
- Python 3.7+
- Google Chrome browser
- ChromeDriver (compatible with your Chrome version)

### Python Dependencies
Install the required Python libraries using:
```bash
pip install selenium pandas openpyxl
```

## Setup Instructions
1. Clone this repository:
   ```bash
   git clone https://github.com/KT-KX/Property-agent-scraping.git
   cd property-agents-scraper
   ```

2. Download ChromeDriver and update the path in `scrape_agents()` function:
   ```python
   driverpath = r"path/to/chromedriver.exe"
   ```

3. Run the scraper script:
   ```bash
   python scraper.py
   ```

4. The output will be saved as `property_agents_detailed.xlsx` in the project directory.

## Script Breakdown
### `setup_driver()`
Configures the Chrome WebDriver with options to run in incognito mode, disable automation detection, and set user-agent.

### `random_sleep()`
Introduces a random delay between operations to avoid detection.

### `get_agent_url()`
Extracts the agent's profile URL using different CSS selectors.

### `go_to_page()`
Handles pagination by clicking buttons or modifying the URL directly.

### `scrape_agent_details()`
Scrapes details like experience, phone number, registration number, and areas of expertise from the agent's profile page.

### `scrape_agents()`
Handles the overall scraping process by navigating through pages, collecting agent data, and saving it.

### `save_to_excel()`
Saves the collected data into an Excel file.

## Error Handling
- If an agent's URL is unavailable, it is skipped.
- Exception handling is implemented at multiple levels to ensure script continuity.

## Potential Improvements
- Implement multithreading to speed up scraping.
- Integrate proxy rotation to avoid IP bans.
- Add logging for better debugging.

## License
This project is licensed under the MIT License.

## Author
- Eng Kuan Tian
