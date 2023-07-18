from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote
import re
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import os

def get_title_page(url):
    header={
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.41"
            }
    response = requests.get(url,headers=header)
    if response.status_code != 200:
        print("无法访问网页！")
        return False
    # 使用正则表达式提取<title>标签中书名号中的文字
    pattern = r"《(.*?)》"
    match = re.search(pattern, response.text)
    if match:
        title = match.group(1)
        return title
    else:
        return False

def get_video_html(url):
    header={
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.41"
            }
    driver = webdriver.Chrome()
    # 发送请求并获取页面
    driver.get(url)
    # 获取页面内容
    page_content = driver.page_source
    driver.quit()
    pattern = r'<iframe[^>]+src="([^"]+)"'  # 匹配 <iframe> 标签中的 src 属性的值
    matches = re.search(pattern,page_content)
    if matches:
        iframe_content = matches.group(0)
        pattern = r'url=([^&"]+)'  # 匹配 url= 后面的内容，直到遇到 & 或 " 字符
        matches = re.search(pattern, iframe_content)
        if matches:
            url = matches.group(1)
            url= unquote(url)
            print(type(url))
            response = requests.get(url,headers=header)
            if response.status_code==200:
                lines = response.text.split('\n')
                print(lines)
                if len(lines) >= 3:
                    third_line = lines[2]
                url=url.replace("index.m3u8",third_line)
                print(url)
                return url
            else:
                return False
        else:
            return False
    else:
        return False
def get_page_url(url):
    header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.41"
    }
    response=requests.get(url,headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    # 存储所有链接的列表
    all_links = []
    # 查找所有 class="movurl" 的 <div> 标签
    div_tags = soup.find_all('div', class_='movurl')
    # 遍历每个 <div> 标签
    for div_tag in div_tags:
        # 创建当前组链接的列表
        group_links = []
        # 查找 div_tag 下的所有 <a> 标签
        links = div_tag.find_all('a')
        # 提取链接的 href 属性值并添加到当前组链接列表中
        for link in links:
            href = link['href']
            group_links.append("https://www.yhdmz.org"+href)
        all_links.append(group_links)
        # 将当前组链接列表添加到总列表中
    return all_links[1]
def download_ts(video_url,i,header,video_urls,last_number):
    print(video_url)
    video_response = requests.get(video_url, headers=header)
    video_save_path = os.path.join(os.getcwd(), "tmp", f"{i}.ts")
    current_number = int(extract_last_number(video_url.split('/')[-1]))
    print(current_number,last_number)
    if current_number>last_number:
        print(f"视频分段 {i+1}/{len(video_urls)} 跳过下载！")
        return False
    with open(video_save_path, 'wb') as file:
        file.write(video_response.content)
    print(f"视频分段 {i+1}/{len(video_urls)} 下载成功！")

def extract_last_number(filename):
    filename=filename.split(".")[0]
    pattern = r"(?!0)\d{1,6}(?=\D*$)"
    match = re.search(pattern, filename[-6:])
    if match:
        last_number = match.group(0)
        return int(last_number)
    elif filename[-6:0]=="000000":
        return int(0)
    else:
        return None


def download_m3u8(url):
    header={
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.41"
    }
    response = requests.get(url,headers=header)
    if response.status_code == 200:
        m3u8_content = response.text
        lines = m3u8_content.split('\n')
        video_urls =[line for line in lines if line.endswith('.ts')]
        last_number=extract_last_number(video_urls[-1])
        with ThreadPoolExecutor(max_workers=10) as pool:
            for i, video_url in enumerate(video_urls):
                download_url = url.replace(url.split('/')[-1], video_url)
                pool.submit(download_ts, download_url, i, header, video_urls,last_number)
        print("M3U8视频下载完成！")
    else:
        print("M3U8文件下载失败！")

def extract_number(filename):
    return int(''.join(filter(str.isdigit, filename)))

def merge_ts_to_mp4(input_dir, output_path, ffmpeg_path):
    ts_files = [file for file in os.listdir(input_dir) if file.endswith('.ts')]
    ts_files.sort(key=extract_number)
    with open('file_list.txt', 'w') as file:
        for line in ts_files:
            file.write('file \'{}\'\n'.format(os.path.join(input_dir, line).replace('\\', '/')))
    command = f'{ffmpeg_path} -f concat -safe 0 -i file_list.txt -c copy "{output_path}"'
    print(command)
    os.system(command)
    os.remove('file_list.txt')
    for ts_file in ts_files:
        os.remove(os.path.join(input_dir, ts_file))
def yinghuadongman(url,ffmpeg_path):
    url="https://www.yhdmz.org/showp/20141.html"
    title=get_title_page(url)
    if not os.path.exists(os.path.join(os.getcwd(),title)):
        os.mkdir(os.path.join(os.getcwd(),title))
    links=get_page_url(url)
    
    video_urls=[]
    t=1
    for link in links:
        video_urls.append(get_video_html(link))
    for video_url in video_urls:
        download_m3u8(video_url)
        merge_ts_to_mp4(os.path.join(os.getcwd(),'tmp'),os.path.join(os.getcwd(),title,"第{}集.mp4".format(t)),ffmpeg_path)
        t=t+1
