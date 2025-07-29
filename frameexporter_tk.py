import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import os
import cv2
import numpy as np

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
            self.root.iconbitmap('icon.ico')
        except Exception:
            pass
        self.video_path = ''
        self.create_widgets()

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
            save_path = filedialog.asksaveasfilename(
                title='캡처',
                defaultextension='.png',
                filetypes=[('PNG Images', '*.png'), ('JPEG Images', '*.jpg')],
                initialfile='frame.png'
            )
            if save_path:
                # 한글 등 특수문자 파일명 안전하게 변환
                import re
                base, ext = os.path.splitext(save_path)
                # 확장자가 jpg면 png로 강제 변경
                if ext.lower() != '.png':
                    ext = '.png'
                safe_base = re.sub(r'[^\w\d_]', '_', os.path.basename(base))
                safe_path = os.path.join(os.path.dirname(save_path), safe_base + ext)
                cv2.imwrite(safe_path, frame)
                messagebox.showinfo('성공', f'캡처된 경로는 {safe_path} 입니다.')
        except Exception as e:
            messagebox.showerror('오류', f'캡처에 실패했습니다: {e}')

if __name__ == '__main__':
    root = tk.Tk()
    app = FrameExporterApp(root)
    root.mainloop()