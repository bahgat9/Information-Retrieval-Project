import tkinter as tk
from tkinter import ttk, messagebox
from crawler.js_handler import JSScraper
import pandas as pd
from datetime import datetime, timedelta
import time


class BookingCrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Booking.com Crawler")
        self.root.geometry("500x400")

        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Add title
        ttk.Label(self.main_frame,
                 text="=== Booking.com Crawler ===",
                 font=('Arial', 14)).grid(row=0, column=0, columnspan=2, pady=10)

        # Destination
        ttk.Label(self.main_frame, text="Destination:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.destination_entry = ttk.Entry(self.main_frame, width=40)
        self.destination_entry.grid(row=1, column=1, pady=5)
        self.destination_entry.insert(0, "Paris, Madrid")

        # Check-in date
        ttk.Label(self.main_frame, text="Check-in Date (YYYY-MM-DD):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.checkin_entry = ttk.Entry(self.main_frame, width=40)
        self.checkin_entry.grid(row=2, column=1, pady=5)
        self.checkin_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        # Check-out date
        ttk.Label(self.main_frame, text="Check-out Date (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.checkout_entry = ttk.Entry(self.main_frame, width=40)
        self.checkout_entry.grid(row=3, column=1, pady=5)
        self.checkout_entry.insert(0, (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))

        # Max results
        ttk.Label(self.main_frame, text="Maximum Results:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.max_results_entry = ttk.Entry(self.main_frame, width=40)
        self.max_results_entry.grid(row=4, column=1, pady=5)
        self.max_results_entry.insert(0, "20")

        # Headless mode checkbox
        self.headless_var = tk.BooleanVar(value=True)
        self.headless_check = ttk.Checkbutton(
            self.main_frame,
            text="Run browser in headless mode",
            variable=self.headless_var
        )
        self.headless_check.grid(row=5, column=0, columnspan=2, pady=5)

        # Run button
        self.run_button = ttk.Button(
            self.main_frame,
            text="Start Crawling",
            command=self.run_crawler
        )
        self.run_button.grid(row=6, column=0, columnspan=2, pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(
            self.main_frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate'
        )
        self.progress.grid(row=7, column=0, columnspan=2, pady=10)

        # Status label
        self.status_label = ttk.Label(self.main_frame, text="Ready", foreground="blue")
        self.status_label.grid(row=8, column=0, columnspan=2)

    def run_crawler(self):
        try:
            # Get values from entries
            destination = self.destination_entry.get()
            checkin = self.checkin_entry.get()
            checkout = self.checkout_entry.get()
            max_results = int(self.max_results_entry.get())
            headless = self.headless_var.get()

            # Validate inputs
            if not destination:
                messagebox.showerror("Error", "Please enter a destination")
                return

            try:
                datetime.strptime(checkin, '%Y-%m-%d')
                datetime.strptime(checkout, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
                return

            # Update UI
            self.status_label.config(text="Scraping in progress...", foreground="orange")
            self.progress["value"] = 0
            self.root.update_idletasks()

            # Initialize scraper
            js_scraper = JSScraper(headless=headless)

            # Start scraping in a separate thread to keep UI responsive
            def scraping_thread():
                try:
                    # Get the hotels DataFrame
                    hotels_df = js_scraper.scrape_hotels(
                        destination=destination,
                        checkin=checkin,
                        checkout=checkout,
                        max_results=max_results
                    )

                    if hotels_df is not None and not hotels_df.empty:
                        # Save with timestamp
                        filename = f"hotels_data_{destination.replace(',', '').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv"
                        hotels_df.to_csv(filename, index=False)

                        # Update UI
                        self.status_label.config(
                            text=f"Success! Scraped {len(hotels_df)} hotels. Saved to {filename}",
                            foreground="green"
                        )
                        self.progress["value"] = 100

                        # Show success message
                        messagebox.showinfo(
                            "Success",
                            f"Successfully scraped {len(hotels_df)} hotels.\nData saved to {filename}"
                        )
                    else:
                        self.status_label.config(text="No hotels were scraped", foreground="red")
                        messagebox.showerror("Error",
                                            "No hotels were scraped. Please check the website structure or try again.")

                except Exception as e:
                    self.status_label.config(text=f"Error: {str(e)}", foreground="red")
                    messagebox.showerror("Error", f"JS scraping failed: {str(e)}")
                finally:
                    self.progress["value"] = 100

            # Start the scraping thread
            import threading
            thread = threading.Thread(target=scraping_thread)
            thread.start()

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for maximum results")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


def main():
    root = tk.Tk()
    app = BookingCrawlerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()