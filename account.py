# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 22:06:58 2026

@author: HP
"""

import hashlib


class Account:
    """Represents a customer bank account in the PyBank ATM system."""

    def __init__(self, account_number, phone_number, pin_hash, balance=0.0):
        """Initialize account credentials and current balance."""
        self.account_number = str(account_number)
        self.phone_number = str(phone_number)
        self.pin_hash = str(pin_hash)
        self.balance = float(balance)

    @staticmethod
    def hash_pin(pin):
        """
        Hash a raw PIN using SHA-256.

        Choice of Algorithm: SHA-256 from hashlib is selected because it is a
        cryptographically secure one-way hash function. It prevents raw PINs
        from being recovered if data storage files are exposed.
        """
        return hashlib.sha256(pin.encode("utf-8")).hexdigest()

    def verify_pin(self, pin_input):
        """Verify provided input PIN against the stored SHA-256 hash."""
        return self.hash_pin(pin_input) == self.pin_hash

    def deposit(self, amount):
        """Deposit a positive monetary amount into the account."""
        if amount <= 0:
            return False
        self.balance += amount
        return True

    def withdraw(self, amount):
        """Withdraw requested funds if sufficient balance is available."""
        if amount <= 0 or amount > self.balance:
            return False
        self.balance -= amount
        return True