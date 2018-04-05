"""zhihu.py"""

# -*- coding: utf-8 -*-
import json

from scrapy import Request, Spider

from zhihu_user.items import UserItem


class ZhihuSpider(Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com']

    # 起始用户的url_token
    start_user = 'excited-vczh'

    # 每个用户信息的url和请求参数
    user_url = 'https://www.zhihu.com/api/v4/members/{user}?include={include}'
    user_query = "locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,avatar_hue,answer_count,articles_count,pins_count,question_count,columns_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_bind_phone,is_force_renamed,is_bind_sina,is_privacy_protected,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics"
    # user_query = 'locations,employments,gender,educations,business,voteup_count,thanked_Count,follower_count,following_count,cover_url,following_topic_count,following_question_count,following_favlists_count,following_columns_count,answer_count,articles_count,pins_count,question_count,commercial_question_count,favorite_count,favorited_count,logs_count,marked_answers_count,marked_answers_text,message_thread_token,account_status,is_active,is_force_renamed,is_bind_sina,sina_weibo_url,sina_weibo_name,show_sina_weibo,is_blocking,is_blocked,is_following,is_followed,mutual_followees_count,vote_to_count,vote_from_count,thank_to_count,thank_from_count,thanked_count,description,hosted_live_count,participated_live_count,allow_message,industry_category,org_name,org_homepage,badge[?(type=best_answerer)].topics'
    # user_query = 'allow_message,is_followed,is_following,is_org,is_blocking,employments,answer_count,follower_count,articles_count,gender,badge[?(type=best_answerer)].topics'

    # 关注列表的url和请求参数
    follows_url = 'https://www.zhihu.com/api/v4/members/{user}/followees?include={include}&offset={offset}&limit={limit}'
    follows_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    #粉丝列表的url和请求参数
    followers_url = 'https://www.zhihu.com/api/v4/members/{user}/followers?include={include}&offset={offset}&limit={limit}'
    followers_query = 'data[*].answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics'

    def start_requests(self):
        # Request the details of the fist user.
        yield Request(self.user_url.format(user=self.start_user, include=self.user_query), callback=self.parse_user)

        # Request the first user's list of following.
        yield Request(self.follows_url.format(user=self.start_user, include=self.follows_query, offset=0, limit=20), callback=self.parse_follows)

        # 请求起始用户的粉丝列表
        yield Request(self.followers_url.format(user=self.start_user, include=self.followers_query, offset=0, limit=20), callback=self.parse_followers)

    def parse_user(self, response):
        """
        解析用户信息,请求用户关注列表和粉丝列表
        :param response:
        :return:
        """
        result = json.loads(response.text) #Convert to a dict
        # Get the first user's details
        item = UserItem()
        # Item有个fields属性,包含所有的field名,依次遍历并赋值
        for field in item.fields:
            if field in result.keys():
                item[field] = result.get(field)
        yield item

        # 获取起始用户关注列表中每个用户的关注列表
        yield Request(self.follows_url.format(user=result.get('url_token'), include=self.follows_query, offset=0, limit=20), callback=self.parse_follows)

        # 获取起始用户粉丝列表中每个用户的粉丝列表
        yield Request(self.follows_url.format(user=result.get('url_token'), include=self.follows_query, offset=0, limit=20), callback=self.parse_followers)

    def parse_follows(self, response):
        """
        Parse follows list information and Get next page url
        """
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                # 请求用户详细信息
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query), callback=self.parse_user)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            # 请求下一页的关注列表
            yield Request(next_page, callback=self.parse_follows)

    def parse_followers(self, response):
        """
        Parse followers list information and Get next page url
        """
        results = json.loads(response.text)
        if 'data' in results.keys():
            for result in results.get('data'):
                #　请求用户详细信息
                yield Request(self.user_url.format(user=result.get('url_token'), include=self.user_query), callback=self.parse_user)
        if 'paging' in results.keys() and results.get('paging').get('is_end') == False:
            next_page = results.get('paging').get('next')
            # 请求下一页的关注列表
            yield Request(next_page, callback=self.parse_followers)



