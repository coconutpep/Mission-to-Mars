#Import Dependencies
from bs4 import BeautifulSoup as bs
import pandas as pd
from splinter import Browser
from flask import Flask, render_template
import pymongo

#def function to scrape data
def scrape():
    #Scrape NASA Mars News Site
    #Set the executable path
    executable_path = {'executable_path':'../../chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    #Set the url to visit
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)
    #Set up BeautifulSoup object
    html = browser.html
    soup = bs(html, 'html.parser')
    #Scrape Latest News Article
    #Scrape Title
    article = soup.find('div', class_='list_text')
    news_title = article.find('a').text
    #Scrape article text
    news_p = article.find('div', class_='article_teaser_body').text

    #Have splinter go to site for image scraping
    url2 = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url2)
    #Reset Beautiful Soup
    html2 = browser.html
    soup2 = bs(html2, 'html.parser')
    #Scrape main image
    img_style = soup2.find('article', class_='carousel_item')['style']
    img_path = img_style[22:(len(img_style)-2)]
    featured_image_url = url2 + img_path

    #Set spliter to Mars Weather Twitter
    #url3 = 'https://twitter.com/marswxreport?lang=en'
    #browser.visit(url3)
    #Reset Beautiful Soup
    #html3 = browser.html
    #soup3 = bs(html3, 'html.parser')
    #Scrape weather information
    #soup3.body.find_all('span', class_='css-901oao css-16my406z').text
    #This should work but bs can't seem to parse twitter's page

    #Scrape Mars Facts page tables
    url4 = 'https://space-facts.com/mars/'
    tables = pd.read_html(url4)

    #scrape hemispere images from USGS
    #reset splinter 
    url5 = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url5)
    #Set bs
    html5 = browser.html
    soup5 = bs(html5, 'html.parser')
    #Create list of hemispheres
    hemispheres = soup5.find_all('h3')
    hemispheres_text = [hemisphere.text for hemisphere in hemispheres]
    #Create list of link urls
    links = soup5.find_all('a', class_='itemLink product-item')
    url_links = links[2::2]
    linkIndex = 1
    #Parse through hemisphere list to pull images and create dictionaries
    hemisphere_image_urls = []
    for hemisphere in hemispheres_text:
        #Set hemisphere dict
        hemisphere_dict = {}
        #Set hemisphere title
        hemisphere_dict['title'] = hemisphere
        #Move to hemisphere page
        browser.click_link_by_partial_text(hemisphere)
        #Set bs
        htmlhemi = browser.html
        souphemi = bs(htmlhemi, 'html.parser')
        #Scrape image path
        img_path = souphemi.find('img', class_='wide-image')['src']
        #Set image url
        img_url = 'https://astrogeology.usgs.gov/search/map/Mars/Viking/' + url_links[linkIndex]['href'] + img_path
        hemisphere_dict['img_url'] = img_url
        hemisphere_image_urls.append(hemisphere_dict)
        #Return to homepage
        browser.visit(url5)
    #Close browser
    browser.quit

    dictionary = {
        'news_title':news_title,
        'news_p':news_p,
        'featured_img_url':featured_image_url,
        'table':tables[0],
        'hemisphere_dict':hemisphere_image_urls
    }
    return dictionary

#set up flask app
app = Flask(__name__)

#create Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_db")

@app.route('/')
def home():
    pass

@app.route("/scrape")
def scraper():

    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)