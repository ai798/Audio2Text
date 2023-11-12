import re
from typing import Union

import aiohttp

tiktok_api_headers = {
    'User-Agent': 'com.ss.android.ugc.trill/494+Mozilla/5.0+(Linux;+Android+12;+2112123G+Build/SKQ1.211006.001;+wv)+AppleWebKit/537.36+(KHTML,+like+Gecko)+Version/4.0+Chrome/107.0.5304.105+Mobile+Safari/537.36',
    'Cookie': '_ttp=2KJAYROGZqx9Tn2tU2aAX6waCr7; tt_csrf_token=15FkfLNc-Y1jURhqaq0m9L_zn0RSoS6HuyM8; tt_chain_token=D7Dzc2U6gnMSWmeueW9eDA==; __tea_cache_tokens_1988={%22_type_%22:%22default%22%2C%22user_unique_id%22:%227282277026336278018%22%2C%22timestamp%22:1695537271096}; tiktok_webapp_theme=light; odin_tt=92ad3ea5d5efd87dd6a6f6f52a8f0a07c0c26d1fa365acc23205178743332b05430aecd38feb0d0d6d7eea2987514d97bb0a2da30d5b0099a6a8cd74df21f7d2b9c47b2df96c5d9e6f231500a7e880f8; csrf_session_id=ab408a8f88c1940afc78c218ab7da5e1; passport_csrf_token=c317ac7fd6b6f3f06076fe0512cfbaa1; passport_csrf_token_default=c317ac7fd6b6f3f06076fe0512cfbaa1; s_v_web_id=verify_lmx34nag_sgsEhTEN_bP2p_4vpF_8Oyf_5QousIxmka0c; multi_sids=7276733218950186026%3A894385f0d3ebae8b7f6e7be8f7540d45; cmpl_token=AgQQAPNSF-RO0rTCyOiY_V0T_25BbOFcP4AhYMyqfw; passport_auth_status=1281c61e2b0a7ca7c53be914867a83e1%2C; passport_auth_status_ss=1281c61e2b0a7ca7c53be914867a83e1%2C; uid_tt=f2647c7fb0049c161e43ce412f0e3c207cc86e7ab7eb9fc25a861c2157605d45; uid_tt_ss=f2647c7fb0049c161e43ce412f0e3c207cc86e7ab7eb9fc25a861c2157605d45; sid_tt=894385f0d3ebae8b7f6e7be8f7540d45; sessionid=894385f0d3ebae8b7f6e7be8f7540d45; sessionid_ss=894385f0d3ebae8b7f6e7be8f7540d45; store-idc=useast5; store-country-code=us; store-country-code-src=uid; tt-target-idc=useast5; tt-target-idc-sign=Mk_EZeEbTXrMxQmkun6YvHV_EVLVqKvlVJn_l2gmplaAdEJJsv-OVdBi4gTTnwZn7xnLD73v4pG21-XrzeE_iEkY_2iqX1T_T1nT6eLJ2XR2x3iAxFGzoC82aqzYatwaQguFNkdTtwk1i4EqvW96JAhS5fXq0u2nDZz2yjTpk8cTsDPBT6mZOaY5p3HBQbYpMxeD8HkXzWyrR2qBqdrLv_JjbjmUa8zWCPDPp_Px5v4iExslMibc4K1E3Et-os9-c3mBkqquUix_FfAYPVKZv9Konq324wIRMhi44r2dR4g8q843jIfIcr8xEcTdz3k0GRcZoVukvwPH8Qd1xcDIpBfAsyQe6bmWVYCKDUO2M_z-Zut0uuY-J5BZxNvkjL8V9lcuTUbkyaWnPSLqerteQvAete5xffI86oMMT6HAtXyDbn9NMxBQvdZFltDfFpidcyEKoTha2ShyPw58yFBSHzWL6FpjdI9Nl6qAa5In5EX5uOBBIjVSZHz7SvEzoFx9; sid_guard=894385f0d3ebae8b7f6e7be8f7540d45%7C1695537322%7C15551992%7CFri%2C+22-Mar-2024+06%3A35%3A14+GMT; sid_ucp_v1=1.0.0-KDQ4NDhlZWQ5NzAxMGRlOGZjOTA0MWM3OWFkOTIyZjQxMzM2MDVmZTIKFwiqiL6G8cmJ_mQQqrG_qAYYsws4CEASEAQaB3VzZWFzdDUiIDg5NDM4NWYwZDNlYmFlOGI3ZjZlN2JlOGY3NTQwZDQ1; ssid_ucp_v1=1.0.0-KDQ4NDhlZWQ5NzAxMGRlOGZjOTA0MWM3OWFkOTIyZjQxMzM2MDVmZTIKFwiqiL6G8cmJ_mQQqrG_qAYYsws4CEASEAQaB3VzZWFzdDUiIDg5NDM4NWYwZDNlYmFlOGI3ZjZlN2JlOGY3NTQwZDQ1; ttwid=1%7CBIYVAFOQVGMfNmXJt782nvlSDq5W6p6lEhgzJO92PRg%7C1695537322%7Cb64fc7db3f5b605181b47bcf3174067ef070190fcf9c8799ea71057718e56d12; perf_feed_cache={%22expireTimestamp%22:1695708000000%2C%22itemIds%22:[%227276411640898260232%22%2C%227270180985507974418%22]}; msToken=r_2SC3er4YLqdoYi1_yiM47Fq2EpLh1SnGJHYRgDUxcGM04vSMbcOjHSL-D-0ZjLbpe2IbstDnYw9LwcabbfonjlW2NU7iDo8IBy3kMVu_k4-TMtgzzp8dbGYG-rTJt3mbb1XDQfud3jItX1Kw==; msToken=9qXxnadC7WvBflltq108QqkekqvmnpNOzmbtLctZW8TZFd9DCZX09Kv56hETANPswAVDh5umvMv2q3VghElgxrNUYZ_QX32D9yfp7z9krSTXq6dOouRb; passport_fe_beating_status=true',
}


