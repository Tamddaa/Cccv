#!/usr/bin/env python3
import os
import threading
import requests
import random
import time
import base64
import sys
import re
from string import ascii_letters, digits
from urllib.parse import unquote

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class Icons:
    SUCCESS = "✓"
    ERROR = "✗"
    WARNING = "⚠"
    INFO = "ℹ"
    LOCK = "🔒"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def install_libs():
    for lib in ["requests", "prettytable"]:
        try: 
            __import__(lib)
        except ImportError: 
            print(f"{Colors.YELLOW}Đang cài đặt {lib}...{Colors.RESET}")
            os.system(f"pip install {lib}")

install_libs()
from prettytable import PrettyTable

class Zefoy:
    def __init__(self):
        clear_screen()
        self.base_url = 'https://zefoy.com/'
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }
        self.session = requests.Session()
        self.captcha_1, self.captcha_, self.video_key = None, {}, None
        self.service, self.services, self.services_ids, self.services_status = None, {}, {}, {}
        
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}    ZEFOY AUTOMATION TOOL - TIKTOK VIEWS BOOSTER{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
        self.url = input(f"{Colors.BLUE}🔗 Nhập link video TikTok: {Colors.RESET}").strip()
        if not self.url:
            print(f"{Colors.RED}{Icons.ERROR} Link không được để trống!{Colors.RESET}")
            sys.exit(1)
        
        self.running = True
        self.video_info = []

    def get_captcha(self):
        if os.path.exists('session'):
            try:
                with open('session', 'r', encoding='utf-8') as f:
                    session_id = f.read().strip()
                    if session_id:
                        self.session.cookies.set("PHPSESSID", session_id, domain='zefoy.com')
            except Exception as e:
                print(f"{Colors.YELLOW}{Icons.WARNING} Không thể đọc session cũ: {e}{Colors.RESET}")
        
        try:
            resp = self.session.get(self.base_url, headers=self.headers, timeout=30)
            
            if "VPN, proxy, or hosting IP" in resp.text:
                print(f"\n{Colors.RED}{Icons.LOCK} {'='*50}{Colors.RESET}")
                print(f"{Colors.RED}{Icons.LOCK} Zefoy phát hiện VPN/Proxy/IP Hosting!{Colors.RESET}")
                print(f"{Colors.RED}{Icons.LOCK} Vui lòng TẮT VPN/Proxy và thử lại.{Colors.RESET}")
                print(f"{Colors.RED}{Icons.LOCK} {'='*50}{Colors.RESET}\n")
                sys.exit(1)

            if 'Enter Video URL' in resp.text:
                match = re.search(r'name="([^"]*)"\s+placeholder="Enter Video URL"', resp.text)
                if match:
                    self.video_key = match.group(1)
                    print(f"{Colors.GREEN}{Icons.SUCCESS} Đã có session hợp lệ!{Colors.RESET}")
                    return True
                else:
                    print(f"{Colors.YELLOW}{Icons.WARNING} Không tìm thấy video_key, cần đăng nhập lại.{Colors.RESET}")
                    return False

            for name, value in re.findall(r'<input type="hidden" name="([^"]*)" value="([^"]*)">', resp.text):
                self.captcha_[name] = value
            
            captcha_name_match = re.search(r'type="text" name="([^"]*)"', resp.text)
            
            captcha_img_patterns = [
                r'<img src="([^"]*)"[^>]*onerror="imgOnError\(\)"',
                r'<img[^>]*src="([^"]*)"[^>]*alt="captcha"',
                r'<img[^>]*src="(/captcha[^"]*)"',
                r'<img[^>]*src="([^"]*captcha[^"]*\.png[^"]*)"',
                r'<img[^>]*class="[^"]*captcha[^"]*"[^>]*src="([^"]*)"',
            ]
            
            captcha_img_match = None
            for pattern in captcha_img_patterns:
                captcha_img_match = re.search(pattern, resp.text, re.IGNORECASE)
                if captcha_img_match:
                    break
            
            if not captcha_name_match or not captcha_img_match:
                with open('debug_html.txt', 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                print(f"{Colors.RED}{Icons.ERROR} Không tìm thấy captcha trong HTML.{Colors.RESET}")
                print(f"{Colors.YELLOW}{Icons.INFO} HTML response đã lưu vào debug_html.txt để kiểm tra{Colors.RESET}")
                print(f"{Colors.RED}{Icons.ERROR} Trang web có thể đã thay đổi cấu trúc.{Colors.RESET}")
                return False
            
            self.captcha_1 = captcha_name_match.group(1)
            img_url = captcha_img_match.group(1)

            try:
                img_response = self.session.get(f"{self.base_url}{img_url}", headers=self.headers, timeout=30)
                if img_response.status_code == 200:
                    with open('captcha.png', 'wb') as f:
                        f.write(img_response.content)
                    
                    if os.path.getsize('captcha.png') == 0:
                        print(f"{Colors.RED}{Icons.ERROR} File captcha trống!{Colors.RESET}")
                        return False
                    
                    print(f"{Colors.GREEN}{Icons.SUCCESS} Đã tải captcha thành công.{Colors.RESET}")
                    return False
                else:
                    print(f"{Colors.RED}{Icons.ERROR} Không thể tải captcha (Mã lỗi: {img_response.status_code}){Colors.RESET}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"{Colors.RED}{Icons.ERROR} Lỗi mạng khi tải captcha: {e}{Colors.RESET}")
                return False
            except Exception as e:
                print(f"{Colors.RED}{Icons.ERROR} Lỗi ghi file captcha: {e}{Colors.RESET}")
                return False

        except requests.exceptions.Timeout:
            print(f"{Colors.RED}{Icons.ERROR} Timeout khi kết nối đến Zefoy!{Colors.RESET}")
            return False
        except requests.exceptions.RequestException as e:
            print(f"{Colors.RED}{Icons.ERROR} Lỗi mạng: {e}{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}{Icons.ERROR} Lỗi không xác định: {e}{Colors.RESET}")
            return False

    def solve_captcha(self, path):
        if not os.path.exists(path):
            print(f"{Colors.RED}{Icons.ERROR} File captcha '{path}' không tồn tại!{Colors.RESET}")
            return ""
        if os.path.getsize(path) == 0:
            print(f"{Colors.RED}{Icons.ERROR} File captcha '{path}' trống!{Colors.RESET}")
            return ""

        try:
            api_key = os.getenv('OCR_API_KEY', 'K87899142388957')
            with open(path, 'rb') as f:
                files = {'file': f}
                print(f"{Colors.YELLOW}{Icons.INFO} Đang gửi captcha đến OCR API...{Colors.RESET}")
                res = self.session.post(
                    'https://api.ocr.space/parse/image', 
                    headers={'apikey': api_key}, 
                    files=files,
                    timeout=30
                ).json()
            
            if 'ParsedResults' in res and len(res['ParsedResults']) > 0:
                captcha_text = res['ParsedResults'][0]['ParsedText'].strip()
                print(f"{Colors.GREEN}{Icons.SUCCESS} OCR kết quả: {captcha_text}{Colors.RESET}")
                return captcha_text
            else:
                print(f"{Colors.RED}{Icons.ERROR} OCR API không trả về kết quả.{Colors.RESET}")
                if 'ErrorMessage' in res:
                    print(f"{Colors.RED}{Icons.ERROR} Lỗi: {res['ErrorMessage']}{Colors.RESET}")
                return ""
        except requests.exceptions.Timeout:
            print(f"{Colors.RED}{Icons.ERROR} OCR API timeout!{Colors.RESET}")
            return ""
        except Exception as e:
            print(f"{Colors.RED}{Icons.ERROR} OCR lỗi: {e}{Colors.RESET}")
            return ""

    def send_captcha(self):
        max_attempts = 3
        for attempt in range(max_attempts):
            print(f"\n{Colors.CYAN}{'─'*50}{Colors.RESET}")
            print(f"{Colors.CYAN}Lần thử {attempt+1}/{max_attempts}{Colors.RESET}")
            print(f"{Colors.CYAN}{'─'*50}{Colors.RESET}")
            
            captcha_needed = not self.get_captcha()

            if not captcha_needed:
                print(f"{Colors.GREEN}{Icons.SUCCESS} Session hợp lệ, bỏ qua captcha!{Colors.RESET}")
                return True

            print(f"{Colors.YELLOW}{Icons.INFO} Đang giải captcha...{Colors.RESET}")
            captcha_text = self.solve_captcha('captcha.png')
            
            if not captcha_text:
                print(f"{Colors.RED}{Icons.ERROR} Không thể giải captcha. Thử lại...{Colors.RESET}")
                time.sleep(2)
                continue

            self.captcha_[self.captcha_1] = captcha_text
            
            try:
                resp = self.session.post(self.base_url, headers=self.headers, data=self.captcha_, timeout=30)

                if "VPN, proxy, or hosting IP" in resp.text:
                    print(f"\n{Colors.RED}{Icons.LOCK} {'='*50}{Colors.RESET}")
                    print(f"{Colors.RED}{Icons.LOCK} Zefoy phát hiện VPN/Proxy sau khi gửi captcha!{Colors.RESET}")
                    print(f"{Colors.RED}{Icons.LOCK} Vui lòng TẮT VPN/Proxy.{Colors.RESET}")
                    print(f"{Colors.RED}{Icons.LOCK} {'='*50}{Colors.RESET}\n")
                    sys.exit(1)

                if 'Enter Video URL' in resp.text:
                    try:
                        with open('session', 'w', encoding='utf-8') as f:
                            f.write(self.session.cookies.get('PHPSESSID'))
                        print(f"{Colors.GREEN}{Icons.SUCCESS} Session đã được lưu!{Colors.RESET}")
                    except Exception as e:
                        print(f"{Colors.YELLOW}{Icons.WARNING} Không thể lưu session: {e}{Colors.RESET}")
                    
                    match = re.search(r'name="([^"]*)"\s+placeholder="Enter Video URL"', resp.text)
                    if match:
                        self.video_key = match.group(1)
                    
                    print(f"{Colors.GREEN}{Icons.SUCCESS} ✨ Đăng nhập thành công! ✨{Colors.RESET}")
                    
                    if os.path.exists('captcha.png'):
                        try:
                            os.remove('captcha.png')
                        except OSError:
                            pass
                    
                    return True
                
                print(f"{Colors.YELLOW}{Icons.WARNING} Captcha sai, thử lại...{Colors.RESET}")
            except requests.exceptions.Timeout:
                print(f"{Colors.RED}{Icons.ERROR} Timeout khi gửi captcha!{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.RED}{Icons.ERROR} Lỗi: {e}{Colors.RESET}")
            
            if os.path.exists('captcha.png'):
                try:
                    os.remove('captcha.png')
                except OSError:
                    pass
            
            time.sleep(2)

        print(f"{Colors.RED}{Icons.ERROR} Đăng nhập thất bại sau {max_attempts} lần thử!{Colors.RESET}")
        return False

    def get_services(self):
        try:
            resp = self.session.get(self.base_url, headers=self.headers, timeout=30).text
            self.services.clear()
            self.services_ids.clear()
            self.services_status.clear()
            
            for name, status in re.findall(r'<h5 class="card-title">(.+?)</h5>.*?<small[^>]*>(.+?)</small>', resp):
                self.services[name.strip()] = status.strip()
            
            for name, url in re.findall(r'<h5 class="card-title mb-3">(.+?)</h5>\s*<form action="(.+?)">', resp):
                self.services_ids[name.strip()] = url.strip()
            
            for name, html in re.findall(r'<h5 class="card-title">(.+?)</h5>\s*(.+?)<button', resp, re.DOTALL):
                self.services_status[name.strip()] = 'disabled' not in html.lower()
        except Exception as e:
            print(f"{Colors.RED}{Icons.ERROR} Lỗi lấy danh sách dịch vụ: {e}{Colors.RESET}")

    def print_services(self):
        self.get_services()
        table = PrettyTable([
            f"{Colors.CYAN}ID{Colors.RESET}", 
            f"{Colors.CYAN}Dịch Vụ{Colors.RESET}", 
            f"{Colors.CYAN}Trạng Thái{Colors.RESET}"
        ])
        
        for i, name in enumerate(self.services.keys(), 1):
            status = self.services[name]
            status_color = Colors.GREEN if 'ago updated' in status else Colors.RED
            active = f"{Colors.GREEN}{Icons.SUCCESS}{Colors.RESET}" if self.services_status.get(name, False) else f"{Colors.RED}{Icons.ERROR}{Colors.RESET}"
            table.add_row([
                f"{Colors.CYAN}{i}{Colors.RESET}", 
                name, 
                f"{status_color}{status} {active}{Colors.RESET}"
            ])
        
        print(table)

    def select_service(self):
        while True:
            print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.GREEN}         DANH SÁCH DỊCH VỤ CÓ SẴN{Colors.RESET}")
            print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
            self.print_services()
            print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
            
            try:
                choice = int(input(f"{Colors.BLUE}➤ Chọn ID dịch vụ (1-{len(self.services)}): {Colors.RESET}"))
                service_list = list(self.services.keys())
                
                if 1 <= choice <= len(service_list):
                    self.service = service_list[choice - 1]
                    print(f"{Colors.GREEN}{Icons.SUCCESS} Đã chọn: {self.service}{Colors.RESET}")
                    break
                else:
                    print(f"{Colors.RED}{Icons.ERROR} ID không hợp lệ!{Colors.RESET}")
            except ValueError:
                print(f"{Colors.RED}{Icons.ERROR} Vui lòng nhập số!{Colors.RESET}")
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}{Icons.INFO} Thoát bởi người dùng.{Colors.RESET}")
                sys.exit(0)

    def find_video(self):
        if not self.service or self.video_key is None: 
            return False
        
        attempts = 0
        while attempts < 3:
            try:
                boundary = "----WebKitFormBoundary0nU8PjANC8BhQgjZ"
                data = f"------WebKitFormBoundary0nU8PjANC8BhQgjZ\r\nContent-Disposition: form-data; name=\"{self.video_key}\"\r\n\r\n{self.url}\r\n------WebKitFormBoundary0nU8PjANC8BhQgjZ--\r\n"
                headers = self.headers.copy()
                headers['content-type'] = f'multipart/form-data; boundary={boundary}'
                headers['origin'] = 'https://zefoy.com'

                resp = self.session.post(
                    f'{self.base_url}{self.services_ids[self.service]}', 
                    headers=headers, 
                    data=data,
                    timeout=30
                )
                decoded_resp = base64.b64decode(unquote(resp.text.encode()[::-1])).decode()

                if 'Session expired. Please re-login' in decoded_resp:
                    print(f"{Colors.RED}{Icons.ERROR} Session hết hạn, đăng nhập lại...{Colors.RESET}")
                    if self.send_captcha(): 
                        continue
                    else: 
                        return False

                if 'service is currently not working' in decoded_resp:
                    print(f"{Colors.RED}{Icons.ERROR} Dịch vụ hiện không khả dụng!{Colors.RESET}")
                    return False

                if 'onsubmit="showHideElements' in decoded_resp:
                    name_match = re.search(r'name="([^"]*)"', decoded_resp)
                    value_match = re.search(r'value="([^"]*)"', decoded_resp)
                    if name_match and value_match:
                        self.video_info = [name_match.group(1), value_match.group(1)]
                        print(f"{Colors.GREEN}{Icons.SUCCESS} Video đã được xác thực!{Colors.RESET}")
                        return True
                    else:
                        print(f"{Colors.RED}{Icons.ERROR} Không tìm thấy thông tin video.{Colors.RESET}")
                        return False

                if 'Checking Timer...' in decoded_resp:
                    try:
                        timer = int(re.search(r'ltm=(\d+);', decoded_resp).group(1))
                        if timer >= 5000: 
                            print(f"{Colors.RED}{Icons.LOCK} Thời gian chờ quá lâu - IP có thể bị chặn!{Colors.RESET}")
                            self.running = False
                            return False
                        
                        print(f"{Colors.YELLOW}{Icons.INFO} Cần chờ {timer} giây...{Colors.RESET}")
                        for i in range(timer, 0, -1):
                            print(f"{Colors.YELLOW}⏳ Chờ: {i}s...{Colors.RESET}", end='\r')
                            time.sleep(1)
                        print(" " * 50, end='\r')
                        attempts += 1
                        continue
                    except:
                        pass

                if 'Too many requests' in decoded_resp: 
                    print(f"{Colors.YELLOW}{Icons.WARNING} Quá nhiều yêu cầu, chờ 3s...{Colors.RESET}")
                    time.sleep(3)
                    continue
                
                print(f"{Colors.RED}{Icons.ERROR} Phản hồi không mong đợi: {decoded_resp[:100]}...{Colors.RESET}")
                attempts += 1

            except requests.exceptions.Timeout:
                print(f"{Colors.RED}{Icons.ERROR} Timeout!{Colors.RESET}")
                time.sleep(2)
            except requests.exceptions.RequestException as e:
                print(f"{Colors.RED}{Icons.ERROR} Lỗi mạng: {e}{Colors.RESET}")
                time.sleep(2)
            except Exception as e:
                print(f"{Colors.RED}{Icons.ERROR} Lỗi: {e}{Colors.RESET}")
                time.sleep(2)
        
        return False

    def use_service(self):
        if not self.find_video(): 
            return False
        
        try:
            token = "".join(random.choices(ascii_letters + digits, k=16))
            boundary = f"----WebKitFormBoundary{token}"
            data = f"------WebKitFormBoundary{token}\r\nContent-Disposition: form-data; name=\"{self.video_info[0]}\"\r\n\r\n{self.video_info[1]}\r\n------WebKitFormBoundary{token}--\r\n"
            headers = self.headers.copy()
            headers['content-type'] = f'multipart/form-data; boundary={boundary}'
            headers['origin'] = 'https://zefoy.com'

            resp = self.session.post(
                f'{self.base_url}{self.services_ids[self.service]}', 
                headers=headers, 
                data=data,
                timeout=30
            )
            res = base64.b64decode(unquote(resp.text.encode()[::-1])).decode()

            if 'Session expired. Please re-login' in res:
                print(f"{Colors.RED}{Icons.ERROR} Session hết hạn, đăng nhập lại...{Colors.RESET}")
                self.send_captcha()
                return False
            
            if 'Too many requests' in res: 
                print(f"{Colors.YELLOW}{Icons.WARNING} Quá nhiều yêu cầu, chờ...{Colors.RESET}")
                time.sleep(3)
                return False
            
            if 'service is currently not working' in res: 
                print(f"{Colors.RED}{Icons.ERROR} Dịch vụ không hoạt động!{Colors.RESET}")
                return False

            success_match = re.search(r'color:green;">(.+?)</', res)
            if success_match:
                print(f"{Colors.GREEN}{Icons.SUCCESS} ✨ {success_match.group(1)}{Colors.RESET}")
                return True
            else:
                print(f"{Colors.GREEN}{Icons.SUCCESS} Yêu cầu đã được gửi thành công!{Colors.RESET}")
                return True
                
        except requests.exceptions.Timeout:
            print(f"{Colors.RED}{Icons.ERROR} Timeout khi gửi yêu cầu!{Colors.RESET}")
            return False
        except Exception as e:
            print(f"{Colors.RED}{Icons.ERROR} Lỗi: {e}{Colors.RESET}")
            return False

    def run(self):
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.YELLOW}{Icons.INFO} Đang đăng nhập vào Zefoy...{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        if not self.send_captcha(): 
            print(f"{Colors.RED}{Icons.ERROR} Không thể đăng nhập!{Colors.RESET}")
            return
        
        self.select_service()
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.GREEN}{Icons.SUCCESS} Bắt đầu gửi yêu cầu...{Colors.RESET}")
        print(f"{Colors.YELLOW}{Icons.INFO} Nhấn Ctrl+C để dừng{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")
        
        request_count = 0
        success_count = 0
        
        try:
            while self.running:
                request_count += 1
                print(f"{Colors.CYAN}{'─'*60}{Colors.RESET}")
                print(f"{Colors.BOLD}Yêu cầu #{request_count} | Thành công: {success_count}{Colors.RESET}")
                print(f"{Colors.CYAN}{'─'*60}{Colors.RESET}")
                
                if self.use_service():
                    success_count += 1
                    time.sleep(2)
                else:
                    print(f"{Colors.YELLOW}{Icons.WARNING} Chờ 5s trước khi thử lại...{Colors.RESET}")
                    time.sleep(5)
                    
        except KeyboardInterrupt:
            print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
            print(f"{Colors.YELLOW}{Icons.INFO} Dừng bởi người dùng{Colors.RESET}")
            print(f"{Colors.GREEN}Tổng yêu cầu: {request_count} | Thành công: {success_count}{Colors.RESET}")
            print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

if __name__ == "__main__":
    try:
        Z = Zefoy()
        Z.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}{Icons.INFO} Chương trình đã dừng.{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}{Icons.ERROR} Lỗi nghiêm trọng: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
