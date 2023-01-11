# Import Splinter and Browser
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import pendulum

executable_path = {'executable_path': ChromeDriverManager().install()}
# -- Scrape All --
def scrape_all():
    # Initiate headless driver for deployment
    
    browser = Browser('chrome', **executable_path, headless=True)

    # Setting our Title and Paragraph to variables
    news_title, news_paragraph = mars_news(browser)
    # Scrape Hemisphere facts and images
    hemisphere_images = mars_hemisphere(browser)
    # Run all scraping functions and store results in dictionary
    data = {
      "news_title": news_title,
      "news_paragraph": news_paragraph,
      "featured_image": featured_image(browser),
      "facts": mars_facts(),
      "last_modified": pendulum.now(),
      "hemispheres" : hemisphere_images
    }
    # Stop webdriver and return data
    browser.quit()
    return data

# -- Mars News --
def mars_news(browser):
    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p
   

 # --Featured Images-- 
def featured_image(browser):
    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image')['src']

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# --Mars Facts--
def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    # Convert dataframe into HTML format
    df = df.to_html()
    
    # Center the converted df, add bootstrap
    return df.replace('<tr>', '<tr align="center">')

def mars_hemisphere(browser):
    url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(url)
    hemisphere_img_url = []
    html = browser.html
    h_soup = soup(html, 'html.parser')

    # Get the links for each of the 4 hemispheres
    h_links = h_soup.find_all('h3')

    # Loop throup the the four links to click on the page 
    # and retrieve the information
    for h in h_links:
        h_page = browser.find_by_text(h.text)
        h_page.click()
        html = browser.html
        sp = soup(html, 'html.parser')
        # Scrape the image link and add the initail part to the link
        img_url = 'https://astrogeology.usgs.gov/' + str(sp.find('img', class_='wide-image')['src'])
        # Scrape the title
        title = sp.find('h2', class_='title').text
        h_dict = {'image_url' : img_url, 'title' : title}
        hemisphere_img_url.append(h_dict)
        browser.back()

    return hemisphere_img_url


if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())