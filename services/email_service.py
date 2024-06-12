import email
import imaplib
from imapclient import IMAPClient

from colorama import Fore

from typing import Tuple, List, Dict, Optional


class EmailService:
    def __init__(self, email_address: str, password: str, imap_server: str = "outlook.office365.com"):
        self.imap_server = imap_server
        self.email_address = email_address
        self.password = password

        self.imap_message_format = "RFC822"
        self.imap = IMAPClient(imap_server)

    def do_login(self) -> bool or Tuple[bool, str]:
        try:
            self.imap.login(self.email_address, self.password)
            self.imap.select_folder("INBOX")
            return True
        except imaplib.IMAP4.error as imap_error:
            print(Fore.RED + f"IMAP error: {imap_error}")
            return False

    def do_logout(self) -> None:
        try:
            self.imap.logout()
        except:
            pass

    def get_all_emails(self, max_amount: int = -1) -> Optional[List[Dict[str, str]]]:
        emails = []

        messages = self.imap.search(["FROM", "sales@tinytronics.nl"])  # another example: ['FROM', 'email@outlook.example']
        for uid, message_data in self.imap.fetch(messages, self.imap_message_format).items():
            print(message_data)
            print(message_data[b"RFC822"])

            # message = email.message_from_bytes(message_data[self.imap_message_format])
            #
            # message_content = []
            # for part in message.walk():
            #     if part.get_content_type() == "text/plain":
            #         message_content.append(part.as_string())
            #
            # emails.append({
            #     "from": message.get("From"),
            #     "to": message.get("To"),
            #     "BCC": message.get("BCC"),
            #     "date": message.get("Date"),
            #     "subject": message.get("Subject"),
            #     "content": "\n".join(message_content)
            # })

        return emails
