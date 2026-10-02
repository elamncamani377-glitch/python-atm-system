# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 22:07:34 2026

@author: HP
"""

import csv
import os
import random
import string
from datetime import datetime
from account import Account


class ATMSystem:
    """Manages storage, user auth, account creation, EFT, and logging."""

    def __init__(
        self,
        accounts_file="account_balances.txt",
        transactions_file="transactions.txt",
        log_file="log.txt"
    ):
        """Initialize file references, active accounts, and lockout tracker."""
        self.accounts_file = accounts_file
        self.transactions_file = transactions_file
        self.log_file = log_file
        self.accounts = {}
        self.failed_attempts = {}
        self._ensure_files_exist()
        self.load_accounts()

    def _ensure_files_exist(self):
        """Ensure all required data files exist with CSV headers."""
        if not os.path.exists(self.accounts_file):
            with open(
                self.accounts_file, "w", newline="", encoding="utf-8"
            ) as f:
                writer = csv.writer(f)
                writer.writerow([
                    "account_number",
                    "phone_number",
                    "pin_hash",
                    "balance"
                ])

        if not os.path.exists(self.transactions_file):
            with open(
                self.transactions_file, "w", newline="", encoding="utf-8"
            ) as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "phone_number",
                    "type",
                    "amount",
                    "resulting_balance"
                ])

        if not os.path.exists(self.log_file):
            open(self.log_file, "a", encoding="utf-8").close()

    def load_accounts(self):
        """Load account details from account_balances.txt into memory."""
        self.accounts = {}
        if not os.path.exists(self.accounts_file):
            return

        with open(self.accounts_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                acc = Account(
                    account_number=row["account_number"],
                    phone_number=row["phone_number"],
                    pin_hash=row["pin_hash"],
                    balance=float(row["balance"])
                )
                self.accounts[acc.phone_number] = acc

    def save_accounts(self):
        """Persist current memory state of all accounts to file."""
        with open(
            self.accounts_file, "w", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow([
                "account_number",
                "phone_number",
                "pin_hash",
                "balance"
            ])
            for acc in self.accounts.values():
                writer.writerow([
                    acc.account_number,
                    acc.phone_number,
                    acc.pin_hash,
                    f"{acc.balance:.2f}"
                ])

    def write_log(self, phone_number, event_type):
        """Record system events and security operations with timestamps."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, phone_number, event_type])

    def record_transaction(self, phone_number, tx_type, amount, balance):
        """Record completed user transaction into transactions.txt."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(
            self.transactions_file, "a", newline="", encoding="utf-8"
        ) as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                phone_number,
                tx_type,
                f"{amount:+.2f}",
                f"Balance: R{balance:.2f}"
            ])

    def generate_unique_account_number(self):
        """Generate a unique 8-digit account number."""
        existing_numbers = {
            acc.account_number for acc in self.accounts.values()
        }
        while True:
            acc_num = "".join(random.choices(string.digits, k=8))
            if acc_num not in existing_numbers:
                return acc_num

    def register(self, phone_number, pin, confirm_pin):
        """Validate input criteria and create a new customer account."""
        if not (phone_number.isdigit() and len(phone_number) == 10):
            return False, "Phone number must be exactly 10 digits."

        if phone_number in self.accounts:
            return False, "Phone number is already associated with an account."

        if pin != confirm_pin:
            return False, "PIN entries do not match."

        if not (pin.isdigit() and len(pin) in (4, 5)):
            return False, "PIN must be either 4 or 5 numeric digits."

        acc_num = self.generate_unique_account_number()
        pin_hash = Account.hash_pin(pin)
        new_account = Account(acc_num, phone_number, pin_hash, 0.0)

        self.accounts[phone_number] = new_account
        self.save_accounts()
        self.write_log(phone_number, "REGISTERED")
        return True, f"Registration successful.\nYour Account Number: {acc_num}"

    def login(self, phone_number, pin):
        """Authenticate user login and manage failed attempt lockouts."""
        if self.failed_attempts.get(phone_number, 0) >= 3:
            return None, "Account locked due to 3 consecutive failed logins."

        acc = self.accounts.get(phone_number)
        if not acc:
            self.write_log(phone_number, "LOGIN_FAILED")
            return None, "Invalid phone number or PIN."

        if acc.verify_pin(pin):
            self.failed_attempts[phone_number] = 0
            self.write_log(phone_number, "LOGIN_SUCCESS")
            return acc, "Login successful. Welcome back."

        self.failed_attempts[phone_number] = (
            self.failed_attempts.get(phone_number, 0) + 1
        )
        self.write_log(phone_number, "LOGIN_FAILED")

        if self.failed_attempts[phone_number] >= 3:
            return None, "Account locked due to 3 failed login attempts."

        remaining = 3 - self.failed_attempts[phone_number]
        return None, f"Invalid PIN. Remaining attempts: {remaining}"

    def transfer(self, sender_acc, target_acc_num, amount):
        """Execute Electronic Funds Transfer (EFT) between two accounts."""
        if not (target_acc_num.isdigit() and len(target_acc_num) == 8):
            return False, "Invalid account number format. Must be 8 digits."

        if sender_acc.account_number == target_acc_num:
            return False, "You cannot transfer money to your own account."

        target_acc = None
        for acc in self.accounts.values():
            if acc.account_number == target_acc_num:
                target_acc = acc
                break

        if not target_acc:
            return False, "Target account number does not exist."

        if amount <= 0:
            return False, "Transfer amount must be greater than zero."

        if sender_acc.balance < amount:
            return False, "Insufficient funds for transfer."

        sender_acc.balance -= amount
        target_acc.balance += amount

        self.save_accounts()
        self.record_transaction(
            sender_acc.phone_number, "EFT OUT", -amount, sender_acc.balance
        )
        self.record_transaction(
            target_acc.phone_number, "EFT IN", amount, target_acc.balance
        )
        return True, f"Transferred R{amount:.2f} to Account {target_acc_num}."

    def get_statement(self, phone_number):
        """Retrieve historical transaction lines for the target account."""
        statements = []
        if not os.path.exists(self.transactions_file):
            return statements

        with open(self.transactions_file, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for row in reader:
                if len(row) >= 5 and row[1] == phone_number:
                    statements.append(
                        f"{row[0]} | {row[2]:<10} | {row[3]:>10} | {row[4]}"
                    )
        return statements