def get_tiktok_video_no(original_url: str):
    """
    获取视频id
    :param original_url: 视频链接
    :return: 视频id
    """
    try:
        # 转换链接/Convert link
        original_url = convert_share_urls(original_url)
        # 获取视频ID/Get video ID
        if '/video/' in original_url:
            video_no = re.findall('/video/(\d+)', original_url)[0]
        elif '/v/' in original_url:
            video_no = re.findall('/v/(\d+)', original_url)[0]
        # print('获取到的TikTok视频ID是{}'.format(video_id))
        # 返回视频ID/Return video ID
        return video_no
    except Exception as e:
        print('获取TikTok视频ID出错了:{}'.format(e))
        return "0"


async def get_tiktok_video_data(video_no: str) -> Union[dict, None]:
    """
    获取单个视频信息
    :param video_no: 视频id
    :return: 视频信息
    """
    # print('正在获取TikTok视频数据...')
    try:
        # 构造访问链接/Construct the access link
        api_url = f'https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={video_no}'
        print("正在获取视频数据API: {}".format(api_url))
        async with aiohttp.ClientSession() as session:
            # TODO 这里暂时修改, proxy为None, 而不是启动初始化
            async with session.get(api_url, headers=tiktok_api_headers, proxy=None,
                                   timeout=10) as response:
                response = await response.json()
                video_data = response['aweme_list'][0]
                # print('获取视频信息成功！')
                return video_data
    except Exception as e:
        print('获取视频信息失败！原因:{}'.format(e))
        # return None
        raise e


