import tkinter as tk
from tkinter import filedialog, messagebox, ttk


import os
import sys
import webbrowser
import cv2
import numpy as np
def resource_path(relative_path):
    """
    PyInstaller 환경에서 리소스 파일 경로를 안전하게 반환
    개발 환경에서는 상대경로, 빌드 환경에서는 _MEIPASS 사용
    """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

__version__ = '1.0.1'  # 앱 버전

def capture_frame(video_path, time_sec, resolution):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception('비디오 파일을 열 수 없었습니다:')
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_num = int(round(time_sec * fps))
    if frame_num >= total_frames:
        frame_num = total_frames - 1
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise Exception('해당 시간대의 프레임을 읽는 데 실패했습니다.')
    res_map = {
        'SD': (640, 480),
        'HD': (1280, 720),
        'FHD': (1920, 1080),
        'QHD': (2560, 1440),
        '4K': (3840, 2160),
        '8K': (7680, 4320)
    }
    if resolution in res_map:
        size = res_map[resolution]
        frame = cv2.resize(frame, size)
    # '원본' 또는 기타는 리사이즈 없이 반환
    return frame

class FrameExporterApp:
    def __init__(self, root):
        self.root = root
        self.root.title('프레임 캡처')
        # 아이콘 적용 (icon.ico가 있으면 적용, 없으면 무시)
        try:
            icon_path = resource_path('icon.ico')
            self.root.iconbitmap(icon_path)
        except Exception:
            pass
        self.video_path = ''
        self.create_menu()
        self.create_widgets()
        # 프로그램 최초 실행 시 자동 업데이트 체크
        self.root.after(100, self.check_update_silent)

    def check_update_silent(self):
        """
        프로그램 시작 시: 업데이트가 있을 때만 안내, 최신이면 아무 메시지도 띄우지 않음
        """
        try:
            import requests
        except ImportError:
            # 조용히 무시
            return
        try:
            api_url = 'https://api.github.com/repos/seunghoon4176/frame-capture/releases/latest'
            resp = requests.get(api_url, timeout=5)
            if resp.status_code != 200:
                return
            data = resp.json()
            latest_ver = data.get('tag_name', '').lstrip('v')
            release_url = data.get('html_url', 'https://github.com/seunghoon4176/frame-capture/releases')
            if not latest_ver:
                return
            if latest_ver != __version__:
                if messagebox.askyesno('업데이트 확인', f'새 버전이 있습니다! (현재: v{__version__}, 최신: v{latest_ver})\n업데이트 페이지를 여시겠습니까?'):
                    webbrowser.open(release_url)
        except Exception:
            pass

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        # 도움말 메뉴
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label='업데이트 확인', command=self.check_update)
        helpmenu.add_separator()
        helpmenu.add_command(label='버전 정보', command=self.show_version)
        menubar.add_cascade(label='도움말', menu=helpmenu)
        # 문의 메뉴
        contactmenu = tk.Menu(menubar, tearoff=0)
        contactmenu.add_command(label='개발자에게 문의하기', command=self.open_contact_link)
        menubar.add_cascade(label='문의', menu=contactmenu)

    def open_contact_link(self):
        url = 'https://open.kakao.com/o/sObJJxJh'
        webbrowser.open(url)

    def show_version(self):
        messagebox.showinfo('버전 정보', f'현재 버전: {__version__}')

    def check_update(self):
        try:
            import requests
        except ImportError:
            messagebox.showwarning('업데이트 확인', 'requests 모듈이 필요합니다.\n명령 프롬프트에서 "pip install requests"를 실행해 주세요.')
            return
        try:
            api_url = 'https://api.github.com/repos/seunghoon4176/frame-capture/releases/latest'
            resp = requests.get(api_url, timeout=5)
            if resp.status_code != 200:
                raise Exception('GitHub API 오류')
            data = resp.json()
            latest_ver = data.get('tag_name', '').lstrip('v')
            release_url = data.get('html_url', 'https://github.com/seunghoon4176/frame-capture/releases')
            if not latest_ver:
                raise Exception('최신 버전 정보를 찾을 수 없습니다.')
            if latest_ver == __version__:
                messagebox.showinfo('업데이트 확인', f'최신 버전입니다! (v{__version__})')
            else:
                if messagebox.askyesno('업데이트 확인', f'새 버전이 있습니다! (현재: v{__version__}, 최신: v{latest_ver})\n업데이트 페이지를 여시겠습니까?'):
                    webbrowser.open(release_url)
        except Exception as e:
            messagebox.showerror('업데이트 확인', f'업데이트 확인에 실패했습니다: {e}')

    def create_widgets(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid()

        # File selection
        self.file_label = ttk.Label(frm, text='파일이 선택되지 않음', width=40)
        self.file_label.grid(row=0, column=0, padx=5, pady=5)
        file_btn = ttk.Button(frm, text='비디오 파일 선택', command=self.select_file)
        file_btn.grid(row=0, column=1, padx=5, pady=5)

        # Time input
        ttk.Label(frm, text='시간 (초 단위로, 예를 들어 4.15):').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.time_input = ttk.Entry(frm)
        self.time_input.grid(row=1, column=1, padx=5, pady=5)
        # placeholder만, 값은 비워둠

        # Resolution selection
        res_options = ['SD', 'HD', 'FHD', 'QHD', '4K', '8K', '원본']
        ttk.Label(frm, text='해상도:').grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.res_combo = ttk.Combobox(frm, values=res_options, state='readonly')
        self.res_combo.grid(row=2, column=1, padx=5, pady=5)
        self.res_combo.set('FHD')

        # Export button
        export_btn = ttk.Button(frm, text='프레임 캡처', command=self.export_frame)
        export_btn.grid(row=3, column=0, columnspan=2, pady=10)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title='비디오 파일 선택',
            filetypes=[('비디오 파일', '*.mp4 *.avi *.mov *.mkv')]
        )
        if file_path:
            self.video_path = file_path
            self.file_label.config(text=os.path.basename(file_path))

    def export_frame(self):
        if not self.video_path:
            messagebox.showwarning('오류', '비디오 파일을 선택해 주세요.')
            return
        try:
            time_sec = float(self.time_input.get())
        except ValueError:
            messagebox.showwarning('오류', '캡처할 시간대를 입력해 주세요.')
            return
        resolution = self.res_combo.get()
        try:
            frame = capture_frame(self.video_path, time_sec, resolution)
            # 프로그램과 같은 위치에 저장
            default_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
            save_path = filedialog.asksaveasfilename(
                title='캡처',
                defaultextension='.png',
                filetypes=[('PNG Images', '*.png'), ('JPEG Images', '*.jpg')],
                initialfile='frame.png',
                initialdir=default_dir
            )
            if save_path:
                # 한글 등 특수문자 파일명 안전하게 변환
                import re
                base, ext = os.path.splitext(save_path)
                # 확장자가 jpg면 png로 강제 변경
                if ext.lower() != '.png':
                    ext = '.png'
                safe_base = re.sub(r'[^\w\d_]', '_', os.path.basename(base))
                # 저장 경로를 프로그램과 같은 위치로 강제 지정
                safe_path = os.path.join(default_dir, safe_base + ext)
                cv2.imwrite(safe_path, frame)
                messagebox.showinfo('성공', f'캡처된 경로는 {safe_path} 입니다.')
        except Exception as e:
            messagebox.showerror('오류', f'캡처에 실패했습니다: {e}')

if __name__ == '__main__':
    root = tk.Tk()
    app = FrameExporterApp(root)
    root.mainloop()