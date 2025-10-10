#!/usr/bin/env python
"""
Setup script for Wax and Warmth Django backend
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("=== Wax and Warmth Django Backend Setup ===\n")
    
    # Check if we're in the right directory
    if not os.path.exists('manage.py'):
        print("Error: Please run this script from the backend directory (where manage.py is located)")
        sys.exit(1)
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("Please ensure you have pip installed and try again.")
        sys.exit(1)
    
    # Make migrations
    if not run_command("python manage.py makemigrations", "Creating database migrations"):
        sys.exit(1)
    
    # Apply migrations
    if not run_command("python manage.py migrate", "Applying database migrations"):
        sys.exit(1)
    
    # Create superuser prompt
    print("\n" + "="*50)
    print("Setup completed successfully!")
    print("="*50)
    
    create_superuser = input("\nWould you like to create an admin user? (y/n): ").lower().strip()
    if create_superuser in ['y', 'yes']:
        print("\nCreating admin user...")
        os.system("python manage.py createsuperuser")
    
    print("\n" + "="*50)
    print("NEXT STEPS:")
    print("="*50)
    print("1. Run the development server:")
    print("   python manage.py runserver")
    print("")
    print("2. Access your website at: http://127.0.0.1:8000/")
    print("")
    if create_superuser in ['y', 'yes']:
        print("3. Access admin panel at: http://127.0.0.1:8000/admin/")
        print("")
    print("4. Test newsletter subscription on your website")
    print("")
    print("Your Django backend is ready! 🎉")

if __name__ == "__main__":
    main()