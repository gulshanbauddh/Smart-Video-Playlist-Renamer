import os
import re
import difflib
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import webbrowser

# Safe Import for yt_dlp
try:
    import yt_dlp
except ImportError:
    yt_dlp = None

class RenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Video Playlist Renamer v2.0 (Bug Fixed)")
        self.root.geometry("650x540")
        self.root.resizable(False, False)
        
        # FIX: Safe Window Closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.is_processing = False
        self.missing_videos = []

        # Theme Configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure("Main.TFrame", background="#f4f6f9")
        style.configure("Header.TLabel", background="#f4f6f9", foreground="#1a252f", font=("Segoe UI", 16, "bold"))
        style.configure("Sub.TLabel", background="#f4f6f9", foreground="#34495e", font=("Segoe UI", 9, "bold"))
        
        main_frame = ttk.Frame(root, padding="20", style="Main.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="🎬 Smart Video Playlist Renamer", style="Header.TLabel")
        title_label.pack(pady=(0, 15))
        
        # YouTube Link Input
        ttk.Label(main_frame, text="YouTube Playlist Link:", style="Sub.TLabel").pack(anchor=tk.W, pady=(5, 2))
        self.url_entry = ttk.Entry(main_frame, width=75, font=("Segoe UI", 10))
        self.url_entry.pack(fill=tk.X, ipady=5)
        
        # Folder Selection
        ttk.Label(main_frame, text="Select Video Folder (HDD):", style="Sub.TLabel").pack(anchor=tk.W, pady=(12, 2))
        folder_frame = ttk.Frame(main_frame, style="Main.TFrame")
        folder_frame.pack(fill=tk.X)
        
        self.folder_entry = ttk.Entry(folder_frame, font=("Segoe UI", 10))
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        browse_btn = ttk.Button(folder_frame, text="📁 Browse Folder", command=self.browse_folder)
        browse_btn.pack(side=tk.RIGHT, padx=(8, 0), ipady=2)
        
        # Status Log
        ttk.Label(main_frame, text="Processing Status Log:", style="Sub.TLabel").pack(anchor=tk.W, pady=(12, 2))
        self.status_box = tk.Text(main_frame, height=9, width=70, state=tk.DISABLED, bg="#ffffff", fg="#2c3e50", font=("Consolas", 9), relief=tk.SOLID, bd=1)
        self.status_box.pack(fill=tk.BOTH, expand=True)
        
        # Action Buttons
        action_frame = ttk.Frame(main_frame, style="Main.TFrame")
        action_frame.pack(fill=tk.X, pady=(15, 0))

        self.start_btn = tk.Button(
            action_frame, 
            text="▶ START RENAMING", 
            font=("Segoe UI", 10, "bold"), 
            bg="#27ae60", 
            fg="white", 
            activebackground="#219150", 
            activeforeground="white", 
            bd=0, 
            cursor="hand2",
            command=self.start_process_thread
        )
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)

        self.view_missing_btn = tk.Button(
            action_frame, 
            text="✅ Ready / No Missing", 
            font=("Segoe UI", 9, "bold"), 
            bg="#2ecc71", 
            fg="white", 
            activebackground="#27ae60", 
            activeforeground="white", 
            bd=0, 
            state=tk.DISABLED, 
            cursor="hand2",
            command=self.open_missing_window
        )
        self.view_missing_btn.pack(side=tk.RIGHT, padx=(10, 0), ipady=8)

    def on_closing(self):
        if self.is_processing:
            if not messagebox.askyesno("Warning", "Background process chal rahi hai.\nKya aap sach me band karna chahte hain?"):
                return
        self.root.destroy()

    def browse_folder(self):
        selected_folder = filedialog.askdirectory()
        if selected_folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, selected_folder)
            
    # FIX: Thread-Safe UI Update method
    def log(self, text):
        def _append():
            self.status_box.config(state=tk.NORMAL)
            self.status_box.insert(tk.END, text + "\n")
            self.status_box.see(tk.END)
            self.status_box.config(state=tk.DISABLED)
        self.root.after(0, _append)

    def start_process_thread(self):
        if self.is_processing:
            return
        if yt_dlp is None:
            messagebox.showerror("Module Error", "yt_dlp library nahi mili! Kripya 'pip install yt-dlp' karke dubara EXE banayein.")
            return
        threading.Thread(target=self.rename_videos, daemon=True).start()

    def rename_videos(self):
        self.is_processing = True
        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip()
        
        if not url or not folder:
            self.root.after(0, lambda: messagebox.showwarning("Input Missing", "Kripya YouTube Link aur Folder Path dono daalein!"))
            self.is_processing = False
            return
            
        # FIX: Validate proper directory instead of just exists
        if not os.path.isdir(folder):
            self.root.after(0, lambda: messagebox.showerror("Error", "Diya गया Folder Path मान्य (valid) नहीं है!"))
            self.is_processing = False
            return
            
        self.root.after(0, lambda: self.start_btn.config(state=tk.DISABLED, bg="#bdc3c7"))
        self.root.after(0, lambda: self.view_missing_btn.config(state=tk.DISABLED, bg="#2ecc71", fg="white", text="🔍 Checking..."))
        self.missing_videos.clear()
        
        # Clear Text Box Safely
        self.root.after(0, lambda: self.status_box.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.status_box.delete('1.0', tk.END))
        self.root.after(0, lambda: self.status_box.config(state=tk.DISABLED))
        
        self.log("YouTube se playlist titles aur links fetch ho rahe hain...")
        
        ydl_opts = {'extract_flat': True, 'skip_download': True, 'quiet': True}
        playlist_items = []
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_data = ydl.extract_info(url, download=False)
                if 'entries' in playlist_data:
                    for entry in playlist_data['entries']:
                        if entry:
                            title = entry.get('title', 'Unknown Title').strip()
                            
                            # FIX: Skip Private and Deleted videos automatically
                            if title.lower() in ['[private video]', '[deleted video]']:
                                continue
                                
                            video_id = entry.get('id', '')
                            video_url = entry.get('url') or f"https://www.youtube.com/watch?v={video_id}"
                            playlist_items.append({'title': title, 'url': video_url})
        except Exception as e:
            self.log(f"Error: Playlist fetch nahi ho payi!\n{e}")
            self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL, bg="#27ae60"))
            self.root.after(0, lambda: self.view_missing_btn.config(text="✅ Ready"))
            self.is_processing = False
            return

        total_videos = len(playlist_items)
        self.log(f"Playlist me kul {total_videos} valid videos mili hain.\nMatching shuru ho rahi hai...\n")
        
        valid_extensions = ('.mp4', '.mkv', '.webm', '.avi', '.flv', '.mov')
        folder_files = [f for f in os.listdir(folder) if f.lower().endswith(valid_extensions)]
        
        # FIX: Dictionary mapping for logic to isolate file names from their extensions & prefixes
        file_mapping = {}
        clean_names = []
        
        for f in folder_files:
            name, ext = os.path.splitext(f)
            # Remove any existing prefixes like "001_" or "02_" to avoid double-prefixing
            clean_name = re.sub(r'^\d+_\s*', '', name)
            file_mapping[clean_name.lower()] = f
            clean_names.append(clean_name.lower())

        renamed_count = 0
        
        for real_position, item in enumerate(playlist_items, start=1):
            if not self.is_processing:
                break # Exit if app was closed
                
            prefix = f"{real_position:03d}_"
            pl_title = item['title']
            video_url = item['url']
            
            # Compare pure names (no extensions, no old numbers) against YouTube title
            matches = difflib.get_close_matches(pl_title.lower(), clean_names, n=1, cutoff=0.3)
            
            if matches:
                best_match_clean = matches[0]
                original_file = file_mapping[best_match_clean]
                old_path = os.path.join(folder, original_file)
                
                # Get the actual base name from the original file, removing old prefix
                _, ext = os.path.splitext(original_file)
                base_name_without_old_prefix = re.sub(r'^\d+_\s*', '', original_file)
                
                new_name = prefix + base_name_without_old_prefix
                new_path = os.path.join(folder, new_name)
                
                if old_path != new_path:
                    try:
                        # FIX: FileExistsError Crash Protection
                        if os.path.exists(new_path) and old_path.lower() != new_path.lower():
                            self.log(f"⚠️ [{prefix[:-1]}] Conflict: '{new_name}' already exists!")
                        else:
                            os.rename(old_path, new_path)
                            self.log(f"[{prefix[:-1]}] Renamed: {new_name[:32]}...")
                            renamed_count += 1
                    except Exception as e:
                        self.log(f"❌ [{prefix[:-1]}] Rename Error: {str(e)}")
                else:
                    self.log(f"[{prefix[:-1]}] Already Correct: {new_name[:32]}...")
                
                # Ensure we do not map the same file twice
                clean_names.remove(best_match_clean)
                del file_mapping[best_match_clean]
            else:
                self.log(f"❌ [{prefix[:-1]}] MISSING (Skipped): {pl_title[:32]}...")
                self.missing_videos.append({
                    'index': f"{prefix[:-1]}",
                    'title': pl_title,
                    'url': video_url
                })

        missing_count = len(self.missing_videos)
        self.log(f"\n🎉 Process Complete!")
        self.log(f"✔️ Successful Renamed: {renamed_count}")
        self.log(f"⚠️ Missing / Skipped Numbers: {missing_count}")
        
        # Update Final UI States securely
        def finish_ui():
            if missing_count > 0:
                self.view_missing_btn.config(
                    state=tk.NORMAL, 
                    bg="#e74c3c", 
                    activebackground="#c0392b",
                    text=f"⚠️ View Missing ({missing_count})"
                )
                messagebox.showwarning(
                    "Task Completed", 
                    f"Task Complete!\n\n• Renamed Files: {renamed_count}\n• Missing Videos: {missing_count}\n\nMissing videos ka number skip kar diya gaya hai. Red button par click karke unka data dekhein."
                )
            else:
                self.view_missing_btn.config(
                    state=tk.NORMAL, 
                    bg="#2ecc71", 
                    activebackground="#27ae60",
                    text="✅ All Videos Matched"
                )
                messagebox.showinfo("Success", f"All Completed!\nSabhi {renamed_count} videos perfectly sequence me match aur rename ho gayi hain.")
                
            self.start_btn.config(state=tk.NORMAL, bg="#27ae60")
            self.is_processing = False

        self.root.after(0, finish_ui)

    def open_missing_window(self):
        if not self.missing_videos:
            messagebox.showinfo("No Missing", "Koi bhi video missing nahi hai! Sabhi videos match ho chuki hain.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Missing Videos List - ({len(self.missing_videos)} Items)")
        win.geometry("680x480")
        win.configure(bg="#f4f6f9")
        
        ttk.Label(
            win, 
            text="Niche wo videos hain jo HDD me nahi mili (aur jinka Number Skip hua hai):", 
            font=("Segoe UI", 10, "bold"),
            background="#f4f6f9"
        ).pack(anchor=tk.W, padx=15, pady=(12, 5))
        
        frame = ttk.Frame(win)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        text_area = tk.Text(frame, wrap=tk.WORD, font=("Consolas", 9), bg="#ffffff", fg="#2c3e50", relief=tk.SOLID, bd=1)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_area.yview)
        text_area.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # FIX: Secure Lambda Binding Scope
        def _bind_link(tag, link_url):
            text_area.tag_bind(tag, "<Button-1>", lambda e: webbrowser.open_new(link_url))
            text_area.tag_bind(tag, "<Enter>", lambda e: text_area.config(cursor="hand2"))
            text_area.tag_bind(tag, "<Leave>", lambda e: text_area.config(cursor=""))

        for idx, item in enumerate(self.missing_videos, start=1):
            num = item['index']
            title = item['title']
            url = item['url']

            text_area.insert(tk.END, f"[{num}] {title}\n")
            
            tag_name = f"link_{idx}"
            text_area.insert(tk.END, f"    🔗 Link: {url}\n\n", tag_name)
            text_area.tag_config(tag_name, foreground="#2980b9", underline=1)
            
            # Application of Secure Binding
            _bind_link(tag_name, url)

        text_area.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(win)
        btn_frame.pack(fill=tk.X, padx=15, pady=12)

        copy_btn = tk.Button(
            btn_frame, 
            text="📋 Copy All Links", 
            font=("Segoe UI", 9, "bold"),
            bg="#3498db", 
            fg="white", 
            bd=0, 
            cursor="hand2",
            command=self.copy_missing_links
        )
        copy_btn.pack(side=tk.LEFT, ipady=5, ipadx=10)

        save_btn = tk.Button(
            btn_frame, 
            text="💾 Save List to TXT File", 
            font=("Segoe UI", 9, "bold"),
            bg="#2c3e50", 
            fg="white", 
            bd=0, 
            cursor="hand2",
            command=self.save_missing_to_file
        )
        save_btn.pack(side=tk.RIGHT, ipady=5, ipadx=10)

    def copy_missing_links(self):
        if not self.missing_videos:
            return
        links_text = "\n".join([f"[{item['index']}] {item['title']} - {item['url']}" for item in self.missing_videos])
        self.root.clipboard_clear()
        self.root.clipboard_append(links_text)
        messagebox.showinfo("Copied", "Sabhi missing videos aur unke links Clipboard par copy ho gaye hain!")

    def save_missing_to_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            filetypes=[("Text Files", "*.txt")],
            title="Save Missing Videos List"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("=== MISSING VIDEOS & SKIPPED NUMBERS LIST ===\n\n")
                for item in self.missing_videos:
                    f.write(f"[{item['index']}] {item['title']}\nLink: {item['url']}\n\n")
            messagebox.showinfo("Saved", "File सफलतापूर्वक सेव हो गई है!")


if __name__ == "__main__":
    root = tk.Tk()
    app = RenamerApp(root)
    root.mainloop()