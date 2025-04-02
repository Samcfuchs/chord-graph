# %%
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException

from tqdm import tqdm
import json

# %% [markdown]
# ## Grab Links
# 
# First, we need a list of tabs. We can use the total hits ranking to get a bunch of links quickly.

# %%
URL = "https://www.ultimate-guitar.com/explore?order=hitstotal_desc&page={}&type[]=Chords"
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=2560,1440")

driver = webdriver.Chrome(options=chrome_options)
driver.get(URL.format(0))

# %%
URL = "https://www.ultimate-guitar.com/explore?order=hitstotal_desc&page={}&type[]=Chords"
def get_page_links(page_number):
    driver.get(URL.format(page_number))
    elements = driver.find_elements(By.TAG_NAME, 'article')
    table = elements[1] # this will *probably* work. It's a magic number

    elements = table.find_elements(By.TAG_NAME, 'a')
    links = [e.get_property('href') for e in elements]

    artist_links = list(filter(lambda s: '/artist/' in s, links))
    page_links = list(filter(lambda s: '/tab/' in s, links))

    return artist_links, page_links

# %%
# get_page_links(0)

# %%
# all_artist_links = []
# all_tab_links = []
# for i in tqdm(range(0,101)):
    # artist_links, page_links = get_page_links(i)
# 
    # all_artist_links += artist_links
    # all_tab_links += page_links

# %% [markdown]
# I'll save this data, because I'm getting some refused connections from UG, which means they could be blocking my parser.

# %%
# import json

# with open('data/tab_links.json','w') as f:
    # json.dump(all_tab_links, f)

# %% [markdown]
# ## Chord Extraction
# 
# Now that we have page links, we can check those pages and extract the data.


# %%

def get_song_data(URL):
    driver.get(URL)
    #ActionChains(driver).scroll_by_amount(0,10000).perform()

    elements = driver.find_elements(By.CSS_SELECTOR, 'code pre span')
    try:
        key = driver.find_element(By.XPATH, "//tr/th[contains(text(),'Key')]/../td").text
    except NoSuchElementException:
        key = '?'

    data = {
        'link': URL,
        'artist': None,
        'title': None,
        'key': key,
        'text_chords': [e.text for e in elements],
        'prop_chords': [e.get_attribute('data-name') for e in elements]
    }

    return data


with open('data/tab_links.json', 'r') as f:
    all_tab_links = json.load(f)


# %%
all_data = []
chunk = []
n = 0
for tab_link in tqdm(all_tab_links):
    chunk.append(get_song_data(tab_link))


    if len(chunk) > 1000:
        n += 1
        all_data += chunk
        with open(f'data/chunk{n}.json', 'w') as f:
            json.dump(chunk, f)
        
        chunk = []

        print(f'Finished chunk {n}')

print(len(all_data))   
