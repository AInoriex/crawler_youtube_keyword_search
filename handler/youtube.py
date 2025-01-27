from pytz import utc, timezone
from os import path, makedirs, walk, getenv
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from datetime import datetime
from handler.yt_dlp import download_by_watch_url, download_by_playlist_url

def download_url(url, save_path):
    ''' 下载油管单个视频或者播放列表 '''
    if "watch" in url:
        return download_by_watch_url(url, save_path)
    else:
        return download_by_playlist_url(url, save_path)

def format_into_watch_url(url:str):
    '''
    @Desc   格式化链接保留参数v
    @Params url:https://www.youtube.com/watch?v=6s416NmSFmw&list=PLRMEKqidcRnAGC6j1oYPFV9E26gyWdgU4&index=4
    @Return 6s416NmSFmw, https://www.youtube.com/watch?v=6s416NmSFmw
    '''
    vid = str("")
    try:
        # 解析URL
        parsed_url = urlparse(url)
        
        # 解析查询参数
        query_params = parse_qs(parsed_url.query)
        if len(query_params) > 1:
            # 保留查询参数中的v
            if 'v' in query_params:
                vid = query_params['v'][0]
                new_query_params = {'v': vid}
            else:
                raise ValueError
            
            # 构建新的查询字符串
            new_query_string = urlencode(new_query_params, doseq=True)
            
            # 构建新的URL
            new_url = urlunparse(parsed_url._replace(query=new_query_string))
        else:
            if 'v' in query_params:
                vid = str(query_params['v'][0])
                new_url = url
            else:
                raise ValueError
    except Exception as e:
        print(f"Yt-dlp > format_into_watch_url failed, url:{url}, error:{e.__str__}")
        return vid, ""
    else:
        # print(f"format_into_watch_url succeed, url:{url}")
        return vid, new_url;

def try_to_get_file_name(save_dir:str, vid:str, default_name='')->str:
    ''' 尝试获取下载文件名 '''
    ret_name = ""
    # files = []
    for dirpath, dirnames, filenames in walk(save_dir):
        for filename in filenames:
            # files.append(path.join(dirpath, filename))
            if ".part" in filename:
                print("try_to_get_file_name > part文件跳过获取")
                continue
            if vid in filename:
                ret_name = (path.join(dirpath, filename))
                break
    if ret_name == "":
        ret_name = default_name
    print(f"try_to_get_file_name > 获取到本地资源文件{ret_name}")
    return ret_name

def is_touch_fish_time()->bool:
    ''' 判断是否能摸鱼，以Youtube总部地区为限制 '''
    ytb_timezone = "America/Los_Angeles"

    # 获取当前时间
    now_utc = datetime.now(utc)
    
    # 转换为美国加利福尼亚州时区时间
    pacific_tz = timezone(ytb_timezone)
    now_pacific = now_utc.astimezone(pacific_tz)
    
    # 获取当前的小时
    current_hour = now_pacific.hour
    current_mint = now_pacific.minute
    
    # 判断是否在办公时间内(早上9点到下午5点)
    if 9 <= current_hour < 17+1:
        print(f"[×] 非摸鱼时间 > 当地时区 {ytb_timezone} | 当地时间 {current_hour}:{current_mint}")
        return False
    else:
        print(f"[√] 摸鱼时间 > 当地时区 {ytb_timezone} | 当地时间 {current_hour}:{current_mint}")
        return True

