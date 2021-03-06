import requests

from scrapy import Spider, Request, log
from scrapy.selector import Selector

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from utils.sql import get_session
from utils.sql.models.course_unit import CourseUnit
from utils.sql.models.course_video import CourseVideo

from scraper.edx_bot.spiders import EdXLoggerIn
from scraper.edx_bot.spiders.general_course_content import GeneralCourseContent

from scraper.edx_bot.items import CourseVideoItem


class VideoTranscripts(Spider):
    name = 'video_transcripts'
    allowed_domains = ['edx.org']
    session = None

    def start_requests(self):
        self.session = get_session()
        self.edx_logger = EdXLoggerIn()

        driver = self.edx_logger.driver
        driver.maximize_window()

        for video_id in self.session.query(CourseVideo.id).filter(\
            CourseVideo.transcript == None):

            # Get a unit corresponding to that video. Though there may
            # be multiple units that host that video, the transcripts
            # should be similar across all... therefore the first unit
            # should allow us to get the transcript.
            unit_href = self.session.query(CourseUnit.href).filter(\
                CourseUnit.videos.any(CourseVideo.id == video_id)).first()

            yield Request(
                url = unit_href[0],
                meta = {'video_id':video_id[0]},
                cookies = driver.get_cookies(),
                callback = self.fetch_transcript
            )


    def fetch_transcript(self, response):
        driver = self.edx_logger.driver
        driver.get(response.url)

        sequence_el = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="seq_content"]')))

        for module in sequence_el.find_elements_by_xpath('.//div/div/div'):
            data_type = module.get_attribute('data-block-type')

            if data_type == 'video':
                try:
                    for download_button in module.find_elements_by_class_name('video-download-button'):
                        sub_element = download_button.find_element_by_xpath('.//a')
                        if sub_element.text == 'Download transcript':
                            transcript_href = sub_element.get_attribute('href')

                            msg = "Got transcript url=%s" % (transcript_href)
                            log.msg(msg, level=log.INFO)

                            return self.parse_transcript(transcript_href, \
                                driver.get_cookies(), meta = response.meta)

                except NoSuchElementException:
                    msg = "No txt transcript found for video in unit with url=%s" \
                        % (response.url)
                    log.msg(msg, level=log.INFO)

        return None


    def parse_transcript(self, transcript_href, driver_cookies, meta):
        cookies = {d['name']:d['value'] for d in driver_cookies}
        r = requests.get(transcript_href, cookies=cookies)

        return CourseVideoItem(
            _id = meta['video_id'],
            transcript = r.text
        )


    def closed(self, reason):
        self.session.close()
        self.edx_logger.close()
