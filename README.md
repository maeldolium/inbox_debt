# Inbox Debt Automation

## Project Overview
This project aims to automate the unsubscription and deletion of emails in a Gmail inbox on behalf of the user. It will save time for users and help manage email deletion effectively, distinguishing between emails to be deleted and those on a whitelist that should not be touched.

## Features
- Connect to a Gmail account and authenticate securely.
- Detect newsletters and promotional senders automatically.
- Read and parse List-Unsubscribe headers to find safe opt-out paths.
- Group and summarize emails by sender to speed up decisions.
- Mark whitelist senders so their emails are never touched.
- Unsubscribe from unwanted senders automatically when possible.
- Delete unwanted emails in bulk while respecting the whitelist.
- Provide optional manual review before deleting or unsubscribing.
- Offer a GUI (Tkinter or Flask) for non-technical users once the backend is stable.

## Technologies Used
- Python
- Gmail API
- Tkinter / Flask (for GUI)

## Future Enhancements
- Implement advanced filtering options.
- Improve user experience with a more intuitive interface.

## License

This project is licensed under the Creative Commons BY-NC 4.0 License.

You are free to study and reuse the code for personal and educational purposes,
but any commercial use is strictly prohibited.