def get_cloud_save_path_by_language(save_path:str, lang_key:str)->str:
    ''' 
    语言对应的云存储路径
    :param save_path: 保存的云存储路径
    :param lang_key: 语言key
    :return: language 对应的云存储路径
    '''
    ret_path = str("")   
    LANGUAGE_PATH_DICT = {
        "ar": "Alaboyu",		# 阿拉伯语
		"bo": "Zangyu",			# 藏语
        "de": "Deyu",			# 德语
        "el": "Xilayu/modern",	# 现代希腊语
        "en": "English",		# 英语
        "es": "Xibanyayu",		# 西班牙语
        "fil": "Feilvbinyu",	# 菲律宾语
        "fr": "Fayu",			# 法语
        "id": "Yinniyu",		# 印尼语
		"it": "Yidaliyu",		# 意大利语
        "ja": "Riyu",			# 日语
        "ko": "Hanyu",			# 韩语
        "ms": "Malaiyu",		# 马来语
        "nan": "Minnanyu",		# 闽南语
		"pl": "Bolanyu",		# 波兰语
		"pt": "Putaoyayu",		# 葡萄牙语
        "ru": "Eyu",			# 俄语
        "th": "Taiyu",			# 泰语
        "vi": "Vietnam",		# 越南语
        "yue": "Yueyu",			# 粤语
        "zh": "Zhongwen",		# 中文
        "nl": "language/Helanyu",       # 荷兰语
        "hi": "language/Yindiyu",       # 印地语
        "tr": "language/Tuerqiyu",      # 土耳其语
        "sv": "language/Ruidianyu",     # 瑞典语
        "bg": "language/Baojialiyayu",  # 保加利亚语
        "ro": "language/Luomaniyayu",   # 罗马尼亚语
        "cs": "language/Jiekeyu",       # 捷克语
        "fi": "language/Fenlanyu",      # 芬兰语
        "hr": "language/Keluodiyayu",   # 克罗地亚语
        "sk": "language/Siluofakeyu",   # 斯洛伐克
        "da": "language/Danmaiyu",      # 丹麦语
        "ta": "language/Taimieryu",     # 泰米尔语
        "uk": "language/Wukelanyu",     # 乌克兰语
        "tl": "language/Tajialuyu",		# 他加禄语
        "mn": "language/Mengguyu",		# 蒙语/蒙古语
        "bo": "language/Zangyu",		# 藏语
        "ug": "language/Weiwueryu",		# 维语/维吾尔语
        "test": f"Unclassify/test",             # 测试数据
        "unknown": f"Unclassify/{lang_key}",    # 其他
    }
    if "{LANGUAGE}" in save_path:
        ret_path = save_path.format(LANGUAGE=LANGUAGE_PATH_DICT.get(lang_key.lower(), f"Unclassify/{lang_key}"))
    else:
        ret_path = save_path
    return ret_path

def get_youtube_vid(url:str):
    """
    Extracts the YouTube video ID from a given URL.

    This function handles both standard YouTube watch URLs and YouTube Shorts URLs.
    For watch URLs, it extracts the video ID from the 'v' query parameter. For Shorts 
    URLs, it extracts the ID from the URL path.

    :param url: The YouTube URL from which to extract the video ID.
    :return: The extracted video ID as a string, or an empty string if extraction fails.
    :raises ValueError: If the URL does not contain a recognizable format for extracting the video ID.
    """

    import re
    from uuid import uuid4
    # default = uuid4()
    default = ""
    try:
        if "watch" in url:
            # https://www.youtube.com/watch?v=kw1fXZNfnVc => kw1fXZNfnVc
            video_id_match = re.search(r"v=([^&#]+)", url)
            if video_id_match:
                return video_id_match.group(1)
            else:
                raise ValueError("get_youtube_vid watch url re.search failed")
        elif "shorts" in url:
            # https://www.youtube.com/shorts/kw1fXZNfnVc => kw1fXZNfnVc
            return url.split("/")[-1]
        else:
            raise ValueError("get_youtube_vid not support url")
    except Exception as e:
        print(f"get_youtube_vid > extract video id error, {e}")
        return default

def get_mime_type(url, default="mp4"):
    """
    Extracts the MIME type from a YouTube URL.

    If the URL contains "mime", it tries to extract the MIME type using a regex 
    pattern. If the extraction fails or the URL format is unsupported, it returns 
    a default value.

    :param url: The YouTube URL from which to extract the MIME type.
    :param default: The default value to return if extraction fails.
    :return: The extracted MIME type or the default value if extraction fails.
    :raises ValueError: If the URL format is unsupported or extraction fails.
    """
    import re
    try:
        mime_match = re.search(r"mime=([^&]+)", url)
        if mime_match:
            mime_value = mime_match.group(1)
            return mime_value.split("%2F")[1]
        else:
            raise ValueError("get_mime_type re.search failed")
    except Exception as e:
        print(f"get_mime_type > get url mime type error, {e}")
        return default