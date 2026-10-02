# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 22:09:21 2026

@author: HP
"""

from transaction import ATMSystem


def active_user_menu(account, system):
    """Display and manage interactive menu options for logged-in user."""
    while True:
        print("\n--- Main Menu ---")
        print("1. Withdraw")
        print("2. Deposit")
        print("3. Transfer (EFT)")
        print("4. View Statement")
        print("5. Logout")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            try:
                amt = float(input("Enter withdrawal amount: R"))
                if account.withdraw(amt):
                    system.save_accounts()
                    system.record_transaction(
                        account.phone_number,
                        "WITHDRAW",
                        -amt,
                        account.balance
                    )
                    print(f"Withdrawal successful.")
                    print(f"Your new balance: R{account.balance:.2f}")
                else:
                    print("Transaction failed: Insufficient balance or invalid amount.")
            except ValueError:
                print("Invalid input. Enter numeric values only.")

        elif choice == "2":
            try:
                amt = float(input("Enter deposit amount: R"))
                if account.deposit(amt):
                    system.save_accounts()
                    system.record_transaction(
                        account.phone_number,
                        "DEPOSIT",
                        amt,
                        account.balance
                    )
                    print(f"Deposit successful.")
                    print(f"Your new balance: R{account.balance:.2f}")
                else:
                    print("Transaction failed: Amount must be greater than zero.")
            except ValueError:
                print("Invalid input. Enter numeric values only.")

        elif choice == "3":
            target_acc = input("Enter destination account number: ").strip()
            try:
                amt = float(input("Enter transfer amount: R"))
                success, msg = system.transfer(account, target_acc, amt)
                print(msg)
                if success:
                    print(f"Your new balance: R{account.balance:.2f}")
            except ValueError:
                print("Invalid input. Enter numeric values only.")

        elif choice == "4":
            print("\n--- Statement ---")
            records = system.get_statement(account.phone_number)
            if records:
                for line in records:
                    print(line)
            else:
                print("No transactions found.")

        elif choice == "5":
            print("\nLogged out. Stay safe.")
            break

        else:
            print("Invalid selection. Please try again.")


def main():
    """Main program loop serving starting menu options."""
    system = ATMSystem()

    while True:
        print("\n===============================")
        print("      Welcome to PyBank ATM    ")
        print("===============================")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            print("\n--- Account Registration ---")
            phone = input("Enter your phone number (10 digits): ").strip()
            pin = input("Create a PIN (4-5 digits): ").strip()
            confirm_pin = input("Confirm PIN: ").strip()

            success, msg = system.register(phone, pin, confirm_pin)
            print(f"\n{msg}")

        elif choice == "2":
            print("\n--- Login ---")
            phone = input("Phone number: ").strip()
            pin = input("PIN: ").strip()

            account, msg = system.login(phone, pin)
            print(f"\n{msg}")

            if account:
                active_user_menu(account, system)

        elif choice == "3":
            print("\nThank you for using PyBank ATM. Goodbye!")
            break

        else:
            print("Invalid option. Please choose 1, 2, or 3.")


if __name__ == "__main__":
    main()
    