import smtplib, ssl, json

class Mailer:

    """
    This script initiaties the email alert function.

    """
    def __init__(self):
        # Enter your email below. This email will be used to send alerts.
        # E.g., "email@gmail.com"
        self.EMAIL = "xxtorntooblivionxx@gmail.com"
        # Enter the email password below. Note that the password varies if you have secured
        # 2 step verification turned on. You can refer the links below and create an application specific password.
        # Google mail has a guide here: https://myaccount.google.com/lesssecureapps
        # For 2 step verified accounts: https://support.google.com/accounts/answer/185833
        self.PASS = "xhmg puel znmo yomu"
        self.PORT = 465
        self.server = smtplib.SMTP_SSL('smtp.gmail.com', self.PORT)

    def send(self, mail:str, text:list):
        self.server = smtplib.SMTP_SSL('smtp.gmail.com', self.PORT)
        self.server.login(self.EMAIL, self.PASS)
        # message to be sent
        if text[0] == "Safe":
            match text[1]:
                case 1: 
                    SUBJECT = 'ALERT!'
                    TEXT = f'Your child has entered the safeZone!'
                case 0:
                    SUBJECT = 'ALERT!'
                    TEXT = f'Your child has left the safeZone!'
                    
            message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
        elif text[0] == "Danger":
            place = json.dumps(text[1], indent=4)
            SUBJECT = 'ALERT!'
            TEXT = f'Your Child is near {place}!'
            message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

        # sending the mail
        self.server.sendmail(self.EMAIL, mail, message)
        self.server.quit()
