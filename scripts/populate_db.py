# reconmaster/scripts/populate_db.py

import sys
import os

# This is a bit of a hack to make the script able to import from the 'app' directory
# It adds the parent directory of 'scripts' (which is the project root) to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal, engine
from app.db.models import Tool, Base

def populate_db():
    """
    Populates the database with an initial set of reconnaissance tools.
    """
    # Create all tables in the database (idempotent operation)
    Base.metadata.create_all(bind=engine)

    # Get a new database session
    db = SessionLocal()

    try:
        # Check if tools already exist to avoid duplicates
        if db.query(Tool).count() > 0:
            print("Database already contains tools. Skipping population.")
            return

        print("Populating database with initial tools...")

        # Define the tools to add
        tools_to_add = [
            Tool(
                name="Nmap",
                category="Network Scanner",
                description="A powerful tool for network discovery and security auditing. It uses IP packets to determine what hosts are available on the network, what services those hosts are offering, what operating systems they are running, etc.",
                base_command="nmap",
                advantages="Extremely versatile, huge number of scanning options, scriptable engine (NSE).",
                example_usage="nmap -sV -T4 example.com"
            ),
            Tool(
                name="Gobuster",
                category="Web Content Discovery",
                description="A tool used to brute-force URIs (directories and files), DNS subdomains, and virtual host names on web servers.",
                base_command="gobuster dir",
                advantages="Very fast, simple to use, supports multiple modes (dir, dns, vhost).",
                example_usage="gobuster dir -u http://example.com -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
            ),
            Tool(
                name="Sublist3r",
                category="Subdomain Enumeration",
                description="A Python tool designed to enumerate subdomains of websites using OSINT. It helps penetration testers and bug hunters collect and gather subdomains for the domain they are targeting.",
                base_command="sublist3r",
                advantages="Aggregates results from many search engines (Google, Yahoo, Bing) and services like VirusTotal and Netcraft.",
                example_usage="sublist3r -d example.com"
            ),
            Tool(
                name="WhatWeb",
                category="Website Fingerprinting",
                description="Identifies websites. Its goal is to answer the question, 'What is that website?'. It recognizes web technologies including content management systems (CMS), blogging platforms, analytic packages, JavaScript libraries, and web servers.",
                base_command="whatweb",
                advantages="Highly detailed output, plugin-based architecture, adjustable aggression levels.",
                example_usage="whatweb example.com"
            )
        ]

        # Add all the tools to the session and commit them to the database
        db.add_all(tools_to_add)
        db.commit()

        print("Database successfully populated!")

    finally:
        # Always close the session
        db.close()

if __name__ == "__main__":
    populate_db()
