from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# def constructConnect(event, context):
#     options = Options()
#     options.binary_location = '/opt/headless-chromium'
#     options.add_argument('--headless')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--single-process')
#     options.add_argument('--disable-dev-shm-usage')

#     driver = webdriver.Chrome('/opt/chromedriver',chrome_options=options)

#     driver.get('https://www.neaminational.org.au/')
#     body = f"Headless Chrome Initialized, Page title: {driver.title}"

#     driver.close()
#     driver.quit()

#     response = {
#         "statusCode": 200,
#         "body": body
#     }

#     return response

import html
import io
import json
import logging
import os
import unicodedata
import time
import shutil
import uuid
import boto3
import requests
import re

def constructConnect(event, context):
    try:
        logger=logging.getLogger(__name__)
        # handler = logging.FileHandler('logger.info', 'w', 'utf-8')
        # logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        logger.info("------------------------ login --------------------------")

        username = "eddie.trejo@polkmechanical.com"
        password = "Mexico6*"

        tempDownloadDir = '/tmp/isqft'
        if not os.path.exists(tempDownloadDir):
            os.makedirs(tempDownloadDir)

        chrome_options = webdriver.ChromeOptions()
        _tmp_folder = '/tmp/{}'.format(uuid.uuid4())

        if not os.path.exists(_tmp_folder):
            os.makedirs(_tmp_folder)

        if not os.path.exists(_tmp_folder + '/user-data'):
            os.makedirs(_tmp_folder + '/user-data')

        if not os.path.exists(_tmp_folder + '/data-path'):
            os.makedirs(_tmp_folder + '/data-path')

        if not os.path.exists(_tmp_folder + '/cache-dir'):
            os.makedirs(_tmp_folder + '/cache-dir')

        prefs = {
            'download.default_directory': tempDownloadDir,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': False,
            'safebrowsing.disable_download_protection': True,
            'profile.default_content_setting_values.automatic_downloads': 1
        }

        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_experimental_option('w3c', False)

        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--window-size=1280x1696')
        chrome_options.add_argument('--user-data-dir={}'.format(_tmp_folder + '/user-data'))
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--data-path={}'.format(_tmp_folder + '/data-path'))
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--homedir={}'.format(_tmp_folder))
        chrome_options.add_argument('--disk-cache-dir={}'.format(_tmp_folder + '/cache-dir'))
        chrome_options.add_argument('--disable-dev-shm-usage')

        chrome_options.binary_location = "/opt/headless-chromium"

        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities['loggingPrefs'] = {'performance': 'ALL'}
        # chrome version 75+
        # desired_capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        driver = webdriver.Chrome('/opt/chromedriver', chrome_options=chrome_options, desired_capabilities=desired_capabilities)

        # enable_download_in_headless_chrome
        """
        This function was pulled from
        https://github.com/shawnbutton/PythonHeadlessChrome/blob/master/driver_builder.py#L44
        There is currently a "feature" in chrome where
        headless does not allow file download: https://bugs.chromium.org/p/chromium/issues/detail?id=696481
        Specifically this comment ( https://bugs.chromium.org/p/chromium/issues/detail?id=696481#c157 )
        saved the day by highlighting that download wasn't working because it was opening up in another tab.
        This method is a hacky work-around until the official chromedriver support for this.
        Requires chrome version 62.0.3196.0 or above.
        """
        driver.execute_script(
            "var x = document.getElementsByTagName('a'); var i; for (i = 0; i < x.length; i++) { x[i].target = '_self'; }")
        # add missing support for chrome "send_command"  to selenium webdriver
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')

        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': tempDownloadDir}}
        command_result = driver.execute("send_command", params)
        logger.info("response from browser:")
        for key in command_result:
            logger.info("result:" + key + ":" + str(command_result[key]))


        url = "https://app.isqft.com/services/Access/GetUserQANAccess?sourceType=2&Id=SNQFYHJ1&ProjectID=6331543"
        m = re.search('https://app.isqft.com/.*ProjectID=(\d+)', url)
        projectID = m.group(1)
        logger.info("Project ID = {}" .format(projectID))
        driver.get(url)
        time.sleep(3)

        logger.info("------------------------ enteremail --------------------------")
        usernameElement = driver.find_element_by_css_selector("input[id='emailInput']")
        logger.info("usernameElement = {}" .format(usernameElement))
        usernameElement.clear()
        usernameElement.send_keys(username)

        submitElement = driver.find_element_by_css_selector("input[id='submitButton']")
        submitElement.click()
        time.sleep(6)

        logger.info("------------------------ access --------------------------")
        loginNowElement = driver.find_element_by_css_selector("a")
        loginNowElement.click()
        time.sleep(3)

        logger.info("------------------------ login --------------------------")
        usernameElement = driver.find_element_by_css_selector("input[name='email']")
        logger.info("usernameElement = {}" .format(usernameElement))
        usernameElement.clear()
        usernameElement.send_keys(username)

        passwordElement = driver.find_element_by_css_selector("input[name='password']")
        logger.info("passwordElement = {}" .format(passwordElement))
        passwordElement.clear()
        passwordElement.send_keys(password)

        submitElement = driver.find_element_by_css_selector("button[type='submit']")
        submitElement.click()

        time.sleep(40)

        # This can't be used in selenium. To use this, we should use seleniumwire but seleniumwire isn't supported in AWS.
        # logger.info("------------------------ capturing all requests --------------------------")
        # for request in driver.requests:

        #     # logger.info("request.url = {}".format(request.url)) # <--------------- Request url
        #     # logger.info("request.response.headers = {}".format(request.response.headers)) # <-- Response headers

        #     if(request.url.endswith('getProjectData')):
        #         logger.info("------------------------ GetProjectData --------------------------")
        #         projectData = request.response.body
        #         logger.info("projectData = {}".format(projectData))

        #     if(request.url.endswith('getContactsList')):
        #         logger.info("------------------------ GetContactsList --------------------------")
        #         contactsList = request.response.body
        #         logger.info("contactsList = {}".format(contactsList))

        #     if(request.url.endswith('getDesignTeam')):
        #         logger.info("------------------------ GetDesignTeam --------------------------")
        #         designTeam = request.response.body
        #         logger.info("designTeam = {}".format(designTeam))

        #     if(request.url.endswith('getProjectTrades')):
        #         logger.info("------------------------ GetProjectTrades --------------------------")
        #         projectTrades = request.response.body
        #         logger.info("projectTrades = {}".format(projectTrades))

        #     if(request.url.endswith('getPublicProjectParticipants')):
        #         logger.info("------------------------ GetPublicProjectParticipants --------------------------")
        #         publicProjectParticipants = request.response.body
        #         logger.info("publicProjectParticipants = {}".format(publicProjectParticipants))

        #     if(request.url.endswith('getProjectDocumentList')):
        #         logger.info("------------------------ GetProjectDocumentList --------------------------")
        #         projectDocumentList = request.response.body
        #         logger.info("projectDocumentList = {}".format(projectDocumentList))

        #     if(request.url.endswith('getCompanyProfile')):
        #         logger.info("------------------------ GetCompanyProfile --------------------------")
        #         companyProfile = request.response.body
        #         logger.info("companyProfile = {}".format(companyProfile))

        #     if(request.url.endswith('getContactInfo')):
        #         logger.info("------------------------ GetContactInfo --------------------------")
        #         contactInfo = request.response.body
        #         logger.info("contactInfo = {}".format(contactInfo))


        logger.info("------------------------ view/download --------------------------")
        viewDocumentElement = driver.find_element_by_xpath(".//*[starts-with(@class, 'ProjectDocumentSummary--viewDocumentsBtn')]")
        viewDocumentElement.click()

        time.sleep(60)
        logger.info("------------------------ switch to active tab --------------------------")
        driver.switch_to_window(driver.window_handles[1])

        logger.info("------------------------ download --------------------------")
        # downloadElements = driver.find_elements_by_css_selector("button")
        # for element in downloadElements:
        #     logger.info("companyProfile = {}".format(element.get_attribute("class")))
        downloadElement = driver.find_element_by_css_selector(".takeoff-control__download-button")
        logger.info("downloadElement = {}" .format(downloadElement))
        downloadElement.click()
        time.sleep(2)

        driver.save_screenshot(tempDownloadDir + '/screenshot1.png')
        logger.info("------------------------ waiting until completing the download --------------------------")
        while(not downloadElement.is_enabled()):
            pass

        driver.save_screenshot(tempDownloadDir + '/screenshot2.png')

        # getting the screenshots to see what happened.
        s3_client = boto3.client('s3', region_name='us-east-1') 
        s3_client.upload_file(tempDownloadDir + '/screenshot1.png', 'selenium-dev-download-bucket', 'screenshots/1.png')
        s3_client.upload_file(tempDownloadDir + '/screenshot2.png', 'selenium-dev-download-bucket', 'screenshots/2.png')

        if os.path.exists(tempDownloadDir + '/screenshot1.png'): 
            os.remove(tempDownloadDir + '/screenshot1.png')
        else:
            logger.info("screenshot1 doesn't exist!")
        if os.path.exists(tempDownloadDir + '/screenshot2.png'):
            os.remove(tempDownloadDir + '/screenshot2.png')
        else:
            logger.info("screenshot2 doesn't exist!")

        logger.info("------------------------ capturing all requests --------------------------")
        
        browser_log = driver.get_log('performance') 
        events = [json.loads(entry['message'])['message'] for entry in browser_log]
        downloadUrl = ''
        bearerToken = ''
        for event in events:
            logger.info(event)
            if 'request' in event['params'] and 'headers' in event['params']['request'] and 'Authorization' in event['params']['request']['headers'] and 'Bearer ' in event['params']['request']['headers']['Authorization']:
                bearerToken = event['params']['request']['headers']['Authorization']
            if 'Network.response' in event['method'] and 'response' in event['params'] and 'url' in event['params']['response'] and 'https://app.isqft.com/services/file/GetProcessStream/' in event['params']['response']['url']:
                downloadUrl = event['params']['response']['url']

        logger.info("downloadUrl = {}" .format(downloadUrl))
        logger.info("bearerToken = {}" .format(bearerToken))

        logger.info("------------------------Download Stream File --------------------------")      
        headers = {
            'Authorization': bearerToken
        }

        response = requests.get(downloadUrl, headers=headers, stream=True)

        logger.info("Return status = {}" .format(response.status_code))
        fileName = tempDownloadDir + '/' + projectID + '.zip'
        if(response.status_code == 200):
            with open(fileName,'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)

        s3_client.upload_file(fileName, 'selenium-dev-download-bucket', projectID + '.zip')
        
        if os.path.exists(fileName): 
            os.remove(fileName)
        else:
            logger.info("{} doesn't exist!".format(fileName))

        driver.close()
        driver.quit()

        return {
            "statusCode": 200,
            "body": "success"
        }

    except Exception as e:
        logger.exception("ERROR in constructConnect processing routine {}" .format(e))
        response = {
            "statusCode": 500,
            "body": "failure"
        }

        return response
