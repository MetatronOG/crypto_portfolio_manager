import requests
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import matplotlib.pyplot as plt
import io
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

class AlertManager:
    def __init__(self, config):
        """Initialize the alert manager with configuration"""
        self.config = config
        self.telegram_alerts = TelegramAlerts(config) if config.get("alerts.telegram.bot_token") else None
        self.email_alerts = EmailAlerts(config) if config.get("alerts.email.address") else None
        self.webhook_alerts = WebhookAlerts(config) if config.get("alerts.webhooks") else None
        self.custom_rules = self.load_custom_rules()
        
    def load_custom_rules(self):
        """Load custom alert rules from configuration"""
        return self.config.get("custom_alert_rules", [])
    
    def should_alert(self, transaction_data):
        """Check if transaction meets any alert rules"""
        # Always alert if no custom rules (default behavior)
        if not self.custom_rules:
            return True
            
        # Check against each custom rule
        for rule in self.custom_rules:
            if self.transaction_matches_rule(transaction_data, rule):
                return True
                
        return False
    
    def transaction_matches_rule(self, transaction, rule):
        """Check if transaction matches a specific rule"""
        # Token match
        if 'token' in rule and transaction['token'] != rule['token']:
            return False
            
        # Amount threshold
        if 'min_amount' in rule and transaction['amount'] < rule['min_amount']:
            return False
            
        # USD value threshold
        if 'min_usd_value' in rule and transaction['usd_value'] < rule['min_usd_value']:
            return False
            
        # Transaction type
        if 'transaction_type' in rule and transaction['type'] != rule['transaction_type']:
            return False
            
        # More complex rules would go here
            
        return True
    
    def send_alert(self, transaction_data):
        """Send alerts through all configured channels if rules match"""
        if not self.should_alert(transaction_data):
            logger.info(f"Transaction {transaction_data['tx_hash']} doesn't match alert rules")
            return
            
        # Determine alert level based on USD value
        if transaction_data['usd_value'] >= 5000000:
            level = "CRITICAL"
        elif transaction_data['usd_value'] >= 1000000:
            level = "HIGH"
        else:
            level = "MEDIUM"
            
        # Generate chart for large transactions
        chart_buffer = None
        if transaction_data['usd_value'] >= 1000000:
            chart_buffer = self.generate_market_chart(transaction_data['token'])
            
        # Send alert through each configured channel
        if self.telegram_alerts:
            self.telegram_alerts.send_alert(transaction_data, level, chart_buffer)
            
        if self.email_alerts:
            self.email_alerts.send_alert(transaction_data, level, chart_buffer)
            
        if self.webhook_alerts:
            self.webhook_alerts.send_alert(transaction_data, level)
    
    def generate_market_chart(self, token):
        """Generate candlestick chart for the token"""
        # This would integrate with a market data API to get historical prices
        # For now, create a simple placeholder chart
        
        plt.figure(figsize=(10, 6))
        plt.title(f"{token}/USD 24h Price Movement")
        plt.xlabel("Time")
        plt.ylabel("Price (USD)")
        
        # Create placeholder data
        times = pd.date_range(end=datetime.now(), periods=24, freq='H')
        prices = [100 + i + (i*i/100) for i in range(24)]  # Dummy data
        
        plt.plot(times, prices)
        plt.grid(True)
        
        # Save to buffer instead of file
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        return buf


class TelegramAlerts:
    def __init__(self, config):
        """Initialize Telegram alerts with config"""
        self.bot_token = config.get("alerts.telegram.bot_token")
        self.chat_id = config.get("alerts.telegram.chat_id")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/"
        
    def send_alert(self, transaction_data, level, chart_buffer=None):
        """Send alert to Telegram"""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram alert not sent: missing bot_token or chat_id")
            return
            
        message = self.format_message(transaction_data, level)
        
        try:
            if chart_buffer and transaction_data['usd_value'] >= 1000000:
                self.send_photo_with_caption(chart_buffer, message)
            else:
                self.send_message(message)
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {str(e)}")
    
    def format_message(self, transaction_data, level):
        """Format transaction data into readable message"""
        emoji_prefix = "🚨" if level == "CRITICAL" else "⚠️" if level == "HIGH" else "📊"
        
        message = f"{emoji_prefix} WHALE ALERT [{level}] {emoji_prefix}\n\n"
        message += f"Token: {transaction_data['token']}\n"
        message += f"Amount: {transaction_data['amount']:,.2f}\n"
        message += f"USD Value: ${transaction_data['usd_value']:,.2f}\n"
        message += f"Type: {transaction_data['type'].upper()}\n\n"
        
        message += f"From: {self.format_address(transaction_data['from_address'])}\n"
        message += f"To: {self.format_address(transaction_data['to_address'])}\n\n"
        
        message += f"Time: {transaction_data['timestamp']}\n"
        
        if 'price_impact' in transaction_data and transaction_data['price_impact'] > 0:
            message += f"Est. Price Impact: {transaction_data['price_impact']}%\n\n"
            
        # Add blockchain explorer link
        if transaction_data.get('blockchain') == 'ethereum':
            message += f"🔍 View: https://etherscan.io/tx/{transaction_data['tx_hash']}"
            
        return message
    
    def format_address(self, address):
        """Format and possibly label an address"""
        # This would integrate with wallet labels
        # For now just truncate the address
        return f"{address[:6]}...{address[-4:]}"
    
    def send_message(self, message):
        """Send text message to Telegram"""
        params = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(f"{self.api_url}sendMessage", params=params)
        if response.status_code != 200:
            logger.error(f"Failed to send Telegram message: {response.text}")
            
    def send_photo_with_caption(self, photo_buffer, caption):
        """Send photo with caption to Telegram"""
        url = f"{self.api_url}sendPhoto"
        
        files = {
            'photo': ('chart.png', photo_buffer, 'image/png')
        }
        
        data = {
            'chat_id': self.chat_id,
            'caption': caption[:1024],  # Telegram caption limit
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, files=files)
        if response.status_code != 200:
            logger.error(f"Failed to send Telegram photo: {response.text}")
            # Fallback to text message
            self.send_message(caption)


