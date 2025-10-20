#!/usr/bin/env python3
"""
Chat History Viewer GUI

A simple GUI to display chat histories as if they were real conversations
with a chatbot. Shows the RAG system in action with a clean interface.

Usage: python3 chat_viewer_gui.py
"""

import sys
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from pathlib import Path
from datetime import datetime
import threading


class ChatViewerGUI:
    """GUI for viewing chat histories as conversations."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RAG Chat History Viewer")
        self.root.geometry("1000x700")
        self.root.configure(bg='#f0f0f0')
        
        # Chat history data
        self.chat_histories = {}
        self.current_chat = None
        
        # Create GUI elements
        self.create_widgets()
        self.load_chat_histories()
    
    def create_widgets(self):
        """Create the GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 RAG Chat History Viewer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Chat selection frame
        selection_frame = ttk.LabelFrame(main_frame, text="Select Chat Session", padding="10")
        selection_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Chat list
        self.chat_listbox = tk.Listbox(selection_frame, height=15, width=40)
        self.chat_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_listbox.bind('<<ListboxSelect>>', self.on_chat_select)
        
        # Scrollbar for chat list
        chat_scrollbar = ttk.Scrollbar(selection_frame, orient="vertical", command=self.chat_listbox.yview)
        chat_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.chat_listbox.configure(yscrollcommand=chat_scrollbar.set)
        
        # Chat info frame
        info_frame = ttk.LabelFrame(selection_frame, text="Chat Info", padding="5")
        info_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.chat_info_text = tk.Text(info_frame, height=4, width=40, wrap=tk.WORD)
        self.chat_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Chat display frame
        chat_frame = ttk.LabelFrame(main_frame, text="Chat Conversation", padding="10")
        chat_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            height=25, 
            width=60, 
            wrap=tk.WORD,
            font=('Arial', 10),
            bg='#ffffff',
            fg='#333333'
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure chat display tags for styling
        self.chat_display.tag_configure("user", foreground="#2c5aa0", font=('Arial', 10, 'bold'))
        self.chat_display.tag_configure("assistant", foreground="#2d5016", font=('Arial', 10))
        self.chat_display.tag_configure("timestamp", foreground="#666666", font=('Arial', 8))
        self.chat_display.tag_configure("context", foreground="#8b4513", font=('Arial', 9, 'italic'))
        self.chat_display.tag_configure("separator", foreground="#cccccc")
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Buttons
        self.refresh_btn = ttk.Button(control_frame, text="🔄 Refresh", command=self.refresh_chats)
        self.refresh_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.export_btn = ttk.Button(control_frame, text="💾 Export Chat", command=self.export_chat)
        self.export_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.clear_btn = ttk.Button(control_frame, text="🗑️ Clear Display", command=self.clear_display)
        self.clear_btn.grid(row=0, column=2, padx=(0, 5))
        
        self.about_btn = ttk.Button(control_frame, text="ℹ️ About", command=self.show_about)
        self.about_btn.grid(row=0, column=3)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Select a chat session to view")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def load_chat_histories(self):
        """Load all chat history files."""
        try:
            chat_dir = Path("chat_history")
            if not chat_dir.exists():
                self.status_var.set("No chat history directory found")
                return
            
            self.chat_histories = {}
            chat_files = list(chat_dir.glob("*.json"))
            
            if not chat_files:
                self.status_var.set("No chat history files found")
                return
            
            for chat_file in chat_files:
                try:
                    with open(chat_file, 'r', encoding='utf-8') as f:
                        chat_data = json.load(f)
                    
                    # Extract chat info
                    session_id = chat_data.get('session_id', chat_file.stem)
                    topic = chat_data.get('topic', 'Unknown')
                    created_at = chat_data.get('created_at', 'Unknown')
                    messages = chat_data.get('messages', [])
                    
                    # Store chat data
                    self.chat_histories[session_id] = {
                        'file': chat_file,
                        'topic': topic,
                        'created_at': created_at,
                        'messages': messages,
                        'message_count': len(messages)
                    }
                    
                    # Add to listbox
                    display_text = f"{topic} ({len(messages)} messages) - {created_at}"
                    self.chat_listbox.insert(tk.END, display_text)
                    
                except Exception as e:
                    print(f"Error loading {chat_file}: {e}")
                    continue
            
            self.status_var.set(f"Loaded {len(self.chat_histories)} chat sessions")
            
        except Exception as e:
            self.status_var.set(f"Error loading chat histories: {e}")
            messagebox.showerror("Error", f"Failed to load chat histories: {e}")
    
    def on_chat_select(self, event):
        """Handle chat selection."""
        selection = self.chat_listbox.curselection()
        if not selection:
            return
        
        # Get selected chat
        chat_keys = list(self.chat_histories.keys())
        if selection[0] < len(chat_keys):
            selected_chat = chat_keys[selection[0]]
            self.current_chat = selected_chat
            self.display_chat(selected_chat)
    
    def display_chat(self, chat_id):
        """Display the selected chat conversation."""
        if chat_id not in self.chat_histories:
            return
        
        chat_data = self.chat_histories[chat_id]
        
        # Clear display
        self.chat_display.delete(1.0, tk.END)
        
        # Display chat info
        self.chat_info_text.delete(1.0, tk.END)
        info_text = f"Topic: {chat_data['topic']}\n"
        info_text += f"Created: {chat_data['created_at']}\n"
        info_text += f"Messages: {chat_data['message_count']}\n"
        info_text += f"Session ID: {chat_id[:8]}..."
        self.chat_info_text.insert(tk.END, info_text)
        
        # Display conversation
        self.chat_display.insert(tk.END, f"🤖 Chat Session: {chat_data['topic']}\n", "separator")
        self.chat_display.insert(tk.END, f"📅 Started: {chat_data['created_at']}\n", "separator")
        self.chat_display.insert(tk.END, f"💬 Messages: {chat_data['message_count']}\n", "separator")
        self.chat_display.insert(tk.END, "=" * 80 + "\n\n", "separator")
        
        # Display messages
        for i, message in enumerate(chat_data['messages']):
            role = message.get('role', 'unknown')
            content = message.get('content', '')
            timestamp = message.get('timestamp', '')
            context = message.get('context', [])
            
            if role == 'user':
                self.chat_display.insert(tk.END, f"👤 You: ", "user")
                self.chat_display.insert(tk.END, f"{content}\n", "user")
                if timestamp:
                    self.chat_display.insert(tk.END, f"   📅 {timestamp}\n", "timestamp")
                
            elif role == 'assistant':
                self.chat_display.insert(tk.END, f"🤖 Assistant: ", "assistant")
                self.chat_display.insert(tk.END, f"{content}\n", "assistant")
                if timestamp:
                    self.chat_display.insert(tk.END, f"   📅 {timestamp}\n", "timestamp")
                
                # Show context if available
                if context:
                    self.chat_display.insert(tk.END, f"   📚 Context: Used {len(context)} relevant papers\n", "context")
                    for j, ctx in enumerate(context[:3]):  # Show first 3 context items
                        title = ctx.get('metadata', {}).get('title', 'Unknown')
                        self.chat_display.insert(tk.END, f"      {j+1}. {title[:60]}{'...' if len(title) > 60 else ''}\n", "context")
                    if len(context) > 3:
                        self.chat_display.insert(tk.END, f"      ... and {len(context) - 3} more\n", "context")
            
            self.chat_display.insert(tk.END, "\n", "separator")
        
        # Scroll to top
        self.chat_display.see(1.0)
        
        # Update status
        self.status_var.set(f"Displaying chat: {chat_data['topic']} ({chat_data['message_count']} messages)")
    
    def refresh_chats(self):
        """Refresh the chat list."""
        self.chat_listbox.delete(0, tk.END)
        self.chat_histories.clear()
        self.load_chat_histories()
        self.status_var.set("Chat list refreshed")
    
    def export_chat(self):
        """Export the current chat to a text file."""
        if not self.current_chat:
            messagebox.showwarning("No Selection", "Please select a chat session first.")
            return
        
        try:
            # Get save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialname=f"chat_{self.current_chat[:8]}.txt"
            )
            
            if not filename:
                return
            
            # Export chat
            chat_data = self.chat_histories[self.current_chat]
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"RAG Chat Export\n")
                f.write(f"Topic: {chat_data['topic']}\n")
                f.write(f"Created: {chat_data['created_at']}\n")
                f.write(f"Messages: {chat_data['message_count']}\n")
                f.write("=" * 80 + "\n\n")
                
                for message in chat_data['messages']:
                    role = message.get('role', 'unknown')
                    content = message.get('content', '')
                    timestamp = message.get('timestamp', '')
                    
                    if role == 'user':
                        f.write(f"👤 You: {content}\n")
                    elif role == 'assistant':
                        f.write(f"🤖 Assistant: {content}\n")
                    
                    if timestamp:
                        f.write(f"   📅 {timestamp}\n")
                    f.write("\n")
            
            self.status_var.set(f"Chat exported to {filename}")
            messagebox.showinfo("Success", f"Chat exported successfully to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export chat: {e}")
    
    def clear_display(self):
        """Clear the chat display."""
        self.chat_display.delete(1.0, tk.END)
        self.chat_info_text.delete(1.0, tk.END)
        self.current_chat = None
        self.status_var.set("Display cleared")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """RAG Chat History Viewer

A GUI application for viewing chat histories from the RAG (Retrieval-Augmented Generation) system.

Features:
• View chat sessions as conversations
• See context retrieval information
• Export chats to text files
• Browse multiple chat sessions

This tool helps visualize how the RAG system retrieves relevant papers and generates responses based on the retrieved context.

Built for the ArXiv RAG Pipeline Demo."""
        
        messagebox.showinfo("About RAG Chat Viewer", about_text)


def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = ChatViewerGUI(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()
