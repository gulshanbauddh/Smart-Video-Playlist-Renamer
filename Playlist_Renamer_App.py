import os
import difflib
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading

# yt-dlp library check karna
try:
    import yt_dlp
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "yt-dlp"], shell=True)
    import yt_dlp

class RenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Video Renamer")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Styling
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main Frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title Label
        title_label = ttk.Label(main_frame, text="Smart Video Playlist Renamer", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # --- YouTube Link Section ---
        ttk.Label(main_frame, text="YouTube Playlist Link:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(10, 2))
        self.url_entry = ttk.Entry(main_frame, width=70)
        self.url_entry.pack(fill=tk.X, ipady=4)
        
        # --- Folder Selection Section ---
        ttk.Label(main_frame, text="Select Video Folder (HDD):", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(15, 2))
        folder_frame = ttk.Frame(main_frame)
        folder_frame.pack(fill=tk.X)
        
        self.folder_entry = ttk.Entry(folder_frame, width=55)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        
        browse_btn = ttk.Button(folder_frame, text="Browse Folder", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # --- Status Box ---
        ttk.Label(main_frame, text="Status Log:", font=("Arial", 9)).pack(anchor=tk.W, pady=(15, 2))
        self.status_box = tk.Text(main_frame, height=6, width=70, state=tk.DISABLED, bg="#f0f0f0", font=("Consolas", 9))
        self.status_box.pack(fill=tk.BOTH, expand=True)
        
        # --- Start Button ---
        self.start_btn = ttk.Button(main_frame, text="START RENAMING", command=self.start_process_thread)
        self.start_btn.pack(pady=15, ipady=6, fill=tk.X)

    def browse_folder(self):
        selected_folder = filedialog.askdirectory()
        if selected_folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, selected_folder)
            
    def log(self, text):
        self.status_box.config(state=tk.NORMAL)
        self.status_box.insert(tk.END, text + "\n")
        self.status_box.see(tk.END)
        self.status_box.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def start_process_thread(self):
        # Background thread me chalayenge taaki UI hang na ho
        threading.Thread(target=self.rename_videos, daemon=True).start()

    def rename_videos(self):
        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip()
        
        if not url or not folder:
            messagebox.showwarning("Input Missing", "Kripya YouTube Link aur Folder Path dono daalein!")
            return
            
        if not os.path.exists(folder):
            messagebox.showerror("Error", "Diya gaya Folder Path sahi nahi hai!")
            return
            
        self.start_btn.config(state=tk.DISABLED)
        self.status_box.config(state=tk.NORMAL)
        self.status_box.delete('1.0', tk.END)
        self.status_box.config(state=tk.DISABLED)
        
        self.log("YouTube se titles fetch ho rahe hain... Thoda intezar karein...")
        
        ydl_opts = {'extract_flat': True, 'skip_download': True, 'quiet': True}
        playlist_titles = []
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_data = ydl.extract_info(url, download=False)
                if 'entries' in playlist_data:
                    for entry in playlist_data['entries']:
                        if entry and 'title' in entry:
                            playlist_titles.append(entry['title'].strip())
        except Exception as e:
            self.log(f"Error: Playlist fetch nahi ho payi!\n{e}")
            self.start_btn.config(state=tk.NORMAL)
            return

        total_videos = len(playlist_titles)
        self.log(f"Sahi baat! Playlist me {total_videos} videos mili hain.\nNumbring shuru ho rahi hai...")
        
        folder_files = os.listdir(folder)
        count = 0
        
        for index, pl_title in enumerate(playlist_titles, start=1):
            prefix = f"{index:03d}_"
            matches = difflib.get_close_matches(pl_title, folder_files, n=1, cutoff=0.2)
            
            if matches:
                best_match_file = matches[0]
                old_path = os.path.join(folder, best_match_file)
                new_name = prefix + best_match_file
                new_path = os.path.join(folder, new_name)
                
                if not best_match_file.startswith(prefix) and "Playlist_Renamer_App" not in best_match_file:
                    os.rename(old_path, new_path)
                    self.log(f"[{index:03d}] Renamed: {best_match_file[:30]}... -> {prefix}...")
                    folder_files.remove(best_match_file)
                    count += 1
            else:
                self.log(f"⚠️ Match nahi mila: {pl_title[:40]}...")

        self.log(f"\n🎉 Kaam Poora Hua! Total {count} files rename hui hain.")
        messagebox.showinfo("Success", f"Task Completed!\nTotal {count} files rename ho gayi hain.")
        self.start_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = RenamerApp(root)
    root.mainloop()