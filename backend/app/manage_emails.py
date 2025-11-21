#!/usr/bin/env python3
"""
Script to manage email recipients in the database
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.repository import Repository


def add_email(email: str, name: str = None):
    """Add a new email recipient"""
    repo = Repository()
    result = repo.create_email(email, name)
    if result:
        print(f"✓ Added email: {email}" + (f" ({name})" if name else ""))
    else:
        print(f"✗ Email already exists: {email}")


def list_emails():
    """List all email recipients"""
    repo = Repository()
    emails = repo.get_all_emails(active_only=False)
    
    if not emails:
        print("No email recipients found")
        return
    
    print(f"\nTotal recipients: {len(emails)}\n")
    print(f"{'Email':<40} {'Name':<20} {'Status':<10} {'Created'}")
    print("-" * 90)
    
    for email in emails:
        status = "Active" if email.is_active == "true" else "Inactive"
        name = email.name or "-"
        created = email.created_at.strftime("%Y-%m-%d %H:%M")
        print(f"{email.email:<40} {name:<20} {status:<10} {created}")


def activate_email(email: str):
    """Activate an email recipient"""
    repo = Repository()
    if repo.update_email_status(email, True):
        print(f"✓ Activated: {email}")
    else:
        print(f"✗ Email not found: {email}")


def deactivate_email(email: str):
    """Deactivate an email recipient"""
    repo = Repository()
    if repo.update_email_status(email, False):
        print(f"✓ Deactivated: {email}")
    else:
        print(f"✗ Email not found: {email}")


def delete_email(email: str):
    """Delete an email recipient"""
    repo = Repository()
    if repo.delete_email(email):
        print(f"✓ Deleted: {email}")
    else:
        print(f"✗ Email not found: {email}")


def show_help():
    """Show help message"""
    print("""
Email Management Script

Usage:
    python app/manage_emails.py <command> [arguments]

Commands:
    add <email> [name]     Add a new email recipient
    list                   List all email recipients
    activate <email>       Activate an email recipient
    deactivate <email>     Deactivate an email recipient
    delete <email>         Delete an email recipient
    help                   Show this help message

Examples:
    python app/manage_emails.py add john@example.com "John Doe"
    python app/manage_emails.py list
    python app/manage_emails.py activate john@example.com
    python app/manage_emails.py deactivate john@example.com
    python app/manage_emails.py delete john@example.com
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) < 3:
            print("Error: Email address required")
            print("Usage: python app/manage_emails.py add <email> [name]")
            sys.exit(1)
        email = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else None
        add_email(email, name)
    
    elif command == "list":
        list_emails()
    
    elif command == "activate":
        if len(sys.argv) < 3:
            print("Error: Email address required")
            print("Usage: python app/manage_emails.py activate <email>")
            sys.exit(1)
        activate_email(sys.argv[2])
    
    elif command == "deactivate":
        if len(sys.argv) < 3:
            print("Error: Email address required")
            print("Usage: python app/manage_emails.py deactivate <email>")
            sys.exit(1)
        deactivate_email(sys.argv[2])
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("Error: Email address required")
            print("Usage: python app/manage_emails.py delete <email>")
            sys.exit(1)
        delete_email(sys.argv[2])
    
    elif command == "help":
        show_help()
    
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)