class EmailAlerts:
    def __init__(self, config):
        """Initialize email alerts with config"""
        self.email = config.get("alerts.email.address")
        self.password = config.get("alerts.email.password")
        self.smtp_server = config.get("alerts.email.smtp_server", "smtp.gmail.com")
        self.recipients = config.get("alerts.email.recipients", [self.email])
        
    def send_alert(self, transaction_data, level, chart_buffer=None):
        """Send alert via email"""
        if not self.email or not self.password:
            logger.warning("Email alert not sent: missing email or password")
            return
            
        subject = f"🚨 Whale Alert: {transaction_data['amount']} {transaction_data['token']} {transaction_data['type']} detected"
        
        # Create message
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.email
        
        # Handle multiple recipients
        if isinstance(self.recipients, list):
            msg['To'] = ', '.join(self.recipients)
        else:
            msg['To'] = self.recipients
            
        # Format email body
        body = self.format_message(transaction_data, level)
        msg.attach(MIMEText(body, 'html'))
        
        # Attach chart if available
        if chart_buffer:
            img = MIMEImage(chart_buffer.read())
            img.add_header('Content-ID', '<chart>')
            img.add_header('Content-Disposition', 'inline', filename='chart.png')
            msg.attach(img)
            
            # Reference image in HTML
            body_with_image = body + '<br><img src="cid:chart" alt="Price Chart">'
            msg.attach(MIMEText(body_with_image, 'html'))
            
        try:
            # Connect to SMTP server
            with smtplib.SMTP_SSL(self.smtp_server, 465) as server:
                server.login(self.email, self.password)
                server.send_message(msg)
                logger.info(f"Email alert sent to {self.recipients}")
        except Exception as e:
            logger.error(f"Failed to send email alert: {str(e)}")
    
    def format_message(self, transaction_data, level):
        """Format transaction data into HTML email"""
        color = "#FF0000" if level == "CRITICAL" else "#FFA500" if level == "HIGH" else "#0000FF"
        
        html = f"""
        <html>
        <body>
            <h2 style="color: {color};">WHALE ALERT - {level}</h2>
            <table border="1" cellpadding="5" style="border-collapse: collapse;">
                <tr>
                    <th style="text-align: left;">Token</th>
                    <td>{transaction_data['token']}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">Amount</th>
                    <td>{transaction_data['amount']:,.2f}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">USD Value</th>
                    <td>${transaction_data['usd_value']:,.2f}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">Type</th>
                    <td>{transaction_data['type'].upper()}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">From</th>
                    <td>{transaction_data['from_address']}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">To</th>
                    <td>{transaction_data['to_address']}</td>
                </tr>
                <tr>
                    <th style="text-align: left;">Time</th>
                    <td>{transaction_data['timestamp']}</td>
                </tr>
        """
        
        if 'price_impact' in transaction_data and transaction_data['price_impact'] > 0:
            html += f"""
                <tr>
                    <th style="text-align: left;">Est. Price Impact</th>
                    <td>{transaction_data['price_impact']}%</td>
                </tr>
            """
            
        html += """
            </table>
        """
        
        # Add blockchain explorer link
        if transaction_data.get('blockchain') == 'ethereum':
            html += f"""
            <p>
                <a href="https://etherscan.io/tx/{transaction_data['tx_hash']}">
                    View Transaction on Etherscan
                </a>
            </p>
            """
            
        html += """
        </body>
        </html>
        """
        
        return html


class WebhookAlerts:
    def __init__(self, config):
        """Initialize webhook alerts with config"""
        self.webhooks = config.get("alerts.webhooks", [])
        
    def send_alert(self, transaction_data, level, chart_buffer=None):
        """Send alert to all configured webhooks"""
        if not self.webhooks:
            return
            
        # Prepare payload
        payload = {
            "event": "whale_alert",
            "level": level,
            "transaction": transaction_data
        }
        
        # Send to each webhook
        for webhook in self.webhooks:
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(webhook, headers=headers, data=json.dumps(payload))
                
                if response.status_code >= 200 and response.status_code < 300:
                    logger.info(f"Webhook alert sent to {webhook}")
                else:
                    logger.error(f"Failed to send webhook to {webhook}: {response.status_code} {response.text}")
            except Exception as e:
                logger.error(f"Error sending webhook to {webhook}: {str(e)}")


# Function to trigger alerts from other modules
def trigger_alert(transaction_data, config):
    """Trigger whale alerts through the alert manager"""
    alert_manager = AlertManager(config)
    alert_manager.send_alert(transaction_data) 