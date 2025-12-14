"""
Notification System Module

Handles alerts and notifications for trading signals and events.
Supports multiple notification channels: console, webhook, and email.
"""

import requests
import smtplib
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List, Optional
import os


class NotificationSystem:
    """
    Manages notifications for trading signals and alerts.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the notification system.
        
        Args:
            config: Configuration dictionary for notification settings
        """
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.webhook_url = self.config.get('webhook_url', '')
        self.email_enabled = self.config.get('email_enabled', False)
        self.logger = logging.getLogger(__name__)
        
        # Email settings
        self.smtp_server = self.config.get('email_smtp_server', '')
        self.email_from = self.config.get('email_from', '')
        self.email_to = self.config.get('email_to', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', self.config.get('email_password', ''))
    
    def send_signal_alert(self, signal: Dict) -> bool:
        """
        Send alert for a trading signal.
        
        Args:
            signal: Trading signal dictionary
            
        Returns:
            True if notification sent successfully
        """
        if not self.enabled:
            return False
        
        message = self._format_signal_message(signal)
        
        success = True
        
        # Console notification
        self._log_notification(message)
        
        # Webhook notification
        if self.webhook_url:
            success = success and self._send_webhook(message, signal)
        
        # Email notification
        if self.email_enabled:
            success = success and self._send_email(
                subject="🚨 ICT Trading Signal Alert",
                body=message
            )
        
        return success
    
    def send_trade_alert(self, trade: Dict, alert_type: str = "ENTRY") -> bool:
        """
        Send alert for trade execution.
        
        Args:
            trade: Trade dictionary
            alert_type: Type of alert (ENTRY, EXIT, STOP_LOSS, TAKE_PROFIT)
            
        Returns:
            True if notification sent successfully
        """
        if not self.enabled:
            return False
        
        message = self._format_trade_message(trade, alert_type)
        
        success = True
        
        # Console notification
        self._log_notification(message)
        
        # Webhook notification
        if self.webhook_url:
            success = success and self._send_webhook(message, trade)
        
        # Email notification
        if self.email_enabled:
            success = success and self._send_email(
                subject=f"💰 Trade {alert_type} Alert",
                body=message
            )
        
        return success
    
    def send_error_alert(self, error_msg: str, context: Optional[Dict] = None) -> bool:
        """
        Send alert for errors or exceptions.
        
        Args:
            error_msg: Error message
            context: Additional context information
            
        Returns:
            True if notification sent successfully
        """
        if not self.enabled:
            return False
        
        message = f"⚠️ ERROR ALERT\n\n{error_msg}"
        
        if context:
            message += f"\n\nContext:\n{json.dumps(context, indent=2)}"
        
        message += f"\n\nTime: {datetime.now().isoformat()}"
        
        success = True
        
        # Console notification
        self._log_notification(message, level="ERROR")
        
        # Email notification (for errors, prioritize email)
        if self.email_enabled:
            success = success and self._send_email(
                subject="⚠️ ICT Agent Error Alert",
                body=message
            )
        
        return success
    
    def send_daily_summary(self, summary: Dict) -> bool:
        """
        Send daily performance summary.
        
        Args:
            summary: Summary dictionary with performance metrics
            
        Returns:
            True if notification sent successfully
        """
        if not self.enabled:
            return False
        
        message = self._format_summary_message(summary)
        
        success = True
        
        # Console notification
        self._log_notification(message)
        
        # Email notification
        if self.email_enabled:
            success = success and self._send_email(
                subject="📊 ICT Agent Daily Summary",
                body=message
            )
        
        return success
    
    def _format_signal_message(self, signal: Dict) -> str:
        """Format a trading signal into a readable message."""
        emoji = "🟢" if signal.get('direction') == 'LONG' or signal.get('direction') == 'BULLISH' else "🔴"
        
        message = f"""
{emoji} NEW TRADING SIGNAL DETECTED {emoji}

Pattern: {signal.get('pattern', 'N/A')}
Direction: {signal.get('direction', 'N/A')}
Strength: {signal.get('strength', 0):.2%}

Entry Price: ${signal.get('price', 0):.2f}
Stop Loss: ${signal.get('stop_loss', 0):.2f}
Take Profit: ${signal.get('take_profit', 0):.2f}

Risk/Reward: {self._calculate_risk_reward(signal):.2f}
Timestamp: {signal.get('timestamp', datetime.now().isoformat())}
"""
        return message.strip()
    
    def _format_trade_message(self, trade: Dict, alert_type: str) -> str:
        """Format a trade execution into a readable message."""
        emoji_map = {
            'ENTRY': '📈',
            'EXIT': '💰',
            'STOP_LOSS': '🛑',
            'TAKE_PROFIT': '✅'
        }
        
        emoji = emoji_map.get(alert_type, '📊')
        
        message = f"""
{emoji} TRADE {alert_type} {emoji}

Direction: {trade.get('direction', 'N/A')}
Entry Price: ${trade.get('entry_price', 0):.2f}
"""
        
        if alert_type in ['EXIT', 'STOP_LOSS', 'TAKE_PROFIT']:
            pnl = trade.get('pnl', 0)
            pnl_emoji = "✅" if pnl > 0 else "❌"
            message += f"""
Exit Price: ${trade.get('exit_price', 0):.2f}
P&L: ${pnl:.2f} {pnl_emoji}
Exit Reason: {trade.get('exit_reason', 'N/A')}
"""
        
        message += f"\nTimestamp: {datetime.now().isoformat()}"
        
        return message.strip()
    
    def _format_summary_message(self, summary: Dict) -> str:
        """Format a daily summary into a readable message."""
        message = f"""
📊 DAILY PERFORMANCE SUMMARY

Date: {summary.get('date', datetime.now().date())}

PERFORMANCE:
  Total Trades: {summary.get('total_trades', 0)}
  Winning Trades: {summary.get('winning_trades', 0)}
  Losing Trades: {summary.get('losing_trades', 0)}
  Win Rate: {summary.get('win_rate', 0):.2%}

PROFIT & LOSS:
  Total P&L: ${summary.get('total_pnl', 0):.2f}
  Average Win: ${summary.get('avg_win', 0):.2f}
  Average Loss: ${summary.get('avg_loss', 0):.2f}

ACCOUNT:
  Starting Balance: ${summary.get('starting_balance', 0):.2f}
  Ending Balance: ${summary.get('ending_balance', 0):.2f}
  Daily Return: {summary.get('daily_return', 0):.2%}
"""
        return message.strip()
    
    def _send_webhook(self, message: str, data: Dict) -> bool:
        """
        Send notification via webhook (Discord, Slack, etc.).
        
        Args:
            message: Formatted message
            data: Additional data
            
        Returns:
            True if successful
        """
        if not self.webhook_url:
            return False
        
        try:
            # Format for Discord webhook
            payload = {
                "content": message,
                "embeds": [{
                    "title": "ICT Trading Agent Alert",
                    "description": message[:2000],  # Discord limit
                    "color": 3447003,  # Blue color
                    "timestamp": datetime.now().isoformat()
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 204 or response.status_code == 200:
                self.logger.info("Webhook notification sent successfully")
                return True
            else:
                self.logger.error(f"Webhook failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Webhook notification failed: {e}")
            return False
    
    def _send_email(self, subject: str, body: str) -> bool:
        """
        Send notification via email.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            True if successful
        """
        if not self.email_enabled or not all([self.smtp_server, self.email_from, 
                                              self.email_to, self.email_password]):
            self.logger.warning("Email notification not configured properly")
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_server, 587)
            server.starttls()
            server.login(self.email_from, self.email_password)
            
            # Send email
            server.send_message(msg)
            server.quit()
            
            self.logger.info(f"Email notification sent to {self.email_to}")
            return True
            
        except Exception as e:
            self.logger.error(f"Email notification failed: {e}")
            return False
    
    def _log_notification(self, message: str, level: str = "INFO") -> None:
        """
        Log notification to console.
        
        Args:
            message: Message to log
            level: Log level
        """
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        # Also print to console
        print(f"\n{'='*70}")
        print(message)
        print(f"{'='*70}\n")
    
    def _calculate_risk_reward(self, signal: Dict) -> float:
        """
        Calculate risk/reward ratio for a signal.
        
        Args:
            signal: Trading signal
            
        Returns:
            Risk/reward ratio
        """
        entry = signal.get('price', 0)
        stop = signal.get('stop_loss', 0)
        target = signal.get('take_profit', 0)
        
        if entry == 0 or stop == 0:
            return 0.0
        
        risk = abs(entry - stop)
        reward = abs(target - entry)
        
        if risk == 0:
            return 0.0
        
        return reward / risk