async def convert_share_urls(self, url: str) -> Union[str, None]:
    """
    用于将分享链接(短链接)转换为原始链接/Convert share links (short links) to original links
    :return: 原始链接/Original link
    """
    # 检索字符串中的链接/Retrieve links from string
    url = self.get_url(url)
    # 判断是否有链接/Check if there is a link
    if url is None:
        print('无法检索到链接/Unable to retrieve link')
        return None
    # 判断是否为抖音分享链接/judge if it is a douyin share link
    if 'douyin' in url:
        """
        抖音视频链接类型(不全)：
        1. https://v.douyin.com/MuKhKn3/
        2. https://www.douyin.com/video/7157519152863890719
        3. https://www.iesdouyin.com/share/video/7157519152863890719/?region=CN&mid=7157519152863890719&u_code=ffe6jgjg&titleType=title&timestamp=1600000000&utm_source=copy_link&utm_campaign=client_share&utm_medium=android&app=aweme&iid=123456789&share_id=123456789
        抖音用户链接类型(不全)：
        1. https://www.douyin.com/user/MS4wLjABAAAAbLMPpOhVk441et7z7ECGcmGrK42KtoWOuR0_7pLZCcyFheA9__asY-kGfNAtYqXR?relation=0&vid=7157519152863890719
        2. https://v.douyin.com/MuKoFP4/
        抖音直播链接类型(不全)：
        1. https://live.douyin.com/88815422890
        """
        if 'v.douyin' in url:
            # 转换链接/convert url
            # 例子/Example: https://v.douyin.com/rLyAJgf/8.74
            url = re.compile(r'(https://v.douyin.com/)\w+', re.I).match(url).group()
            print('正在通过抖音分享链接获取原始链接...')
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, proxy=self.proxies, allow_redirects=False,
                                           timeout=10) as response:
                        if response.status == 302:
                            url = response.headers['Location'].split('?')[0] if '?' in response.headers[
                                'Location'] else \
                                response.headers['Location']
                            print('获取原始链接成功, 原始链接为: {}'.format(url))
                            return url
            except Exception as e:
                print('获取原始链接失败！')
                print(e)
                # return None
                raise e
        else:
            print('该链接为原始链接,无需转换,原始链接为: {}'.format(url))
            return url
    # 判断是否为TikTok分享链接/judge if it is a TikTok share link
    elif 'tiktok' in url:
        """
        TikTok视频链接类型(不全)：
        1. https://www.tiktok.com/@tiktok/video/6950000000000000000
        2. https://www.tiktok.com/t/ZTRHcXS2C/
        TikTok用户链接类型(不全)：
        1. https://www.tiktok.com/@tiktok
        """
        if '@' in url:
            print('该链接为原始链接,无需转换,原始链接为: {}'.format(url))
            return url
        else:
            print('正在通过TikTok分享链接获取原始链接...')
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, proxy=self.proxies, allow_redirects=False,
                                           timeout=10) as response:
                        if response.status == 301:
                            url = response.headers['Location'].split('?')[0] if '?' in response.headers[
                                'Location'] else \
                                response.headers['Location']
                            print('获取原始链接成功, 原始链接为: {}'.format(url))
                            return url
            except Exception as e:
                print('获取原始链接失败！')
                print(e)
                return None
    elif 'b23.tv' in url or "bilibili" in url:
        """
        bilibili视频链接类型(不全)：
        1. https://b23.tv/Ya65brl
        2. https://www.bilibili.com/video/BV1MK4y1w7MV/
        bilibili用户链接类型(不全)：
        1. https://www.douyin.com/user/MS4wLjABAAAAbLMPpOhVk441et7z7ECGcmGrK42KtoWOuR0_7pLZCcyFheA9__asY-kGfNAtYqXR?relation=0&vid=7157519152863890719
        bilibili直播链接类型(不全)：
        """
        if 'b23.tv' in url:
            print('正在通过哔哩哔哩分享链接获取原始链接...')
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=self.headers, proxy=self.proxies, allow_redirects=False,
                                           timeout=10) as response:
                        if response.status == 302:
                            url = response.headers['Location'].split('?')[0] if '?' in response.headers[
                                'Location'] else \
                                response.headers['Location']
                            print('获取原始链接成功, 原始链接为: {}'.format(url))
                            return url
            except Exception as e:
                print('获取原始链接失败！')
                print(e)
                # return None
                raise e
        else:
            print('该链接为原始链接,无需转换,原始链接为: {}'.format(url))
            return url


@staticmethod
def get_url(text: str) -> Union[str, None]:
    try:
        # 从输入文字中提取索引链接存入列表/Extract index links from input text and store in list
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        # 判断是否有链接/Check if there is a link
        if len(url) > 0:
            return url[0]
    except Exception as e:
        print('Error in get_url:', e)
        return None


if __name__ == '__main__':
    get_tiktok_video_data("6876811402821061890")